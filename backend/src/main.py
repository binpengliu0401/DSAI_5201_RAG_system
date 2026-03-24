from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api.routes import router as rest_router
from backend.src.api.websocket import router as websocket_router
from backend.src.config import settings
from backend.src.dependencies import warmup_backend
from config.logging import configure_logging, get_logger


configure_logging(settings.runtime.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    warmup_backend()
    yield


app = FastAPI(title="RAG Backend", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.backend.allowed_origins) or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(rest_router)
app.include_router(websocket_router)

logger.info(
    "Backend configured env=%s host=%s port=%s engine=%s ws=%s",
    settings.runtime.app_env,
    settings.backend.host,
    settings.backend.port,
    settings.rag.engine_mode,
    settings.backend.ws_url,
)
