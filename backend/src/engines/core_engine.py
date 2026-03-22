from __future__ import annotations

import asyncio
import time
from typing import Any, AsyncIterator

from main import run_workflow
from backend.src.engines.base import RAGEngine
from backend.src.schemas.events import (
    AnswerReplacedEvent,
    DocumentsRetrievedEvent,
    GradingCompletedEvent,
    HallucinationResult,
    QueryRewrittenEvent,
    RetrievedDoc,
    RunCompletedEvent,
    RunFailedEvent,
    RunStartedEvent,
    ServerEvent,
    StepChangedEvent,
)


def _doc_to_event(index: int, doc: Any) -> RetrievedDoc:
    metadata = getattr(doc, "metadata", {}) or {}
    source = str(metadata.get("source") or metadata.get("title") or f"Document {index}")
    snippet = str(getattr(doc, "page_content", "")).strip()
    return RetrievedDoc(
        id=str(metadata.get("id") or index),
        source=source,
        snippet=snippet,
        relevant=True,
    )


class CoreRAGEngine(RAGEngine):
    async def run(self, query: str) -> AsyncIterator[ServerEvent]: # type: ignore
        run_id = f"run-{int(time.time() * 1000)}"
        yield RunStartedEvent(runId=run_id, query=query)

        final_state = await asyncio.to_thread(run_workflow, query)
        error_message = final_state.get("error_message")
        if error_message:
            yield RunFailedEvent(error=error_message)
            return

        yield StepChangedEvent(step="rewriting")
        rewritten_query = final_state.get("rewritten_query", "")
        yield QueryRewrittenEvent(rewrittenQuery=rewritten_query)

        yield StepChangedEvent(step="retrieval")
        retrieved_docs = [
            _doc_to_event(index + 1, doc)
            for index, doc in enumerate(final_state.get("retrieved_docs", []))
        ]
        yield DocumentsRetrievedEvent(retrievedDocs=retrieved_docs)

        yield StepChangedEvent(step="generation")
        answer = final_state.get("answer", "")
        yield AnswerReplacedEvent(answer=answer)

        yield StepChangedEvent(step="grading")
        score = float(final_state.get("hallucination_score", 0.0))
        yield GradingCompletedEvent(
            hallucinationResult=HallucinationResult(
                score=score,
                explanation=(
                    "Evaluation derived from the current RAG workflow output. "
                    "Backend core integration does not yet expose unsupported claims."
                ),
            )
        )
        yield RunCompletedEvent()
