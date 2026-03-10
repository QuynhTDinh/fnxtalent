"""
SurveyDesignerAgent — Tạo nội dung survey dựa trên yêu cầu đầu vào.

Input:  Brief dict (category, objective, target_audience, num_questions)
Output: Survey blueprint JSON (title, description, sections, questions)
"""

from core.agents.base_agent import BaseAgent
from core.agents.llm_client import create_llm_client
from core.agents.survey_prompts import (
    SURVEY_DESIGNER_SYSTEM,
    build_designer_prompt,
    build_redesign_prompt,
)


class SurveyDesignerAgent(BaseAgent):
    def __init__(self, llm_provider="gemini", **kwargs):
        super().__init__(name="SurveyDesignerAgent")
        self.llm = create_llm_client(llm_provider, **kwargs)

    def handle_event(self, event_name, data):
        if event_name == "SURVEY_REQUESTED":
            return self.design(data)
        return None

    def design(self, brief: dict) -> dict:
        """Generate a survey blueprint from a brief.

        Args:
            brief: {
                "category": "student_career" | "enterprise_hr" | "working_pro",
                "objective": "Mục tiêu khảo sát",
                "target_audience": "Mô tả đối tượng (optional)",
                "num_questions": 15,
                "additional_context": "Ghi chú thêm (optional)"
            }

        Returns:
            Survey blueprint dict with title, description, sections, questions
        """
        self.log(f"Designing survey: category={brief.get('category')}")

        user_prompt = build_designer_prompt(brief)
        blueprint = self.llm.generate_json(
            system_prompt=SURVEY_DESIGNER_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.4,  # Slightly creative
        )

        # Validate & enrich
        blueprint["category"] = brief.get("category", "general")
        blueprint.setdefault("title", "Khảo sát FNX")
        blueprint.setdefault("description", "")
        blueprint.setdefault("sections", [])

        # Count questions
        total_q = sum(
            len(section.get("questions", []))
            for section in blueprint.get("sections", [])
        )
        blueprint["total_questions"] = total_q

        self.log(f"Blueprint created: {blueprint['title']} ({total_q} questions)")

        return self.emit_event("SURVEY_DESIGNED", blueprint)["payload"]

    def redesign(self, brief: dict, feedback: dict) -> dict:
        """Redesign survey based on evaluator feedback.

        Args:
            brief: Original brief
            feedback: Evaluation result with improvements and scores

        Returns:
            New survey blueprint
        """
        self.log("Redesigning survey based on feedback...")

        user_prompt = build_redesign_prompt(brief, feedback)
        blueprint = self.llm.generate_json(
            system_prompt=SURVEY_DESIGNER_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.3,
        )

        blueprint["category"] = brief.get("category", "general")
        blueprint["revision"] = True

        total_q = sum(
            len(section.get("questions", []))
            for section in blueprint.get("sections", [])
        )
        blueprint["total_questions"] = total_q

        self.log(f"Revised blueprint: {blueprint.get('title', 'N/A')} ({total_q} questions)")

        return self.emit_event("SURVEY_REDESIGNED", blueprint)["payload"]
