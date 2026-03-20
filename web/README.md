
# Minimal RAG System UI

This frontend keeps the Figma-exported presentation layer intact, but the runtime has been refactored for backend-owned orchestration over WebSocket.

## Run Locally

Run `npm install`.

Run `npm run dev`.

The frontend now reads shared service settings from the project root `.env` through Vite.
Set `FRONTEND_RAG_TRANSPORT=demo` if you want to force the local demo transport without a backend connection.

## Runtime Architecture

- `src/app/App.tsx`: page shell and layout only.
- `src/app/hooks/use-rag-session.ts`: owns the active run state and transport lifecycle.
- `src/app/lib/rag-socket-client.ts`: thin WebSocket transport.
- `src/app/lib/rag-demo-client.ts`: demo transport fallback used when no backend URL is configured.
- `src/app/types/rag.ts`: shared event and UI state contract.

## Environment

Copy the root `.env.example` to `.env` and set the shared service values there.

Relevant variables:

```bash
FRONTEND_HOST=127.0.0.1
FRONTEND_PORT=5173
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_WS_PATH=/ws/rag
FRONTEND_RAG_TRANSPORT=websocket
```

Optional frontend-only overrides can still be placed in `web/.env`.

## WebSocket Contract

Frontend sends:

```json
{ "type": "submit_query", "query": "What are the benefits of RAG?" }
```

Backend can then stream any of the following JSON messages:

```json
{ "type": "run_started", "runId": "abc123", "query": "What are the benefits of RAG?" }
{ "type": "step_changed", "step": "rewriting" }
{ "type": "query_rewritten", "rewrittenQuery": "Enhanced query..." }
{ "type": "documents_retrieved", "retrievedDocs": [{ "id": "1", "source": "Doc 1", "snippet": "...", "relevant": true }] }
{ "type": "answer_delta", "delta": "Retrieval-Augmented " }
{ "type": "answer_delta", "delta": "Generation improves accuracy." }
{ "type": "grading_completed", "hallucinationResult": { "score": 0.85, "explanation": "Supported by retrieved context." } }
{ "type": "run_completed" }
```

Optional convenience messages supported by the frontend:

```json
{ "type": "answer_replaced", "answer": "Full answer text" }
{ "type": "snapshot", "snapshot": { "currentStep": "generation", "answer": "Partial answer" } }
{ "type": "run_failed", "error": "Backend failed to generate an answer." }
```

## Integration Notes

- The frontend keeps only one active run in memory.
- No attempt history is stored.
- The backend owns retries, grading decisions, and orchestration.
- The answer panel is ready for incremental text updates so streamed output still renders with the existing typewriter effect.
  
