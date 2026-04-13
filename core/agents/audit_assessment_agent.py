"""
AuditAssessmentAgent — Evaluates employee performance via combat test scenarios & historical evidence.
"""

from core.agents.base_agent import BaseAgent
from core.agents.llm_client import create_llm_client
from core.agents.audit_prompts import AUDIT_ASSESSMENT_SYSTEM, AUDIT_USER_TEMPLATE

class AuditAssessmentAgent(BaseAgent):
    def __init__(self, framework_path=None, llm_provider="gemini"):
        super().__init__("AuditAssessmentAgent", framework_path)
        self.llm = None
        self.llm_provider = llm_provider

    def _ensure_llm(self):
        if self.llm is None:
            self.llm = create_llm_client(self.llm_provider)

    def handle_event(self, event_name, data):
        if event_name == "AUDIT_SUBMISSION_READY":
            return self.assess(data)

    def assess(self, submission_data: dict) -> dict:
        """Evaluate an internal employee's combat answers and historical evidence.
        
        Args:
            submission_data: {
                "employee_id": "NV001",
                "role": "Trưởng phòng Kỹ thuật",
                "combat_context": "Dây chuyền B lỗi...",
                "combat_answers": "Tôi đề xuất ngắt toàn bộ dòng diện...",
                "historical_evidence": "Báo cáo tối ưu hệ thống 2025 đính kèm..."
            }
        """
        employee_id = submission_data.get("employee_id", "UNKNOWN")
        role = submission_data.get("role", "N/A")
        self.log(f"Auditing Internal Employee: {employee_id} - {role}")

        user_prompt = AUDIT_USER_TEMPLATE.format(
            employee_id=employee_id,
            role=role,
            combat_context=submission_data.get("combat_context", "N/A"),
            combat_answers=submission_data.get("combat_answers", "Không có câu trả lời."),
            historical_evidence=submission_data.get("historical_evidence", "Không cung cấp bằng chứng lịch sử.")
        )

        self._ensure_llm()
        self.log("Calling LLM for internal audit assessment...")

        try:
            result = self.llm.generate_json(
                system_prompt=AUDIT_ASSESSMENT_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.1,  # Keep it grounded
            )
            self.log(f"Audit complete: {len(result.get('competencies', []))} competencies evaluated.")
        except Exception as e:
            self.log(f"ERROR: Audit LLM call failed: {e}")
            result = {
                "employee_id": employee_id,
                "role": role,
                "competencies": [],
                "audit_summary": "Audit evaluation failed.",
                "error": str(e),
            }

        return result
