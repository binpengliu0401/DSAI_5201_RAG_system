# Backend

Standalone Python backend for the React frontend in [`/web`](/Users/ethan/Documents/poly/AIBDCP/group-project/DSAI_5201_RAG_system/web).

## Stack

- FastAPI
- Uvicorn
- Pydantic
- Native WebSocket support

## Run

```bash
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment

- `BACKEND_ENGINE_MODE=fake` uses the deterministic debug engine
- `BACKEND_ENGINE_MODE=core` runs the existing workflow in [`/app`](/Users/ethan/Documents/poly/AIBDCP/group-project/DSAI_5201_RAG_system/app)
- `BACKEND_DEBUG_STEP_DELAY_MS=250` controls fake engine pacing
- `BACKEND_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`

## Endpoints

- `GET /health`
- `GET /config`
- `WS /ws/rag`

## Frontend wiring

Set `VITE_RAG_WS_URL=ws://localhost:8000/ws/rag` in the frontend environment to connect the React app to this backend.
