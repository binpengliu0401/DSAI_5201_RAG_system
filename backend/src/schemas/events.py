from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


ProcessingStep = Literal["rewriting", "retrieval", "generation", "grading", "complete"]
PipelineStage = Literal["rewriting", "retrieval", "generation", "grading"]
RunStatus = Literal["idle", "running", "complete", "error"]


class RetrievedDoc(BaseModel):
    id: str
    title: str
    source: str
    snippet: str
    score: float | None = None
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


class AttemptStartedEvent(BaseModel):
    type: Literal["attempt_started"] = "attempt_started"
    attempt: int


class StageStartedEvent(BaseModel):
    type: Literal["stage_started"] = "stage_started"
    attempt: int
    stage: PipelineStage


class StageCompletedEvent(BaseModel):
    type: Literal["stage_completed"] = "stage_completed"
    attempt: int
    stage: PipelineStage


class StepChangedEvent(BaseModel):
    type: Literal["step_changed"] = "step_changed"
    step: ProcessingStep
    attempt: int


class QueryRewrittenEvent(BaseModel):
    type: Literal["query_rewritten"] = "query_rewritten"
    attempt: int
    rewrittenQuery: str


class DocumentsRetrievedEvent(BaseModel):
    type: Literal["documents_retrieved"] = "documents_retrieved"
    attempt: int
    retrievedDocs: list[RetrievedDoc]


class AnswerDeltaEvent(BaseModel):
    type: Literal["answer_delta"] = "answer_delta"
    attempt: int
    delta: str


class AnswerReplacedEvent(BaseModel):
    type: Literal["answer_replaced"] = "answer_replaced"
    attempt: int
    answer: str


class AnswerCompletedEvent(BaseModel):
    type: Literal["answer_completed"] = "answer_completed"
    attempt: int


class AttemptReworkTriggeredEvent(BaseModel):
    type: Literal["attempt_rework_triggered"] = "attempt_rework_triggered"
    attempt: int
    reason: str
    score: float | None = None
    threshold: float | None = None


class GradingCompletedEvent(BaseModel):
    type: Literal["grading_completed"] = "grading_completed"
    attempt: int
    hallucinationResult: HallucinationResult


class AttemptCompletedEvent(BaseModel):
    type: Literal["attempt_completed"] = "attempt_completed"
    attempt: int
    outcome: Literal["completed", "reworked", "failed"]


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
    AttemptStartedEvent,
    StageStartedEvent,
    StageCompletedEvent,
    StepChangedEvent,
    QueryRewrittenEvent,
    DocumentsRetrievedEvent,
    AnswerDeltaEvent,
    AnswerReplacedEvent,
    AnswerCompletedEvent,
    AttemptReworkTriggeredEvent,
    GradingCompletedEvent,
    AttemptCompletedEvent,
    RunCompletedEvent,
    RunFailedEvent,
    SnapshotEvent,
]
