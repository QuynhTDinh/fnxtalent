"""
SurveyEvaluatorAgent — Đánh giá chất lượng survey blueprint.

Input:  Survey blueprint (from DesignerAgent)
Output: Evaluation result (scores, feedback, pass/fail)
"""

from core.agents.base_agent import BaseAgent
from core.agents.llm_client import create_llm_client
from core.agents.survey_prompts import (
    SURVEY_EVALUATOR_SYSTEM,
    build_evaluator_prompt,
)


class SurveyEvaluatorAgent(BaseAgent):
    PASS_THRESHOLD = 7.0

    def __init__(self, llm_provider="gemini", **kwargs):
        super().__init__(name="SurveyEvaluatorAgent")
        self.llm = create_llm_client(llm_provider, **kwargs)

    def handle_event(self, event_name, data):
        if event_name == "SURVEY_DESIGNED":
            return self.evaluate(data)
        return None

    def evaluate(self, blueprint: dict) -> dict:
        """Evaluate a survey blueprint for quality.

        Args:
            blueprint: Survey blueprint from DesignerAgent

        Returns:
            {
                "scores": { "clarity": 8, "completeness": 7, ... },
                "average_score": 7.8,
                "passed": true/false,
                "strengths": [...],
                "improvements": [...],
                "critical_issues": [...],
                "recommendation": "..."
            }
        """
        category = blueprint.get("category", "")
        self.log(f"Evaluating survey: {blueprint.get('title', 'N/A')}")

        user_prompt = build_evaluator_prompt(blueprint, category)
        result = self.llm.generate_json(
            system_prompt=SURVEY_EVALUATOR_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.1,  # Deterministic evaluation
        )

        # Ensure required fields
        scores = result.get("scores", {})
        score_values = [
            scores.get("clarity", 5),
            scores.get("completeness", 5),
            scores.get("bias", 5),
            scores.get("length", 5),
            scores.get("actionability", 5),
        ]
        avg = sum(score_values) / len(score_values)

        result["average_score"] = round(avg, 1)
        result["passed"] = avg >= self.PASS_THRESHOLD
        result.setdefault("strengths", [])
        result.setdefault("improvements", [])
        result.setdefault("critical_issues", [])
        result.setdefault("recommendation", "")

        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        self.log(f"Evaluation: {status} (score: {result['average_score']}/10)")

        return self.emit_event("SURVEY_EVALUATED", result)["payload"]
