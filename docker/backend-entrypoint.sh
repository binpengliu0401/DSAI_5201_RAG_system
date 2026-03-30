#!/bin/sh
set -eu

cd /app

if [ -f "/app/.env" ]; then
    echo "[startup] Using mounted /app/.env file."
else
    echo "[startup] /app/.env not found. Relying on injected environment variables."
fi

echo "[startup] Running data setup..."
uv run --active --no-sync python -m scripts.setup_data

echo "[startup] Building retrieval index..."
uv run --active --no-sync python -m scripts.build_index

echo "[startup] Starting backend..."
exec uv run --active --no-sync python -m backend.run
