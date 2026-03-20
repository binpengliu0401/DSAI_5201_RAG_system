from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator

from backend.src.engines.base import RAGEngine
from backend.src.schemas.events import (
    AnswerDeltaEvent,
    DocumentsRetrievedEvent,
    GradingCompletedEvent,
    HallucinationResult,
    QueryRewrittenEvent,
    RetrievedDoc,
    RunCompletedEvent,
    RunStartedEvent,
    ServerEvent,
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
        source="Doc 1, Page 3",
        snippet=(
            "Retrieval-Augmented Generation combines language models with "
            "external knowledge retrieval to improve accuracy."
        ),
        relevant=True,
    ),
    RetrievedDoc(
        id="2",
        source="Doc 2, Page 7",
        snippet=(
            "RAG systems retrieve relevant documents before generating "
            "responses, grounding the output in factual information."
        ),
        relevant=True,
    ),
    RetrievedDoc(
        id="3",
        source="Doc 3, Page 12",
        snippet=(
            "Benefits include factual accuracy, source attribution, and "
            "knowledge updates without retraining."
        ),
        relevant=True,
    ),
    RetrievedDoc(
        id="4",
        source="Doc 4, Page 5",
        snippet="This document discusses generic machine learning workflows.",
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
        yield RunStartedEvent(runId=run_id, query=query)

        yield StepChangedEvent(step="rewriting")
        await asyncio.sleep(self.step_delay_s)
        yield QueryRewrittenEvent(
            rewrittenQuery=f"Enhanced query: {query} (with context and specificity)"
        )

        yield StepChangedEvent(step="retrieval")
        await asyncio.sleep(self.step_delay_s)
        yield DocumentsRetrievedEvent(retrievedDocs=DEMO_DOCS)

        yield StepChangedEvent(step="generation")
        await asyncio.sleep(self.step_delay_s)
        for token in chunk_answer(DEMO_ANSWER):
            yield AnswerDeltaEvent(delta=f"{token} ")
            await asyncio.sleep(min(self.step_delay_s / 4, 0.08))

        yield StepChangedEvent(step="grading")
        await asyncio.sleep(self.step_delay_s)
        yield GradingCompletedEvent(
            hallucinationResult=HallucinationResult(
                score=0.85,
                explanation=(
                    "All major claims in the answer are supported by the "
                    "retrieved documents surfaced in the trace."
                ),
            )
        )
        yield RunCompletedEvent()
