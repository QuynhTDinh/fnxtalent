"""
SurveyPublisherAgent — Publish evaluated survey blueprints to Google Forms.

Input:  Evaluated survey blueprint (passed quality threshold)
Output: Published Google Form URL + metadata

This agent is the final step in the survey pipeline:
    Designer → Evaluator → Publisher
"""

from core.agents.base_agent import BaseAgent
from core.integrations.google_forms import GoogleFormsClient


class SurveyPublisherAgent(BaseAgent):
    def __init__(self, credentials=None, **kwargs):
        super().__init__(name="SurveyPublisherAgent")
        self.forms_client = GoogleFormsClient(credentials=credentials)

    def handle_event(self, event_name, data):
        if event_name == "SURVEY_EVALUATED":
            evaluation = data
            if evaluation.get("passed", False):
                return self.publish(evaluation.get("blueprint", {}))
            else:
                self.log("Survey did not pass evaluation — skipping publish")
                return None
        return None

    def publish(self, blueprint: dict, folder_id: str = None) -> dict:
        """
        Publish a survey blueprint to Google Forms.

        Args:
            blueprint: Survey blueprint dict (title, sections, questions)
            folder_id: Optional Google Drive folder ID

        Returns:
            {
                "status": "published",
                "form_id": "...",
                "form_url": "https://docs.google.com/forms/d/e/.../viewform",
                "edit_url": "https://docs.google.com/forms/d/.../edit",
                "responder_url": "...",
                "title": "...",
                "total_questions": 15,
                "category": "student_career"
            }
        """
        title = blueprint.get("title", "FNX Survey")
        category = blueprint.get("category", "general")
        self.log(f"Publishing survey: {title} (category: {category})")

        try:
            result = self.forms_client.create_form(blueprint, folder_id=folder_id)

            publish_result = {
                "status": "published",
                "form_id": result["form_id"],
                "form_url": result["form_url"],
                "edit_url": result["edit_url"],
                "responder_url": result.get("responder_url", ""),
                "title": result["title"],
                "total_questions": result["total_questions"],
                "category": category,
            }

            self.log(f"✅ Published successfully: {result['edit_url']}")
            return self.emit_event("SURVEY_PUBLISHED", publish_result)["payload"]

        except Exception as e:
            error_result = {
                "status": "failed",
                "error": str(e),
                "title": title,
                "category": category,
            }
            self.log(f"❌ Publish failed: {e}")
            return self.emit_event("SURVEY_PUBLISH_FAILED", error_result)["payload"]

    def get_form_info(self, form_id: str) -> dict:
        """Get metadata for a published form."""
        return self.forms_client.get_form(form_id)

    def get_responses(self, form_id: str) -> dict:
        """Get responses for a published form."""
        responses = self.forms_client.get_responses(form_id)
        return {
            "form_id": form_id,
            "total_responses": len(responses),
            "responses": responses,
        }
