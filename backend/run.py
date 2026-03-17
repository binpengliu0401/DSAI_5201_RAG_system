from __future__ import annotations

import uvicorn

from config.logging import configure_logging, get_logger
from config.settings import settings


configure_logging(settings.runtime.log_level)
logger = get_logger(__name__)


def main() -> None:
    logger.info(
        "Starting backend server on %s:%s with reload enabled",
        settings.backend.host,
        settings.backend.port,
    )
    uvicorn.run(
        "backend.src.main:app",
        host=settings.backend.host,
        port=settings.backend.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
