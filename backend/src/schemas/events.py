from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


ProcessingStep = Literal["rewriting", "retrieval", "generation", "grading", "complete"]
RunStatus = Literal["idle", "running", "complete", "error"]


class RetrievedDoc(BaseModel):
    id: str
    source: str
    snippet: str
    relevant: bool = True


class HallucinationResult(BaseModel):
    score: float
    explanation: str
    unsupportedClaims: list[str] = Field(default_factory=list)


class SessionSnapshot(BaseModel):
    runId: Optional[str] = None
    query: str = ""
    runStatus: RunStatus = "idle"
    currentStep: Optional[ProcessingStep] = None
    rewrittenQuery: str = ""
    retrievedDocs: list[RetrievedDoc] = Field(default_factory=list)
    answer: str = ""
    hallucinationResult: Optional[HallucinationResult] = None
    error: Optional[str] = None


class RunStartedEvent(BaseModel):
    type: Literal["run_started"] = "run_started"
    runId: Optional[str] = None
    query: str


class StepChangedEvent(BaseModel):
    type: Literal["step_changed"] = "step_changed"
    step: ProcessingStep


class QueryRewrittenEvent(BaseModel):
    type: Literal["query_rewritten"] = "query_rewritten"
    rewrittenQuery: str


class DocumentsRetrievedEvent(BaseModel):
    type: Literal["documents_retrieved"] = "documents_retrieved"
    retrievedDocs: list[RetrievedDoc]


class AnswerDeltaEvent(BaseModel):
    type: Literal["answer_delta"] = "answer_delta"
    delta: str


class AnswerReplacedEvent(BaseModel):
    type: Literal["answer_replaced"] = "answer_replaced"
    answer: str


class GradingCompletedEvent(BaseModel):
    type: Literal["grading_completed"] = "grading_completed"
    hallucinationResult: HallucinationResult


class RunCompletedEvent(BaseModel):
    type: Literal["run_completed"] = "run_completed"


class RunFailedEvent(BaseModel):
    type: Literal["run_failed"] = "run_failed"
    error: str


class SnapshotEvent(BaseModel):
    type: Literal["snapshot"] = "snapshot"
    snapshot: SessionSnapshot


ServerEvent = Union[
    RunStartedEvent,
    StepChangedEvent,
    QueryRewrittenEvent,
    DocumentsRetrievedEvent,
    AnswerDeltaEvent,
    AnswerReplacedEvent,
    GradingCompletedEvent,
    RunCompletedEvent,
    RunFailedEvent,
    SnapshotEvent,
]
