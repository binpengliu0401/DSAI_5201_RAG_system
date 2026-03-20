# Backend

Standalone Python backend for the React frontend in [`/web`](/Users/ethan/Documents/poly/AIBDCP/group-project/DSAI_5201_RAG_system/web).

## Stack

- FastAPI
- Uvicorn
- Pydantic
- Native WebSocket support

## Run

```bash
python3 -m backend.run
```

## Environment

- Shared system config lives in the root `.env`
- `RAG_ENGINE_MODE=fake` uses the deterministic debug engine
- `RAG_ENGINE_MODE=core` runs the existing workflow in [`/app`](/Users/ethan/Documents/poly/AIBDCP/group-project/DSAI_5201_RAG_system/app)
- `DEBUG_STEP_DELAY_MS=250` controls fake engine pacing
- `ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`

## Endpoints

- `GET /health`
- `GET /config`
- `WS /ws/rag`

## Frontend wiring

Set the root service config in `.env`; the frontend now derives its WebSocket URL from the same root settings.
