import time
from typing import Any, Literal
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

from config.logging import log_stage_event
from config.settings import settings


LLMTask = Literal[
    "default",
    "rewriting",
    "generation",
    "grading",
    "grading_escalation",
]


class LLMTraceCallbackHandler(BaseCallbackHandler):
    def __init__(self, *, task: LLMTask, model: str, endpoint: str):
        self.task = task
        self.model = model
        self.endpoint = endpoint
        self._start_times: dict[str, float] = {}

    def _key(self, run_id: UUID | str) -> str:
        return str(run_id)

    def on_chat_model_start(self, serialized: dict[str, Any], messages: list[list[Any]], *, run_id: UUID, **kwargs: Any) -> None:
        self._start_times[self._key(run_id)] = time.perf_counter()

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], *, run_id: UUID, **kwargs: Any) -> None:
        self._start_times[self._key(run_id)] = time.perf_counter()

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:
        started_at = self._start_times.pop(self._key(run_id), None)
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2) if started_at else None
        log_stage_event(
            "llm",
            "llm_call",
            {
                "model": self.model,
                "task": self.task,
                "endpoint": self.endpoint,
                "latency_ms": latency_ms,
            },
        )

    def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        started_at = self._start_times.pop(self._key(run_id), None)
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2) if started_at else None
        log_stage_event(
            "llm",
            "llm_call_failed",
            {
                "model": self.model,
                "task": self.task,
                "endpoint": self.endpoint,
                "latency_ms": latency_ms,
                "error": str(error),
            },
        )


def _normalize_openai_base_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized[: -len("/chat/completions")]
    return normalized


def _chat_completions_endpoint(base_url: str) -> str:
    return f"{_normalize_openai_base_url(base_url)}/chat/completions"


def _model_for_task(task: LLMTask = "default") -> str:
    llm_settings = settings.llm
    model_map: dict[LLMTask, str] = {
        "default": llm_settings.default_model_name,
        "rewriting": llm_settings.rewriting_model_name,
        "generation": llm_settings.generation_model_name,
        "grading": llm_settings.grading_model_name,
        "grading_escalation": llm_settings.grading_escalation_model_name,
    }
    return model_map[task]


def get_llm(task: LLMTask = "default"):
    model = _model_for_task(task)
    normalized_base_url = _normalize_openai_base_url(settings.llm.base_url)
    callback = LLMTraceCallbackHandler(
        task=task,
        model=model,
        endpoint=_chat_completions_endpoint(settings.llm.base_url),
    )
    return ChatOpenAI(
        model=model,
        api_key=settings.llm.api_key,  # type: ignore[arg-type]
        base_url=normalized_base_url,
        temperature=settings.llm.temperature,
        callbacks=[callback],
    )
