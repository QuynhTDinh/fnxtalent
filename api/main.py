"""
FNX Talent Factory — FastAPI Server

Endpoints:
    POST /api/pipeline/run       → Run full DAG pipeline
    GET  /api/pipeline/{id}      → Get pipeline run status & results
    GET  /api/health             → Health check
    POST /api/survey/design      → AI-design a survey
    POST /api/survey/evaluate    → Evaluate a survey blueprint
    GET  /api/survey/templates   → List survey templates
    POST /api/survey/publish     → Publish to Google Forms
    GET  /api/survey/auth/status → Check Google auth status
    POST /api/survey/auth/login  → Start Google OAuth flow
"""

import asyncio
import json
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException, UploadFile, File
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
from core.agents.combat_designer_agent import CombatDesignerAgent
from core.agents.evaluator_agent import EvaluatorAgent
from core.agents.llm_client import create_llm_client

_jd_agent = JDDecoderAgent(framework_path=framework_path, llm_provider="gemini")
_cv_agent = AssessmentAgent(framework_path=framework_path, llm_provider="gemini")
_combat_agent = CombatDesignerAgent(llm_provider="gemini")
_evaluator_agent = EvaluatorAgent(create_llm_client("gemini"))

# ── History (in-memory for now; Supabase in future phase) ──
import uuid
from datetime import datetime

_history: dict = {}  # id -> record


class HistoryRecord(BaseModel):
    candidateName: str
    role: str
    fitScore: float
    assessment: dict
    jdResult: dict
    matchResult: dict


# ── Survey Agents ──
from core.agents.survey_designer_agent import SurveyDesignerAgent
from core.agents.survey_evaluator_agent import SurveyEvaluatorAgent

_survey_designer = SurveyDesignerAgent(llm_provider="gemini")
_survey_evaluator = SurveyEvaluatorAgent(llm_provider="gemini")
_survey_publisher = None  # Lazy init — requires Google credentials


def _get_publisher():
    """Lazy-initialize SurveyPublisherAgent (requires Google credentials)."""
    global _survey_publisher
    if _survey_publisher is None:
        from core.agents.survey_publisher_agent import SurveyPublisherAgent
        _survey_publisher = SurveyPublisherAgent()
    return _survey_publisher


# ── Presentation Agent ──
from core.agents.slide_agent import SlideAgent
_slide_agent = SlideAgent()

class PresentationRequest(BaseModel):
    topic: str
    context_materials: Optional[str] = None

class SurveyRequest(BaseModel):
    category: str = "student_career"  # student_career | enterprise_hr | working_pro
    objective: str = "Khảo sát chung"
    target_audience: Optional[str] = None
    num_questions: int = 15
    additional_context: Optional[str] = None


class SurveyPublishRequest(BaseModel):
    blueprint: dict
    folder_id: Optional[str] = None


class CombatRoleRequest(BaseModel):
    role: str
    seniority: Optional[str] = "Junior"
    jd: Optional[str] = "Tự động phân tích theo Role"
    group_tag: Optional[str] = "Operations/Technical"
    industry: Optional[str] = "Hóa Dầu"
    company: Optional[str] = "Đạm Cà Mau"
    
class CombatBatchRequest(BaseModel):
    roles: list[CombatRoleRequest]


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

@app.get("/api/taxonomy")
async def get_taxonomy_config():
    """Return taxonomy configuration (levels, groups, TLD mapping)."""
    try:
        from core.taxonomy import get_taxonomy
        tax = get_taxonomy()
        return tax.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/file/extract")
