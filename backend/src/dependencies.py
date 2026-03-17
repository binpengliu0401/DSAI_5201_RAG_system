from __future__ import annotations

from backend.src.config import settings
from backend.src.engines.base import RAGEngine
from backend.src.engines.fake_engine import FakeRAGEngine
from backend.src.services.session_service import SessionService


def get_engine() -> RAGEngine:
    if settings.engine_mode == "core":
        from backend.src.engines.core_engine import CoreRAGEngine

        return CoreRAGEngine()
    return FakeRAGEngine(step_delay_ms=settings.debug_step_delay_ms)


def get_session_service() -> SessionService:
    return SessionService(engine=get_engine())
