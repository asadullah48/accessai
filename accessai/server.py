"""FastAPI gateway exposing the AccessAI accessibility pipeline and studio UI."""

from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from accessai import __version__
from accessai.config import configure_logging, load_settings
from accessai.core.models import LiveStreamFrame, ProcessedStreamWindow
from accessai.orchestration.accessai_engine import AccessAIEngine

settings = load_settings()
configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

# Probes fire every few seconds; logging them at INFO buries real traffic.
_PROBE_PATHS = frozenset({"/healthz", "/readyz"})


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Record the settings actually in force, so deployments are auditable."""
    logger.info(
        "AccessAI %s starting in %s; cors_origins=%s credentials=%s",
        __version__,
        settings.environment,
        ",".join(settings.cors_origins),
        settings.cors_allow_credentials,
    )
    yield


app = FastAPI(
    title="AccessAI Real-Time Accessibility Gateway",
    version=__version__,
    description=(
        "Real-Time Audio Descriptions & WCAG 2.2 AAA Multi-Agent Framework "
        "for Visually Impaired Users"
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    """
    Tag every response with a correlation id and its server-side duration.

    An inbound X-Request-ID is preserved so a trace survives across a proxy;
    otherwise one is minted here.
    """
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
    started = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - started) * 1000.0
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

    is_probe = request.url.path in _PROBE_PATHS and not settings.log_health_probes
    logger.log(
        logging.DEBUG if is_probe else logging.INFO,
        "%s %s -> %d in %.2fms [%s]",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


engine = AccessAIEngine()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the accessibility studio, falling back to a service descriptor."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"service": "AccessAI", "status": "active", "docs": "/docs"}


@app.get("/healthz", tags=["operations"])
def healthz():
    """Liveness probe."""
    return {"status": "healthy", "service": "AccessAI", "version": __version__}


@app.get("/readyz", tags=["operations"])
def readyz():
    """Readiness probe reporting the active agent roster."""
    return {
        "status": "ready",
        "assistive_agents_active": 3,
        "wcag_standard": "WCAG_2_2_AAA",
    }


@app.post(
    "/api/v1/accessibility/describe-stream",
    response_model=ProcessedStreamWindow,
    tags=["accessibility"],
    summary="Generate a gap-fitted audio description and audit it",
)
def describe_stream(frame: LiveStreamFrame) -> ProcessedStreamWindow:
    """
    Analyse one live stream frame and return the description with its audit.

    The audit is evaluated, not asserted: a description that overruns the
    dialogue gap, or captions below the contrast threshold, yield a failing
    record with a reduced compliance score.
    """
    return engine.process_live_frame(frame)
