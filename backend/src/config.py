from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    port: int = int(os.getenv("BACKEND_PORT", "8000"))
    engine_mode: str = os.getenv("BACKEND_ENGINE_MODE", "fake").strip().lower()
    debug_step_delay_ms: int = int(os.getenv("BACKEND_DEBUG_STEP_DELAY_MS", "250"))
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("BACKEND_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    )


settings = Settings()
