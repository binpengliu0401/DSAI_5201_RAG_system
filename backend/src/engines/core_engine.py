from __future__ import annotations
import re
import time
from typing import Any, AsyncIterator

from app.graph.builder import rag_graph
from app.utils.constants import HALLUCINATION_THRESHOLD, MAX_RETRIES
from config.logging import get_logger
from backend.src.engines.base import RAGEngine
from backend.src.schemas.events import (
    AnswerDeltaEvent,
    AnswerCompletedEvent,
    AnswerReplacedEvent,
    AttemptStartedEvent,
    AttemptCompletedEvent,
    AttemptReworkTriggeredEvent,
    DocumentsRetrievedEvent,
    GradingCompletedEvent,
    HallucinationResult,
    QueryRewrittenEvent,
    RetrievedDoc,
    RunCompletedEvent,
    RunFailedEvent,
    RunStartedEvent,
    ServerEvent,
    StageCompletedEvent,
    StageStartedEvent,
    StepChangedEvent,
)

logger = get_logger(__name__)


def _doc_to_event(index: int, doc: Any) -> RetrievedDoc:
    metadata = getattr(doc, "metadata", {}) or {}
    title = str(metadata.get("title") or metadata.get("source") or f"Document {index}")
    source = str(metadata.get("source") or title)
    snippet = _build_snippet_preview(str(getattr(doc, "page_content", "")).strip())
    score = _extract_score(metadata)
    return RetrievedDoc(
        id=str(metadata.get("id") or index),
        title=title,
        source=source,
        snippet=snippet,
        score=score,
        relevant=True,
    )


class CoreRAGEngine(RAGEngine):
    async def run(self, query: str) -> AsyncIterator[ServerEvent]:  # type: ignore
        run_id = f"run-{int(time.time() * 1000)}"
        yield RunStartedEvent(runId=run_id, query=query)
        current_attempt = 0

        initial_state = {
            "query": query,
            "rewritten_query": "",
            "failed_queries": [],
            "retrieved_docs": [],
            "answer": "",
            "hallucination_score": 0.0,
            "retry_count": 0,
            "max_retries": MAX_RETRIES,
            "final_decision": "",
            "error_message": None,
            "execution_trace": [],
        }

        final_state = {}

        try:
            async for chunk in rag_graph.astream(initial_state): # type: ignore
                node_name = list(chunk.keys())[0]
                node_output = chunk[node_name]
                final_state.update(node_output)

                if node_name == "rewriting":
                    current_attempt += 1
                    yield AttemptStartedEvent(attempt=current_attempt)
                    yield StageStartedEvent(attempt=current_attempt, stage="rewriting")
                    yield StepChangedEvent(step="rewriting", attempt=current_attempt)
                    yield QueryRewrittenEvent(
                        attempt=current_attempt,
                        rewrittenQuery=node_output.get("rewritten_query", "")
                    )
                    yield StageCompletedEvent(attempt=current_attempt, stage="rewriting")
                    yield StageStartedEvent(attempt=current_attempt, stage="retrieval")

                elif node_name == "retrieval":
                    yield StepChangedEvent(step="retrieval", attempt=current_attempt)
                    docs = [
                        _doc_to_event(i + 1, doc)
                        for i, doc in enumerate(node_output.get("retrieved_docs", []))
                    ]
                    logger.info("Prepared %d sources for UI on attempt %d", len(docs), current_attempt)
                    yield DocumentsRetrievedEvent(attempt=current_attempt, retrievedDocs=docs)
                    yield StageCompletedEvent(attempt=current_attempt, stage="retrieval")
                    yield StageStartedEvent(attempt=current_attempt, stage="generation")
                    yield StepChangedEvent(step="generation", attempt=current_attempt)

                elif node_name == "generation":
                    answer = str(node_output.get("answer", "") or "")
                    if not answer:
                        yield AnswerReplacedEvent(attempt=current_attempt, answer="")
                    else:
                        for chunk_text in _chunk_answer(answer):
                            yield AnswerDeltaEvent(attempt=current_attempt, delta=chunk_text)
                    yield AnswerCompletedEvent(attempt=current_attempt)
                    yield StageCompletedEvent(attempt=current_attempt, stage="generation")
                    yield StageStartedEvent(attempt=current_attempt, stage="grading")
                    yield StepChangedEvent(step="grading", attempt=current_attempt)

                elif node_name == "grading":
                    score = float(node_output.get("hallucination_score", 0.0))
                    grading_trace = _extract_trace_entry(node_output, "grading")
                    key_output = grading_trace.get("key_output", {})
                    verdict = str(key_output.get("verdict", "") or "")
                    claim_count = int(key_output.get("claim_count", 0) or 0)
                    unsupported_claim_count = int(
                        key_output.get("unsupported_claim_count", 0) or 0
                    )
                    yield GradingCompletedEvent(
                        attempt=current_attempt,
                        hallucinationResult=HallucinationResult(
                            score=score,
                            explanation=_build_grading_explanation(
                                score=score,
                                verdict=verdict,
                                claim_count=claim_count,
                                unsupported_claim_count=unsupported_claim_count,
                            ),
                        )
                    )
                    yield StageCompletedEvent(attempt=current_attempt, stage="grading")

                elif node_name == "router":
                    decision = str(node_output.get("final_decision", "") or "")
                    score = float(final_state.get("hallucination_score", 0.0) or 0.0)
                    if decision == "retry":
                        yield AttemptReworkTriggeredEvent(
                            attempt=current_attempt,
                            reason="low_confidence",
                            score=score,
                            threshold=HALLUCINATION_THRESHOLD,
                        )
                        yield AttemptCompletedEvent(attempt=current_attempt, outcome="reworked")
                    else:
                        yield AttemptCompletedEvent(attempt=current_attempt, outcome="completed")

        except Exception as e:
            yield RunFailedEvent(error=str(e))
            return

        error_message = final_state.get("error_message")
        if error_message:
            yield RunFailedEvent(error=error_message)
            return

        yield RunCompletedEvent()


def _chunk_answer(answer: str) -> list[str]:
    words = re.findall(r"\S+\s*", answer)
    chunk_size = 8
    return ["".join(words[index:index + chunk_size]) for index in range(0, len(words), chunk_size)]


def _build_snippet_preview(text: str, limit: int = 220) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def _extract_score(metadata: dict[str, Any]) -> float | None:
    for key in ("score", "retrieval_score", "similarity"):
        value = metadata.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return None


def _extract_trace_entry(node_output: dict[str, Any], node_name: str) -> dict[str, Any]:
    execution_trace = node_output.get("execution_trace", []) or []
    for entry in execution_trace:
        if entry.get("node") == node_name:
            return entry
    return {}


def _build_grading_explanation(
    *,
    score: float,
    verdict: str,
    claim_count: int,
    unsupported_claim_count: int,
) -> str:
    if verdict == "grounded":
        if claim_count > 0:
            return f"All {claim_count} checked claims are supported by the retrieved documents."
        return "The answer is fully supported by the retrieved documents."
    if verdict == "partially_grounded":
        if unsupported_claim_count > 0 and claim_count > 0:
            return (
                f"{unsupported_claim_count} of {claim_count} checked claims are unsupported "
                "or only partially supported by the retrieved documents."
            )
        return "Some parts of the answer are not fully supported by the retrieved documents."
    if verdict == "unsupported":
        if claim_count > 0:
            return (
                f"Most checked claims are not supported by the retrieved documents "
                f"(score {score:.2f})."
            )
        return "The answer is not supported by the retrieved documents."
    return f"Support analysis completed with score {score:.2f}."
