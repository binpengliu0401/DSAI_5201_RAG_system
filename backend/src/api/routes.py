from __future__ import annotations

from fastapi import APIRouter

from backend.src.config import settings


router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "engineMode": settings.rag.engine_mode}


@router.get("/config")
async def config() -> dict:
    return {
        "engineMode": settings.rag.engine_mode,
        "frontendPublicUrl": settings.frontend.public_url,
        "backendPublicUrl": settings.backend.public_url,
        "websocketPath": settings.backend.ws_path,
        "websocketUrl": settings.backend.ws_url,
    }
