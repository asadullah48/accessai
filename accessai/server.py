import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from accessai.core.models import LiveStreamFrame, ProcessedStreamWindow, AccessibilityAuditResult
from accessai.orchestration.accessai_engine import AccessAIEngine

app = FastAPI(
    title="AccessAI Real-Time Accessibility Gateway",
    version="1.0.0",
    description="Real-Time Audio Descriptions & WCAG 2.2 AAA Multi-Agent Framework for Visually Impaired Users"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = AccessAIEngine()

# Mount Static UI Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"service": "AccessAI", "status": "active", "docs": "/docs"}

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "AccessAI", "version": "1.0.0"}

@app.get("/readyz")
def readyz():
    return {"status": "ready", "assistive_agents_active": 3, "wcag_standard": "WCAG_2_2_AAA"}

@app.post("/api/v1/accessibility/describe-stream", response_model=ProcessedStreamWindow)
def describe_stream(frame: LiveStreamFrame):
    return engine.process_live_frame(frame)
