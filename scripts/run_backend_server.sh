#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"

cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
    echo "[error] uv is not installed or not on PATH."
    echo "Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if [ ! -f "$ROOT_DIR/.env" ]; then
    echo "[error] Missing $ROOT_DIR/.env"
    echo "Create it first or export the required environment variables."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "[setup] Creating virtual environment at $VENV_DIR"
    uv venv "$VENV_DIR"
fi

echo "[setup] Installing backend dependencies from requirements.txt"
uv pip install --python "$VENV_DIR/bin/python" -r requirements.txt

echo "[setup] Running dataset preparation"
uv run --python "$VENV_DIR/bin/python" python -m scripts.setup_data

echo "[setup] Rebuilding retrieval index"
uv run --python "$VENV_DIR/bin/python" python -m scripts.build_index

echo "[startup] Launching backend"
exec uv run --python "$VENV_DIR/bin/python" python -m backend.run
