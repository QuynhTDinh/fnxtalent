"""
FNX Pipeline Demo - End-to-end test of the Python agent pipeline.

Usage:
    python demo_pipeline.py              # Uses Gemini (default)
    python demo_pipeline.py openai       # Uses OpenAI
    
Requires: GEMINI_API_KEY or OPENAI_API_KEY in .env or environment.
"""

import json
import os
import sys

# ── Setup paths ──
AGENT_DIR = os.path.join(os.path.dirname(__file__), "src", "agents", "python")
sys.path.insert(0, AGENT_DIR)

# ── Load .env ──
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

# ── Import agents ──
from assessment_agent import AssessmentAgent
from jd_decoder_agent import JDDecoderAgent
from matching_agent import MatchingAgent


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    provider = sys.argv[1] if len(sys.argv) > 1 else "gemini"
    print_section(f"FNX TALENT FACTORY PIPELINE (LLM: {provider.upper()})")

    # ── Initialize agents ──
    framework_path = os.path.join(os.path.dirname(__file__), "docs", "building-21", "framework_definition.md")
    
    assessment = AssessmentAgent(framework_path=framework_path, llm_provider=provider)
    jd_decoder = JDDecoderAgent(framework_path=framework_path, llm_provider=provider)
    matching = MatchingAgent(framework_path=framework_path)

    # ── Load candidate data ──
    data_path = os.path.join(os.path.dirname(__file__), "data", "processed", "candidates_mock.json")
    with open(data_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    candidate = candidates[0]  # Nguyễn Văn A

    # ── STEP 1: Assessment ──
    print_section("STEP 1: COMPETENCY ASSESSMENT")
    print(f"Candidate: {candidate['fullName']} ({candidate['id']})")
    
    assessment_result = assessment.handle_event("PROFILE_READY", candidate)
    print(json.dumps(assessment_result, indent=2, ensure_ascii=False))

    # ── STEP 2: JD Decoding ──
    print_section("STEP 2: JD DECODING")

    jd = {
        "id": "job_001",
        "title": "Trưởng phòng Kỹ thuật Hóa dầu",
        "company": "PetroVietnam Gas",
        "industry": "Dầu khí",
        "seniority": "Senior",
        "content": """
        Mô tả công việc:
        - Quản lý và điều phối đội ngũ 20 kỹ sư quy trình tại nhà máy lọc dầu.
        - Thiết kế, tối ưu hóa các quy trình chế biến hydrocarbon, cracking xúc tác.
        - Phân tích dữ liệu vận hành hệ thống, đề xuất giải pháp nâng cao hiệu suất.
        - Đảm bảo tuân thủ các tiêu chuẩn an toàn môi trường ISO 14001.
        
        Yêu cầu:
        - Tốt nghiệp Đại học ngành Kỹ thuật Hóa học, Hóa dầu hoặc tương đương.
        - Tối thiểu 8 năm kinh nghiệm trong ngành lọc hóa dầu.
        - Có kinh nghiệm quản lý đội nhóm từ 10 người trở lên.
        - Tư duy hệ thống, khả năng ra quyết định trong môi trường áp lực cao.
        - Tiếng Anh giao tiếp tốt (IELTS 6.0+).
        - Ưu tiên ứng viên có chứng chỉ PMP hoặc Six Sigma.
        """,
    }

    print(f"JD: {jd['title']} @ {jd['company']}")
    jd_result = jd_decoder.handle_event("JD_SUBMITTED", jd)
    print(json.dumps(jd_result, indent=2, ensure_ascii=False))

    # ── STEP 3: Matching ──
    print_section("STEP 3: TALENT MATCHING")

    # Transform assessment result to matching format
    match_candidate = {
        "candidateId": assessment_result.get("candidateId", candidate["id"]),
        "competencies": [
            {"code": c["code"], "level": c["level"]}
            for c in assessment_result.get("competencies", [])
        ],
    }

    # Transform JD result to matching format
    match_jd = {
        "job_id": jd_result.get("job_id", jd["id"]),
        "required_competencies": [
            {
                "code": c["code"],
                "target_level": c["target_level"],
                "priority": c.get("priority", "Medium"),
            }
            for c in jd_result.get("required_competencies", [])
        ],
    }

    matching.handle_event("COMPETENCY_MEASURED", match_candidate)
    match_result = matching.handle_event("REQUIREMENTS_READY", match_jd)

    if match_result:
        print(json.dumps(match_result, indent=2, ensure_ascii=False))

    print_section("PIPELINE COMPLETE")
    print("All 3 stages executed successfully with real LLM calls!")
    print(f"  - Assessment: {len(assessment_result.get('competencies', []))} competencies mapped")
    print(f"  - JD Requirements: {len(jd_result.get('required_competencies', []))} competencies extracted")
    if match_result:
        print(f"  - Fit Score: {match_result.get('fitScore', 'N/A')}%")
        print(f"  - Gaps: {len(match_result.get('gaps', []))} areas need improvement")
    print(f"  - Candidate: {candidate['fullName']}")
    print(f"  - Role: {jd['title']}")


if __name__ == "__main__":
    main()
