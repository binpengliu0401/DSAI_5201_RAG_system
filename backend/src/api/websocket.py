from __future__ import annotations

import asyncio
import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from backend.src.dependencies import get_session_service
from backend.src.schemas.events import RunFailedEvent
from backend.src.schemas.messages import SubmitQueryMessage
from config.logging import get_logger


router = APIRouter()
logger = get_logger(__name__)


async def _run_query(websocket: WebSocket, query: str) -> None:
    service = get_session_service()
    try:
        logger.info("Processing websocket query: %s", query)
        async for event in service.stream_query(query):
            await websocket.send_json(service.serialize_event(event))
    except asyncio.CancelledError:
        logger.info("Cancelled in-flight websocket query")
        raise
    except Exception as exc:
        logger.exception("Backend websocket execution failed")
        event = RunFailedEvent(error=f"Backend execution failed: {exc}")
        await websocket.send_json(event.model_dump())


@router.websocket("/ws/rag")
async def rag_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("WebSocket client connected from %s", websocket.client)
    current_task: asyncio.Task | None = None

    try:
        while True:
            payload = await websocket.receive_json()
            try:
                message = SubmitQueryMessage.model_validate(payload)
            except ValidationError as exc:
                event = RunFailedEvent(error=f"Invalid client message: {exc.errors()[0]['msg']}")
                await websocket.send_json(event.model_dump())
                continue

            query = message.query.strip()
            if not query:
                await websocket.send_json(
                    RunFailedEvent(error="Query must not be empty.").model_dump()
                )
                continue

            if current_task and not current_task.done():
                logger.info("Cancelling previous websocket query before starting a new one")
                current_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await current_task

            current_task = asyncio.create_task(_run_query(websocket, query))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from %s", websocket.client)
        if current_task and not current_task.done():
            current_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await current_task
