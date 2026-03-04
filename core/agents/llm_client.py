"""
FNX LLM Client - Centralized LLM integration for all Python agents.
Supports Google Gemini (primary) and OpenAI GPT (fallback).
"""

import json
import os
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        pass

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> dict:
        """Generate and parse a JSON response from the LLM."""
        raw = self.generate(system_prompt, user_prompt, temperature)
        return self._extract_json(raw)

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Robustly extract JSON from LLM output (handles markdown fences)."""
        cleaned = text.strip()

        # Strip markdown code fences if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to find JSON object/array in the text
            for start_char, end_char in [("{", "}"), ("[", "]")]:
                start = cleaned.find(start_char)
                end = cleaned.rfind(end_char)
                if start != -1 and end != -1 and end > start:
                    try:
                        return json.loads(cleaned[start:end + 1])
                    except json.JSONDecodeError:
                        continue
            raise ValueError(f"Could not parse JSON from LLM response: {e}\nRaw: {text[:500]}")


class GeminiClient(LLMClient):
    """Google Gemini API client."""

    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash"):
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai package is required. Install with: pip install google-genai"
            )

        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it as environment variable or pass directly."
            )

        self.model_name = model
        self.client = genai.Client(api_key=self.api_key)
        print(f"[LLM] Gemini client initialized (model: {self.model_name})")

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        from google.genai import types

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=4096,
            ),
        )
        return response.text


class OpenAIClient(LLMClient):
    """OpenAI GPT API client."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Set it as environment variable or pass directly."
            )

        self.model_name = model
        self.client = OpenAI(api_key=self.api_key)
        print(f"[LLM] OpenAI client initialized (model: {self.model_name})")

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=4096,
        )
        return response.choices[0].message.content


def create_llm_client(provider: str = "gemini", **kwargs) -> LLMClient:
    """Factory function to create an LLM client.
    
    Args:
        provider: "gemini" or "openai"
        **kwargs: Additional arguments passed to the client constructor
    """
    providers = {
        "gemini": GeminiClient,
        "openai": OpenAIClient,
    }
    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")
    return providers[provider](**kwargs)
