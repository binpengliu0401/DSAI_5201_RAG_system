from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator

from backend.src.engines.base import RAGEngine
from backend.src.schemas.events import (
    AttemptStartedEvent,
    AttemptCompletedEvent,
    AnswerDeltaEvent,
    AnswerCompletedEvent,
    DocumentsRetrievedEvent,
    GradingCompletedEvent,
    HallucinationResult,
    QueryRewrittenEvent,
    RetrievedDoc,
    RunCompletedEvent,
    RunStartedEvent,
    ServerEvent,
    StageCompletedEvent,
    StageStartedEvent,
    StepChangedEvent,
)


DEMO_ANSWER = (
    "Retrieval-Augmented Generation improves factual accuracy by grounding "
    "answers in retrieved sources. It also exposes source context to users "
    "and lets teams update knowledge without retraining the model."
)

DEMO_DOCS = [
    RetrievedDoc(
        id="1",
        title="RAG Overview",
        source="Doc 1, Page 3",
        snippet=(
            "Retrieval-Augmented Generation combines language models with "
            "external knowledge retrieval to improve accuracy."
        ),
        score=0.92,
        relevant=True,
    ),
    RetrievedDoc(
        id="2",
        title="Grounded Response Flow",
        source="Doc 2, Page 7",
        snippet=(
            "RAG systems retrieve relevant documents before generating "
            "responses, grounding the output in factual information."
        ),
        score=0.88,
        relevant=True,
    ),
    RetrievedDoc(
        id="3",
        title="Benefits of RAG",
        source="Doc 3, Page 12",
        snippet=(
            "Benefits include factual accuracy, source attribution, and "
            "knowledge updates without retraining."
        ),
        score=0.81,
        relevant=True,
    ),
    RetrievedDoc(
        id="4",
        title="Generic ML Workflow",
        source="Doc 4, Page 5",
        snippet="This document discusses generic machine learning workflows.",
        score=0.27,
        relevant=False,
    ),
]


def chunk_answer(answer: str) -> list[str]:
    return answer.split(" ")


class FakeRAGEngine(RAGEngine):
    def __init__(self, step_delay_ms: int = 250) -> None:
        self.step_delay_s = max(step_delay_ms, 0) / 1000

    async def run(self, query: str) -> AsyncIterator[ServerEvent]:
        run_id = f"demo-{int(time.time() * 1000)}"
        attempt = 1
        yield RunStartedEvent(runId=run_id, query=query)
        yield AttemptStartedEvent(attempt=attempt)
        yield StageStartedEvent(attempt=attempt, stage="rewriting")

        yield StepChangedEvent(step="rewriting", attempt=attempt)
        await asyncio.sleep(self.step_delay_s)
        yield QueryRewrittenEvent(
            attempt=attempt,
            rewrittenQuery=f"Enhanced query: {query} (with context and specificity)"
        )
        yield StageCompletedEvent(attempt=attempt, stage="rewriting")
        yield StageStartedEvent(attempt=attempt, stage="retrieval")

        yield StepChangedEvent(step="retrieval", attempt=attempt)
        await asyncio.sleep(self.step_delay_s)
        yield DocumentsRetrievedEvent(attempt=attempt, retrievedDocs=DEMO_DOCS)
        yield StageCompletedEvent(attempt=attempt, stage="retrieval")
        yield StageStartedEvent(attempt=attempt, stage="generation")
        yield StepChangedEvent(step="generation", attempt=attempt)

        await asyncio.sleep(self.step_delay_s)
        for token in chunk_answer(DEMO_ANSWER):
            yield AnswerDeltaEvent(attempt=attempt, delta=f"{token} ")
            await asyncio.sleep(min(self.step_delay_s / 4, 0.08))
        yield AnswerCompletedEvent(attempt=attempt)
        yield StageCompletedEvent(attempt=attempt, stage="generation")
        yield StageStartedEvent(attempt=attempt, stage="grading")
        yield StepChangedEvent(step="grading", attempt=attempt)

        await asyncio.sleep(self.step_delay_s)
        yield GradingCompletedEvent(
            attempt=attempt,
            hallucinationResult=HallucinationResult(
                score=0.85,
                explanation=(
                    "All major claims in the answer are supported by the "
                    "retrieved documents surfaced in the trace."
                ),
            )
        )
        yield StageCompletedEvent(attempt=attempt, stage="grading")
        yield AttemptCompletedEvent(attempt=attempt, outcome="completed")
        yield RunCompletedEvent()
