FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.2 /uv /uvx /usr/local/bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
RUN uv venv "${VIRTUAL_ENV}" \
    && uv pip install --python "${VIRTUAL_ENV}/bin/python" --no-cache -r requirements.txt

COPY app /app/app
COPY backend /app/backend
COPY config /app/config
COPY scripts /app/scripts
COPY docker /app/docker

RUN useradd --create-home --shell /bin/sh appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app "${VIRTUAL_ENV}"

USER appuser

EXPOSE 8000

ENTRYPOINT ["sh", "/app/docker/backend-entrypoint.sh"]
