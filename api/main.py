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

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass  # dotenv not required on Vercel if env vars are set in project settings

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
# On Vercel serverless, only /tmp is writable
IS_VERCEL = os.environ.get("VERCEL", False)
data_dir = "/tmp/fnx_store" if IS_VERCEL else os.path.join(PROJECT_ROOT, "data", "store")

store = LocalStore(data_dir=data_dir)

framework_path = os.path.join(PROJECT_ROOT, "docs", "building-21", "framework_definition.md")
pipeline = build_fnx_pipeline(
    store=store,
    framework_path=framework_path,
    llm_provider="gemini",
)


# ── Request Models ──
class PipelineRequest(BaseModel):
    candidate: dict
    job: dict
    run_id: Optional[str] = None

class JDRequest(BaseModel):
    content: str
    role: Optional[str] = "Không rõ vị trí"
    company: Optional[str] = None
    industry: Optional[str] = None

class CVRequest(BaseModel):
    content: str
    name: Optional[str] = "Ứng viên"
    major: Optional[str] = None
    graduation_year: Optional[int] = None

# ── Standalone agents (for wizard step-by-step calls) ──
from core.agents.jd_decoder_agent import JDDecoderAgent
from core.agents.assessment_agent import AssessmentAgent

_jd_agent = JDDecoderAgent(framework_path=framework_path, llm_provider="gemini")
_cv_agent = AssessmentAgent(framework_path=framework_path, llm_provider="gemini")


# ── Routes ──

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "engine": "DAG Pipeline",
        "nodes": list(pipeline.nodes.keys()),
        "store": store.__class__.__name__,
        "vercel": bool(IS_VERCEL),
    }

@app.post("/api/jd/decode")
async def decode_jd(request: JDRequest):
    """Wizard Step 1: Decode JD text into Building 21 competency requirements."""
    try:
        jd_data = {
            "role": request.role,
            "content": request.content,
            "company": request.company,
            "industry": request.industry,
        }
        result = _jd_agent.decode(jd_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cv/assess")
async def assess_cv(request: CVRequest):
    """Wizard Step 2: Assess CV text into Building 21 competency matrix."""
    try:
        profile = {
            "id": "wizard_candidate",
            "fullName": request.name,
            "yearbook_info": {
                "major": request.major or "N/A",
                "graduation_year": request.graduation_year or "N/A",
            },
            "experience": [],
            "social_data": {},
            "_raw_cv_text": request.content,
        }
        # Inject raw CV text as a single experience entry for the LLM
        profile["experience"] = [{
            "title": "Toàn bộ kinh nghiệm",
            "company": "",
            "duration": "",
            "description": request.content,
        }]
        result = _cv_agent.assess(profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


# ── Serve Dashboard (local dev only — Vercel handles static via vercel.json) ──

if not IS_VERCEL:
    dashboard_dir = os.path.join(PROJECT_ROOT, "dashboard")
    if os.path.exists(dashboard_dir):
        @app.get("/")
        async def serve_wizard():
            return FileResponse(os.path.join(dashboard_dir, "wizard.html"))

        @app.get("/report")
        async def serve_report():
            return FileResponse(os.path.join(dashboard_dir, "index.html"))

        # Mount static AFTER explicit routes so /api/* takes priority
        app.mount("/", StaticFiles(directory=dashboard_dir), name="dashboard")


# ── Vercel handler ──
# Vercel Python runtime looks for `app` — already exported above.

# ── Local dev ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
