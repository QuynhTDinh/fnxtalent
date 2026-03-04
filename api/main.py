"""
FNX Talent Factory — FastAPI Server

Endpoints:
    POST /api/pipeline/run    → Run full DAG pipeline
    GET  /api/pipeline/{id}   → Get pipeline run status & results
    GET  /api/health          → Health check
"""

import asyncio
import json
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from core.store.local_store import LocalStore
from core.pipeline.nodes import build_fnx_pipeline

# ── App Setup ──
app = FastAPI(
    title="FNX Talent Factory API",
    description="DAG Pipeline Engine for AI-powered talent assessment",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── State ──
store = LocalStore(data_dir=os.path.join(PROJECT_ROOT, "data", "store"))
pipeline = build_fnx_pipeline(
    store=store,
    framework_path=os.path.join(PROJECT_ROOT, "docs", "building-21", "framework_definition.md"),
    llm_provider="gemini",
)


# ── Request Models ──
class PipelineRequest(BaseModel):
    candidate: dict
    job: dict
    run_id: Optional[str] = None


# ── Routes ──

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "engine": "DAG Pipeline",
        "nodes": list(pipeline.nodes.keys()),
        "store": store.__class__.__name__,
    }


@app.post("/api/pipeline/run")
async def run_pipeline(request: PipelineRequest):
    """Run the full DAG pipeline for a candidate + job pair."""
    try:
        result = await pipeline.run(
            candidate_data=request.candidate,
            job_data=request.job,
            run_id=request.run_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/{run_id}")
async def get_pipeline_run(run_id: str):
    """Get the status and results of a pipeline run."""
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    node_results = store.get_all_node_results(run_id)

    return {
        "run": run,
        "node_results": node_results,
    }


# ── Serve Dashboard (static files) ──

dashboard_dir = os.path.join(PROJECT_ROOT, "dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="dashboard")

    @app.get("/")
    async def serve_dashboard():
        return FileResponse(os.path.join(dashboard_dir, "index.html"))


# ── Run ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
