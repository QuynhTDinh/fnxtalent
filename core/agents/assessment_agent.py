"""
AssessmentAgent — Maps candidate experience to Building 21 competencies via LLM.
"""

import json
from .base_agent import BaseAgent
from .llm_client import create_llm_client
from .prompts import ASSESSMENT_SYSTEM_PROMPT, ASSESSMENT_USER_TEMPLATE


class AssessmentAgent(BaseAgent):
    def __init__(self, framework_path=None, llm_provider="gemini"):
        super().__init__("AssessmentAgent", framework_path)
        self.llm = None
        self.llm_provider = llm_provider

    def _ensure_llm(self):
        if self.llm is None:
            self.llm = create_llm_client(self.llm_provider)

    def handle_event(self, event_name, data):
        if event_name == "PROFILE_READY":
            return self.assess(data)

    def assess(self, profile):
        """Run competency assessment on a candidate profile."""
        self.log(f"Auditing profile: {profile.get('fullName')}")

        # Build experience text
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

        # Build social data text
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

        yearbook = profile.get("yearbook_info", {})

        user_prompt = ASSESSMENT_USER_TEMPLATE.format(
            candidate_id=profile.get("id", "UNKNOWN"),
            full_name=profile.get("fullName", "N/A"),
            major=yearbook.get("major", "N/A"),
            graduation_year=yearbook.get("graduation_year", "N/A"),
            experience_text=experience_text,
            social_data=social_data,
        )

        self._ensure_llm()
        self.log("Calling LLM for competency assessment...")

        try:
            result = self.llm.generate_json(
                system_prompt=ASSESSMENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            self.log(f"Assessment complete: {len(result.get('competencies', []))} competencies.")
        except Exception as e:
            self.log(f"ERROR: LLM call failed: {e}")
            result = {
                "candidateId": profile.get("id"),
                "fullName": profile.get("fullName"),
                "competencies": [],
                "overallStrength": "Assessment failed.",
                "developmentAreas": "N/A",
                "error": str(e),
            }

        return result
