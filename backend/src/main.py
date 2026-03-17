from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api.routes import router as rest_router
from backend.src.api.websocket import router as websocket_router
from backend.src.config import settings


app = FastAPI(title="RAG Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins) or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(rest_router)
app.include_router(websocket_router)

