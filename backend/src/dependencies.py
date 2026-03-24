from __future__ import annotations

from functools import lru_cache

from backend.src.config import settings
from backend.src.engines.base import RAGEngine
from backend.src.engines.fake_engine import FakeRAGEngine
from backend.src.services.session_service import SessionService
from config.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_engine() -> RAGEngine:
    if settings.rag.engine_mode == "core":
        from backend.src.engines.core_engine import CoreRAGEngine

        return CoreRAGEngine()
    return FakeRAGEngine(step_delay_ms=settings.rag.debug_step_delay_ms)


@lru_cache(maxsize=1)
def get_session_service() -> SessionService:
    return SessionService(engine=get_engine())


def warmup_backend() -> None:
    logger.info("Starting backend warmup for engine_mode=%s", settings.rag.engine_mode)
    get_session_service()
    logger.info("Backend warmup complete")
