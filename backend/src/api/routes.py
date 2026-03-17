from __future__ import annotations

from fastapi import APIRouter

from backend.src.config import settings


router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "engineMode": settings.engine_mode}


@router.get("/config")
async def config() -> dict:
    return {
        "engineMode": settings.engine_mode,
        "websocketPath": "/ws/rag",
    }
