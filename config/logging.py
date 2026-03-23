from __future__ import annotations

import logging
from typing import Any

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def _trace(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


logging.Logger.trace = _trace  # type: ignore[attr-defined]

def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=TRACE_LEVEL_NUM if level.upper() == "TRACE" else getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_stage_event(stage: str, event: str, payload: dict) -> None:
    logger = get_logger(stage)
    logger.trace("%s", {"stage": stage, "event": event, **payload})
