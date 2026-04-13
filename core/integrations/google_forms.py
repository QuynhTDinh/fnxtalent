"""
Google Forms API Integration for FNX Talent Factory.

Converts survey blueprints (from SurveyDesignerAgent) into real Google Forms.

Usage:
    from core.integrations.google_forms import GoogleFormsClient

    client = GoogleFormsClient()
    result = client.create_form(blueprint)
    print(result["form_url"])  # https://docs.google.com/forms/d/e/xxx/viewform
"""

import json
from typing import Optional


# Maps our blueprint question types to Google Forms item types
QUESTION_TYPE_MAP = {
    "TEXT": "textQuestion",
    "PARAGRAPH": "textQuestion",      # paragraph=True
    "RADIO": "choiceQuestion",        # type=RADIO
    "CHECKBOX": "choiceQuestion",     # type=CHECKBOX
    "DROPDOWN": "choiceQuestion",     # type=DROP_DOWN
    "SCALE": "scaleQuestion",
}


class GoogleFormsClient:
    """Client for creating and managing Google Forms via API."""

    def __init__(self, credentials=None):
        """
        Initialize Google Forms client.

        Args:
            credentials: google.oauth2.credentials.Credentials
                        If None, will try to get from google_auth module.
        """
        self.credentials = credentials
        self._forms_service = None
        self._drive_service = None

    @property
    def forms_service(self):
        """Lazy-initialize Google Forms API service."""
        if self._forms_service is None:
            self._ensure_credentials()
            from googleapiclient.discovery import build
            self._forms_service = build(
                "forms", "v1",
                credentials=self.credentials,
                cache_discovery=False,
            )
        return self._forms_service

    @property
    def drive_service(self):
        """Lazy-initialize Google Drive API service."""
        if self._drive_service is None:
            self._ensure_credentials()
            from googleapiclient.discovery import build
            self._drive_service = build(
                "drive", "v3",
                credentials=self.credentials,
                cache_discovery=False,
            )
        return self._drive_service

    def _ensure_credentials(self):
        """Ensure credentials are available."""
        if self.credentials is None:
            from core.integrations.google_auth import get_google_credentials
            self.credentials = get_google_credentials()

    def create_form(self, blueprint: dict, folder_id: Optional[str] = None) -> dict:
        """
        Create a Google Form from a survey blueprint.

        Args:
            blueprint: Survey blueprint dict from SurveyDesignerAgent
                {
                    "title": "...",
                    "description": "...",
                    "sections": [
                        {
                            "title": "Section 1",
                            "description": "...",
                            "questions": [
                                {
                                    "text": "Question?",
                                    "type": "RADIO",
                                    "options": ["A", "B", "C"],
                                    "required": true,
                                    "helpText": "..."
                                }
                            ]
                        }
                    ]
                }
            folder_id: Optional Google Drive folder ID to move the form into

        Returns:
            {
                "form_id": "abc123",
                "form_url": "https://docs.google.com/forms/d/e/xxx/viewform",
                "edit_url": "https://docs.google.com/forms/d/xxx/edit",
                "title": "Survey Title",
                "total_questions": 15
            }
        """
        print(f"[GoogleForms] 📝 Creating form: {blueprint.get('title', 'Untitled')}")

        # Step 1: Create empty form with title
        form_body = {
            "info": {
                "title": blueprint.get("title", "FNX Survey"),
            }
        }
        form = self.forms_service.forms().create(body=form_body).execute()
        form_id = form["formId"]
        print(f"[GoogleForms] ✅ Form created: {form_id}")

        # Step 2: Build batchUpdate requests for description + questions
        requests = []

        # Add form description
        description = blueprint.get("description", "")
        if description:
            requests.append({
                "updateFormInfo": {
                    "info": {
                        "description": description,
                    },
                    "updateMask": "description",
                }
            })

        # Add questions from all sections
        item_index = 0
        for section in blueprint.get("sections", []):
            # Add section header as a text item
            section_title = section.get("title", "")
            if section_title:
                requests.append({
                    "createItem": {
                        "item": {
                            "title": section_title,
                            "description": section.get("description", ""),
                            "textItem": {},  # Section divider
                        },
                        "location": {"index": item_index},
                    }
                })
                item_index += 1

            # Add questions
            for question in section.get("questions", []):
                item_request = self._build_question_request(question, item_index)
                if item_request:
                    requests.append(item_request)
                    item_index += 1

        # Step 3: Execute batchUpdate
        if requests:
            # Google Forms API has max batch size — split if needed
            batch_size = 50
            for i in range(0, len(requests), batch_size):
                batch = requests[i:i + batch_size]
                self.forms_service.forms().batchUpdate(
                    formId=form_id,
                    body={"requests": batch},
                ).execute()
                print(f"[GoogleForms] 📦 Batch {i // batch_size + 1} applied ({len(batch)} items)")

        # Step 4: Move to folder if specified
        if folder_id:
            try:
                self._move_to_folder(form_id, folder_id)
            except Exception as e:
                print(f"[GoogleForms] ⚠️ Failed to move to folder: {e}")

        # Build result
        total_questions = sum(
            len(s.get("questions", []))
            for s in blueprint.get("sections", [])
        )

        result = {
            "form_id": form_id,
            "form_url": f"https://docs.google.com/forms/d/e/{form_id}/viewform",
            "edit_url": f"https://docs.google.com/forms/d/{form_id}/edit",
            "responder_url": form.get("responderUri", ""),
            "title": blueprint.get("title", ""),
            "total_questions": total_questions,
        }

        print(f"[GoogleForms] 🎉 Form ready: {result['edit_url']}")
        return result

    def _build_question_request(self, question: dict, index: int) -> Optional[dict]:
        """Convert a blueprint question to a Google Forms createItem request."""
        q_type = question.get("type", "TEXT").upper()
        q_text = question.get("text", "")
        required = question.get("required", False)
        help_text = question.get("helpText", "")
        options = question.get("options", [])

        item = {
            "title": q_text,
            "description": help_text,
        }

        if q_type in ("TEXT", "PARAGRAPH"):
            item["questionItem"] = {
                "question": {
                    "required": required,
                    "textQuestion": {
                        "paragraph": q_type == "PARAGRAPH",
                    },
                }
            }

        elif q_type in ("RADIO", "CHECKBOX", "DROPDOWN"):
            google_type = {
                "RADIO": "RADIO",
                "CHECKBOX": "CHECKBOX",
                "DROPDOWN": "DROP_DOWN",
            }.get(q_type, "RADIO")

            choice_options = [{"value": opt} for opt in options] if options else [{"value": "Option 1"}]

            item["questionItem"] = {
                "question": {
                    "required": required,
                    "choiceQuestion": {
                        "type": google_type,
                        "options": choice_options,
                    },
                }
            }

        elif q_type == "SCALE":
            # Google Forms scale question
            low = 1
            high = 5
            low_label = ""
            high_label = ""

            if options and len(options) >= 2:
                # Parse labels from options like "1 (Rất kém)", "5 (Xuất sắc)"
                low_label = options[0] if options else ""
                high_label = options[-1] if options else ""
                try:
                    high = len(options)
                except (ValueError, IndexError):
                    high = 5

            item["questionItem"] = {
                "question": {
                    "required": required,
                    "scaleQuestion": {
                        "low": low,
                        "high": high,
                        "lowLabel": low_label,
                        "highLabel": high_label,
                    },
                }
            }

        else:
            # Fallback to text
            item["questionItem"] = {
                "question": {
                    "required": required,
                    "textQuestion": {"paragraph": False},
                }
            }

        return {
            "createItem": {
                "item": item,
                "location": {"index": index},
            }
        }

    def _move_to_folder(self, form_id: str, folder_id: str):
        """Move a form to a specific Google Drive folder."""
        # Get current parents
        file = self.drive_service.files().get(
            fileId=form_id,
            fields="parents",
        ).execute()
        previous_parents = ",".join(file.get("parents", []))

        # Move to new folder  
        self.drive_service.files().update(
            fileId=form_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()
        print(f"[GoogleForms] 📁 Moved form to folder: {folder_id}")

    def get_form(self, form_id: str) -> dict:
        """Get form metadata."""
        return self.forms_service.forms().get(formId=form_id).execute()

    def get_responses(self, form_id: str) -> list:
        """Get all responses for a form."""
        result = self.forms_service.forms().responses().list(formId=form_id).execute()
        return result.get("responses", [])

    def get_response_count(self, form_id: str) -> int:
        """Get total number of responses."""
        responses = self.get_responses(form_id)
        return len(responses)
