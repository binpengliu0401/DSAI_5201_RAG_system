from __future__ import annotations

import logging
import os
from typing import Any

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def _trace(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


logging.Logger.trace = _trace  # type: ignore[attr-defined]


def _resolve_level(level: str) -> int:
    normalized = level.upper()
    if normalized == "TRACE":
        return TRACE_LEVEL_NUM
    return getattr(logging, normalized, logging.INFO)


def _configure_third_party_loggers(*, app_level: int) -> None:
    transport_debug_enabled = os.getenv("LOG_TRANSPORT_DEBUG", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    third_party_level = logging.DEBUG if transport_debug_enabled else logging.INFO

    for logger_name in ("openai", "openai._base_client", "httpcore", "httpx"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(third_party_level)
        logger.propagate = True

    # Keep app namespaces on the requested level.
    for logger_name in ("app", "backend", "config", "main", "llm", "grading"):
        logging.getLogger(logger_name).setLevel(app_level)


def configure_logging(level: str = "INFO") -> None:
    resolved_level = _resolve_level(level)
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    _configure_third_party_loggers(app_level=resolved_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_stage_event(stage: str, event: str, payload: dict) -> None:
    logger = get_logger(stage)
    logger.trace("%s", {"stage": stage, "event": event, **payload})
