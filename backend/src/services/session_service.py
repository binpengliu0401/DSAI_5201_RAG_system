from __future__ import annotations

from backend.src.engines.base import RAGEngine
from backend.src.schemas.events import ServerEvent


class SessionService:
    def __init__(self, engine: RAGEngine) -> None:
        self.engine = engine

    async def stream_query(self, query: str):
        async for event in self.engine.run(query):
            yield event

    @staticmethod
    def serialize_event(event: ServerEvent) -> dict:
        return event.model_dump(exclude_none=True)
