import re

with open('api/main.py', 'r') as f:
    content = f.read()

# Patch 1: Import
if "from core.agents.slide_agent" not in content:
    target1 = "class SurveyRequest(BaseModel):"
    replacement1 = """# ── Presentation Agent ──
from core.agents.slide_agent import SlideAgent
_slide_agent = SlideAgent()

class PresentationRequest(BaseModel):
    topic: str
    context_materials: Optional[str] = None

class SurveyRequest(BaseModel):"""
    content = content.replace(target1, replacement1)

# Patch 2: Route
if "/api/presentation/generate" not in content:
    target2 = "# ── Serve Dashboard"
    replacement2 = """# ── Presentation Routes ──
@app.post("/api/presentation/generate")
async def generate_presentation(request: PresentationRequest):
    result = _slide_agent.handle_event("GENERATE_SLIDE", request.dict())
    if result.get("status") == "success":
        return {"markdown": result["markdown"]}
    raise HTTPException(status_code=500, detail=result.get("message", "Unknown error generation slide"))

# ── Serve Dashboard"""
    content = content.replace(target2, replacement2)

# Patch 3: Local Dev
if "/presentation" not in content:
    target3 = """        @app.get("/taxonomy")
        async def serve_taxonomy():
            return FileResponse(os.path.join(dashboard_dir, "taxonomy.html"))"""
    replacement3 = """        @app.get("/taxonomy")
        async def serve_taxonomy():
            return FileResponse(os.path.join(dashboard_dir, "taxonomy.html"))

        @app.get("/presentation")
        async def serve_presentation():
            return FileResponse(os.path.join(dashboard_dir, "presentation.html"))"""
    content = content.replace(target3, replacement3)

with open('api/main.py', 'w') as f:
    f.write(content)
print("Patched main.py")
