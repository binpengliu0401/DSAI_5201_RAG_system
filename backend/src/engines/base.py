from __future__ import annotations

from typing import AsyncIterator, Protocol

from backend.src.schemas.events import ServerEvent


class RAGEngine(Protocol):
    async def run(self, query: str) -> AsyncIterator[ServerEvent]:
        """Yield server events for a query execution."""
