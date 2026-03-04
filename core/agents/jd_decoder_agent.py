"""
JDDecoderAgent — Decodes JDs into Building 21 requirement matrices via LLM.
"""

from .base_agent import BaseAgent
from .llm_client import create_llm_client
from .prompts import JD_DECODER_SYSTEM_PROMPT, JD_DECODER_USER_TEMPLATE


class JDDecoderAgent(BaseAgent):
    def __init__(self, framework_path=None, llm_provider="gemini"):
        super().__init__("JDDecoderAgent", framework_path)
        self.llm = None
        self.llm_provider = llm_provider

    def _ensure_llm(self):
        if self.llm is None:
            self.llm = create_llm_client(self.llm_provider)

    def handle_event(self, event_name, data):
        if event_name == "JD_SUBMITTED":
            return self.decode(data)

    def decode(self, jd_data):
        """Decode a JD into a Building 21 requirement matrix."""
        job_title = jd_data.get("title") or jd_data.get("role", "Unknown Role")
        self.log(f"Decoding JD: {job_title}")

        jd_parts = []
        if jd_data.get("title") or jd_data.get("role"):
            jd_parts.append(f"**Chức danh**: {job_title}")
        if jd_data.get("company"):
            jd_parts.append(f"**Công ty**: {jd_data['company']}")
        if jd_data.get("industry"):
            jd_parts.append(f"**Ngành**: {jd_data['industry']}")
        if jd_data.get("seniority"):
            jd_parts.append(f"**Cấp bậc**: {jd_data['seniority']}")

        content = jd_data.get("content") or jd_data.get("text") or jd_data.get("description", "")
        if content:
            jd_parts.append(f"\n**Nội dung JD**:\n{content}")

        jd_content = "\n".join(jd_parts) if jd_parts else "Không có nội dung JD."

        user_prompt = JD_DECODER_USER_TEMPLATE.format(jd_content=jd_content)

        self._ensure_llm()
        self.log("Calling LLM for JD decoding...")

        try:
            result = self.llm.generate_json(
                system_prompt=JD_DECODER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            if not result.get("job_id"):
                result["job_id"] = jd_data.get("id", "auto_generated")
            self.log(f"JD decoded: {len(result.get('required_competencies', []))} competencies.")
        except Exception as e:
            self.log(f"ERROR: LLM call failed: {e}")
            result = {
                "job_id": jd_data.get("id", "error"),
                "role": job_title,
                "required_competencies": [],
                "raw_jd_summary": "JD decoding failed.",
                "error": str(e),
            }

        return result
