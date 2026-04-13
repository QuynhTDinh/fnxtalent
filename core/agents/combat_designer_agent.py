"""
CombatDesignerAgent — Tạo kịch bản Combat Audit theo tiêu chuẩn FNX.

Input:  Role details (role title, jd, seniority)
Output: Combat scenario JSON (scenario_title, background_context, questions)
"""

from core.agents.base_agent import BaseAgent
from core.agents.llm_client import create_llm_client
from core.agents.combat_prompts import COMBAT_DESIGNER_SYSTEM, build_combat_prompt

class CombatDesignerAgent(BaseAgent):
    def __init__(self, llm_provider="gemini", **kwargs):
        super().__init__(name="CombatDesignerAgent")
        self.llm = create_llm_client(llm_provider, **kwargs)

    def handle_event(self, event_name, data):
        if event_name == "COMBAT_DESIGN_REQUESTED":
            return self.design(data)
        return None

    def design(self, role_data: dict) -> dict:
        """Generate a combat scenario for an internal audit.
        
        Args:
            role_data: {
                "role": "Chuyên viên Vận hành DCS",
                "seniority": "Junior",
                "jd": "Giám sát hệ thống SCADA, báo cáo rủi ro..."
            }
        """
        self.log(f"Designing combat scenario for: {role_data.get('role')}")

        user_prompt = build_combat_prompt(role_data)
        
        try:
            scenario = self.llm.generate_json(
                system_prompt=COMBAT_DESIGNER_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.6,  # Need creativity for scenarios
            )
            
            # Ensure basic fields
            scenario.setdefault("role", role_data.get("role", "Unknown Role"))
            scenario.setdefault("scenario_title", "Tình huống nghiệp vụ")
            scenario.setdefault("questions", [])
            
            self.log(f"Combat scenario created: {scenario['scenario_title']} ({len(scenario['questions'])} questions)")
            return scenario
            
        except Exception as e:
            self.log(f"ERROR generating combat scenario: {e}")
            return {
                "error": str(e),
                "role": role_data.get("role"),
                "questions": []
            }
