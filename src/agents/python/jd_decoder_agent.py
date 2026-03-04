"""
JDDecoderAgent - Decodes Job Descriptions into Building 21 requirement matrices using LLM.
"""

import json
from base_agent import BaseAgent
from llm_client import create_llm_client
from prompts import JD_DECODER_SYSTEM_PROMPT, JD_DECODER_USER_TEMPLATE


class JDDecoderAgent(BaseAgent):
    def __init__(self, framework_path=None, llm_provider="gemini"):
        super().__init__("JDDecoderAgent", framework_path)
        self.llm = None
        self.llm_provider = llm_provider

    def _ensure_llm(self):
        """Lazy-initialize the LLM client."""
        if self.llm is None:
            self.llm = create_llm_client(self.llm_provider)

    def handle_event(self, event_name, data):
        """Handle incoming events."""
        if event_name == "JD_SUBMITTED":
            return self.handle_jd_submission(data)

    def handle_jd_submission(self, jd_data):
        """Skill: Decode JD and convert to Building 21 requirements using LLM."""
        job_title = jd_data.get("title", jd_data.get("role", "Unknown Role"))
        self.log(f"Decoding JD for role: {job_title}")

        # ── Build JD content text ──
        jd_parts = []
        if jd_data.get("title") or jd_data.get("role"):
            jd_parts.append(f"**Chức danh**: {job_title}")
        if jd_data.get("company"):
            jd_parts.append(f"**Công ty**: {jd_data['company']}")
        if jd_data.get("industry"):
            jd_parts.append(f"**Ngành**: {jd_data['industry']}")
        if jd_data.get("seniority"):
            jd_parts.append(f"**Cấp bậc**: {jd_data['seniority']}")
        if jd_data.get("location"):
            jd_parts.append(f"**Địa điểm**: {jd_data['location']}")

        # Main content: could be in 'content', 'text', or 'description'
        content = jd_data.get("content") or jd_data.get("text") or jd_data.get("description", "")
        if content:
            jd_parts.append(f"\n**Nội dung JD**:\n{content}")

        # Requirements section
        if jd_data.get("requirements"):
            if isinstance(jd_data["requirements"], list):
                req_text = "\n".join(f"- {r}" for r in jd_data["requirements"])
            else:
                req_text = str(jd_data["requirements"])
            jd_parts.append(f"\n**Yêu cầu**:\n{req_text}")

        # Responsibilities section
        if jd_data.get("responsibilities"):
            if isinstance(jd_data["responsibilities"], list):
                resp_text = "\n".join(f"- {r}" for r in jd_data["responsibilities"])
            else:
                resp_text = str(jd_data["responsibilities"])
            jd_parts.append(f"\n**Trách nhiệm**:\n{resp_text}")

        jd_content = "\n".join(jd_parts) if jd_parts else "Không có nội dung JD."

        # ── Construct the user prompt ──
        user_prompt = JD_DECODER_USER_TEMPLATE.format(jd_content=jd_content)

        # ── Call LLM ──
        self._ensure_llm()
        self.log("Calling LLM for JD decoding...")

        try:
            result = self.llm.generate_json(
                system_prompt=JD_DECODER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            # Ensure job_id is set
            if not result.get("job_id"):
                result["job_id"] = jd_data.get("id", "auto_generated")
            self.log(
                f"JD decoded: {len(result.get('required_competencies', []))} competencies extracted."
            )
        except Exception as e:
            self.log(f"ERROR: LLM call failed: {e}")
            result = {
                "job_id": jd_data.get("id", "error"),
                "role": job_title,
                "required_competencies": [],
                "raw_jd_summary": "JD decoding failed due to LLM error.",
                "error": str(e),
            }

        self.emit_event("REQUIREMENTS_READY", result)
        return result


# ─────────────────────────────────────────────────────────────
# CLI Testing
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    import sys

    # Load .env if available
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

    # Determine provider
    provider = sys.argv[1] if len(sys.argv) > 1 else "gemini"

    agent = JDDecoderAgent(
        framework_path="docs/building-21/framework_definition.md",
        llm_provider=provider,
    )

    # Example JD for testing
    mock_jd = {
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

    result = agent.handle_event("JD_SUBMITTED", mock_jd)
    print("\n" + "=" * 60)
    print("JD DECODED RESULT:")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
