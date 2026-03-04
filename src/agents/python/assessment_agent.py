"""
AssessmentAgent - Maps candidate experience to Building 21 competencies using LLM.
"""

import json
from base_agent import BaseAgent
from llm_client import create_llm_client
from prompts import ASSESSMENT_SYSTEM_PROMPT, ASSESSMENT_USER_TEMPLATE


class AssessmentAgent(BaseAgent):
    def __init__(self, framework_path=None, llm_provider="gemini"):
        super().__init__("AssessmentAgent", framework_path)
        self.llm = None
        self.llm_provider = llm_provider

    def _ensure_llm(self):
        """Lazy-initialize the LLM client (so agent can be created without API key)."""
        if self.llm is None:
            self.llm = create_llm_client(self.llm_provider)

    def handle_event(self, event_name, data):
        """Handle incoming events."""
        if event_name == "PROFILE_READY":
            return self.handle_profile_ready(data)

    def handle_profile_ready(self, profile):
        """Skill: Map experiences to Building 21 using LLM."""
        self.log(f"Auditing profile: {profile.get('fullName')}")

        # ── Build experience text ──
        experience_entries = profile.get("experience", [])
        experience_text = ""
        for exp in experience_entries:
            experience_text += (
                f"- **{exp.get('title', 'N/A')}** tại {exp.get('company', 'N/A')} "
                f"({exp.get('duration', 'N/A')})\n"
                f"  {exp.get('description', 'Không có mô tả.')}\n\n"
            )
        if not experience_text:
            experience_text = "Không có dữ liệu kinh nghiệm."

        # ── Build social data text ──
        social = profile.get("social_data", {})
        social_lines = []
        if social.get("linkedin_url"):
            social_lines.append(f"- LinkedIn: {social['linkedin_url']}")
        if social.get("google_scholar"):
            social_lines.append(f"- Google Scholar: {social['google_scholar']}")
        if social.get("patents"):
            social_lines.append(f"- Bằng sáng chế: {', '.join(social['patents'])}")
        if social.get("publications"):
            social_lines.append(f"- Công bố khoa học: {', '.join(social['publications'])}")
        social_data = "\n".join(social_lines) if social_lines else "Không có dữ liệu bổ sung."

        # ── Build yearbook info ──
        yearbook = profile.get("yearbook_info", {})

        # ── Construct the user prompt ──
        user_prompt = ASSESSMENT_USER_TEMPLATE.format(
            candidate_id=profile.get("id", "UNKNOWN"),
            full_name=profile.get("fullName", "N/A"),
            major=yearbook.get("major", "N/A"),
            graduation_year=yearbook.get("graduation_year", "N/A"),
            experience_text=experience_text,
            social_data=social_data,
        )

        # ── Call LLM ──
        self._ensure_llm()
        self.log("Calling LLM for competency assessment...")

        try:
            result = self.llm.generate_json(
                system_prompt=ASSESSMENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            self.log(f"Assessment complete: {len(result.get('competencies', []))} competencies identified.")
        except Exception as e:
            self.log(f"ERROR: LLM call failed: {e}")
            result = {
                "candidateId": profile.get("id"),
                "fullName": profile.get("fullName"),
                "competencies": [],
                "overallStrength": "Assessment failed due to LLM error.",
                "developmentAreas": "N/A",
                "error": str(e),
            }

        self.emit_event("COMPETENCY_MEASURED", result)
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

    agent = AssessmentAgent(
        framework_path="docs/building-21/framework_definition.md",
        llm_provider=provider,
    )

    # Use the mock candidate data
    mock_profile = {
        "id": "cand_001",
        "fullName": "Nguyễn Văn A",
        "yearbook_info": {
            "major": "Kỹ thuật Hóa học",
            "graduation_year": 2015,
            "class": "CH10A",
        },
        "experience": [
            {
                "title": "Kỹ sư quy trình",
                "company": "PetroVietnam",
                "duration": "2015-2020",
                "description": (
                    "Quản lý dây chuyền sản xuất nhựa PP, tối ưu hóa quy trình nhiệt và áp suất. "
                    "Xây dựng hệ thống giám sát an toàn tự động."
                ),
            },
            {
                "title": "Trưởng phòng kỹ thuật",
                "company": "Chemical Corp X",
                "duration": "2020-Present",
                "description": (
                    "Điều phối đội ngũ 15 kỹ sư, thiết kế các giải pháp xử lý nước thải công nghiệp. "
                    "Áp dụng tư duy hệ thống để giảm 20% chi phí vận hành."
                ),
            },
        ],
        "social_data": {
            "linkedin_url": "linkedin.com/in/nguyen-van-a",
            "patents": ["Hệ thống lọc khí thải đa tầng (2022)"],
        },
    }

    result = agent.handle_event("PROFILE_READY", mock_profile)
    print("\n" + "=" * 60)
    print("ASSESSMENT RESULT:")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