async def extract_file(file: UploadFile = File(...)):
    """Extract text from uploaded PDF/DOCX file."""
    from core.utils.file_parser import extract_text
    try:
        content = await file.read()
        text = extract_text(content, file.filename or "unknown")
        return {"text": text, "filename": file.filename, "chars": len(text)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File parsing error: {str(e)}")

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


# ── History Routes ──

@app.post("/api/history/save")
async def save_history(record: HistoryRecord):
    """Save an assessment result to history."""
    record_id = str(uuid.uuid4())[:8]
    _history[record_id] = {
        "id": record_id,
        "candidateName": record.candidateName,
        "role": record.role,
        "fitScore": record.fitScore,
        "assessment": record.assessment,
        "jdResult": record.jdResult,
        "matchResult": record.matchResult,
        "createdAt": datetime.now().isoformat(),
    }
    return {"id": record_id, "status": "saved"}


@app.get("/api/history")
async def list_history():
    """List all saved assessment records."""
    records = sorted(_history.values(), key=lambda r: r["createdAt"], reverse=True)
    # Return summary only (no full data)
    return [
        {
            "id": r["id"],
            "candidateName": r["candidateName"],
            "role": r["role"],
            "fitScore": r["fitScore"],
            "createdAt": r["createdAt"],
        }
        for r in records
    ]


@app.get("/api/history/{record_id}")
async def get_history(record_id: str):
    """Get a specific history record by ID."""
    record = _history.get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ── Survey Routes ──

@app.post("/api/survey/design")
async def design_survey(request: SurveyRequest):
    """Design a survey with auto-evaluation and redesign loop."""
    try:
        brief = {
            "category": request.category,
            "objective": request.objective,
            "target_audience": request.target_audience or "",
            "num_questions": request.num_questions,
            "additional_context": request.additional_context or "",
        }

        # Step 1: Design
        blueprint = _survey_designer.design(brief)

        # Step 2: Evaluate
        evaluation = _survey_evaluator.evaluate(blueprint)

        # Step 3: Redesign if needed (max 2 attempts)
        attempts = 1
        while not evaluation.get("passed", False) and attempts < 3:
            blueprint = _survey_designer.redesign(brief, evaluation)
            evaluation = _survey_evaluator.evaluate(blueprint)
            attempts += 1

        return {
            "blueprint": blueprint,
            "evaluation": evaluation,
            "attempts": attempts,
            "status": "approved" if evaluation.get("passed") else "needs_review",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/survey/evaluate")
async def evaluate_survey(blueprint: dict):
    """Evaluate an existing survey blueprint."""
    try:
        evaluation = _survey_evaluator.evaluate(blueprint)
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/survey/templates")
async def list_survey_templates():
    """List available survey templates."""
    import glob
    templates_dir = os.path.join(PROJECT_ROOT, "core", "templates", "survey")
    templates = []
    for path in sorted(glob.glob(os.path.join(templates_dir, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                templates.append({
                    "id": os.path.basename(path).replace(".json", ""),
                    "title": data.get("title", ""),
                    "category": data.get("category", ""),
                    "estimated_time": data.get("estimated_time", ""),
                    "total_questions": sum(len(s.get("questions", [])) for s in data.get("sections", [])),
                })
        except Exception:
            continue
    return templates


@app.post("/api/survey/publish")
async def publish_survey(request: SurveyPublishRequest):
    """Publish a survey blueprint to Google Forms."""
    try:
        publisher = _get_publisher()
        result = publisher.publish(request.blueprint, folder_id=request.folder_id)
        return result
    except RuntimeError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Google authentication required: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/survey/auth/status")
async def survey_auth_status():
    """Check if Google Forms API credentials are configured."""
    try:
        from core.integrations.google_auth import check_auth_status
        return check_auth_status()
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
        }


@app.post("/api/survey/auth/login")
async def survey_auth_login():
    """Trigger Google OAuth2 login flow (local dev only)."""
    if IS_VERCEL:
        raise HTTPException(
            status_code=400,
            detail="OAuth flow not available on Vercel. Use service account."
        )
    try:
        from core.integrations.google_auth import get_google_credentials
        creds = get_google_credentials()
        return {
            "status": "authenticated",
            "valid": creds.valid if creds else False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Internal Audit Routes ──

@app.post("/api/audit/org-chart/upload")
async def upload_org_chart(file: UploadFile = File(...)):
    """Upload CSV File, Parse and Cluster by Role."""
    from core.utils.excel_parser import parse_org_chart_csv
    try:
        content = await file.read()
        result = parse_org_chart_csv(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Org chart parsing error: {str(e)}")

@app.post("/api/audit/combat/generate-batch")
async def generate_combat_batch(request: CombatBatchRequest):
    """Generate combat scenarios for a list of roles."""
    import uuid
    try:
        results = []
        for req_role in request.roles:
            data = {
                "role": req_role.role,
                "seniority": req_role.seniority,
                "jd": req_role.jd,
                "group_tag": req_role.group_tag,
                "industry": req_role.industry,
                "company": req_role.company
            }
            scenario = _combat_agent.design(data)
            
            # Generate Link and Save to Persistent Store
            if "error" not in scenario:
                campaign_id = str(uuid.uuid4())[:8]
                scenario["campaign_id"] = campaign_id
                scenario["status"] = "active"
                store.save_campaign(campaign_id, scenario)
            
            results.append(scenario)
        return {"scenarios": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audit/test/{campaign_id}")
async def get_audit_campaign(campaign_id: str):
    """Candidate loads the test via campaign ID"""
    campaign_data = store.get_campaign(campaign_id)
    if not campaign_data:
        raise HTTPException(status_code=404, detail="Bài thi không tồn tại hoặc link không đúng.")
    return campaign_data

class TestSubmitRequest(BaseModel):
    candidate_name: str
    answers: dict

@app.post("/api/audit/test/{campaign_id}/submit")
async def submit_audit_test(campaign_id: str, request: TestSubmitRequest):
    """Candidate submits the test, creating a unique session"""
    import uuid
    campaign_data = store.get_campaign(campaign_id)
    if not campaign_data:
        raise HTTPException(status_code=404, detail="Bài kiểm tra không tồn tại.")
    
    session_id = str(uuid.uuid4())[:8]
    session_payload = {
        "session_id": session_id,
        "campaign_id": campaign_id,
        "candidate_name": request.candidate_name,
        "answers": request.answers,
        "status": "completed",
        "submitted_at": datetime.now().isoformat()
    }
    store.save_session(session_id, session_payload)
    return {"status": "success", "message": "Nộp bài thành công", "session_id": session_id}

@app.get("/api/audit/campaign/{campaign_id}/sessions")
async def get_campaign_sessions(campaign_id: str):
    """Admin loads all candidate sessions for a specific campaign"""
    sessions = store.get_sessions_by_campaign(campaign_id)
    return {"sessions": sessions}

@app.post("/api/audit/session/{session_id}/evaluate")
async def evaluate_audit_session(session_id: str):
    """Trigged by Admin to let AI read the candidate answers and score."""
    session_data = store.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Phiên làm bài không tồn tại.")
        
    if session_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Chỉ có thể chấm bài khi ở trạng thái completed.")

    campaign_data = store.get_campaign(session_data.get("campaign_id"))
    if not campaign_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy kịch bản thi gốc.")

    try:
        role_data = {
            "role": campaign_data.get("role", ""),
            "seniority": campaign_data.get("seniority", ""),
            "group_tag": campaign_data.get("group_tag", "")
        }
        candidate_answers = session_data.get("answers", {})
        
        evaluation_result = _evaluator_agent.evaluate(role_data, candidate_answers)
        
        update_payload = {
            "evaluation_result": evaluation_result,
            "status": "evaluated"
        }
        store.update_session(session_id, update_payload)
        
        return {"status": "success", "evaluation": evaluation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Presentation Routes ──
@app.post("/api/presentation/generate")
async def generate_presentation(request: PresentationRequest):
    result = _slide_agent.handle_event("GENERATE_SLIDE", request.dict())
    if result.get("status") == "success":
        return {"markdown": result["markdown"]}
    raise HTTPException(status_code=500, detail=result.get("message", "Unknown error generation slide"))

# ── Serve Dashboard (local dev only — Vercel handles static via vercel.json) ──

if not IS_VERCEL:
    dashboard_dir = os.path.join(PROJECT_ROOT, "dashboard")
    if os.path.exists(dashboard_dir):
        @app.get("/")
        async def serve_wizard():
            return FileResponse(os.path.join(dashboard_dir, "wizard.html"))

        @app.get("/demand")
        async def serve_demand():
            return FileResponse(os.path.join(dashboard_dir, "demand.html"))

        @app.get("/assess")
        async def serve_assess():
            return FileResponse(os.path.join(dashboard_dir, "assess.html"))

        @app.get("/report")
        async def serve_report():
            return FileResponse(os.path.join(dashboard_dir, "index.html"))

        @app.get("/history")
        async def serve_history():
            return FileResponse(os.path.join(dashboard_dir, "history.html"))

        @app.get("/audit")
        async def serve_audit():
            return FileResponse(os.path.join(dashboard_dir, "audit.html"))

        @app.get("/taxonomy")
        async def serve_taxonomy():
            return FileResponse(os.path.join(dashboard_dir, "taxonomy.html"))

        @app.get("/presentation")
        async def serve_presentation():
            return FileResponse(os.path.join(dashboard_dir, "presentation.html"))
            
        @app.get("/test")
        async def serve_test():
            return FileResponse(os.path.join(dashboard_dir, "test.html"))

        # Mount static AFTER explicit routes so /api/* takes priority
        app.mount("/", StaticFiles(directory=dashboard_dir), name="dashboard")


# ── Vercel handler ──
# Vercel Python runtime looks for `app` — already exported above.

# ── Local dev ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8005, reload=True)
