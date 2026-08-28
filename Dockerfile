# syntax=docker/dockerfile:1

# ---- build stage: compile wheels once, so the runtime image carries no toolchain
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---- runtime stage
FROM python:3.12-slim

# Fail fast, never buffer logs behind a pipe, skip .pyc in an immutable layer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Run as an unprivileged user: a container breakout should not land on root.
RUN useradd --create-home --uid 10001 accessai

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY --chown=accessai:accessai pyproject.toml README.md ./
COPY --chown=accessai:accessai accessai ./accessai
RUN pip install --no-cache-dir --no-deps -e .

USER accessai

EXPOSE 8015

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8015/healthz || exit 1

CMD ["uvicorn", "accessai.server:app", "--host", "0.0.0.0", "--port", "8015"]
