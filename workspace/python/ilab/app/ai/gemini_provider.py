from typing import List

from .base_provider import BaseProvider
from ..models.question import Question


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", base_url: str = ""):
        self.api_key = api_key
        self.model = model or "gemini-1.5-pro"
        self._client = None

    def _get_client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client

    def generate_questions(self, jd: str, experience_level: str, num_questions: int, mode: str = "jd") -> List[Question]:
        model = self._get_client()
        prompt = self._build_prompt(jd, experience_level, num_questions, mode)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": 8192},
        )
        return self._parse_questions(response.text)

    def test_connection(self) -> bool:
        try:
            model = self._get_client()
            model.generate_content("Hi", generation_config={"max_output_tokens": 5})
            return True
        except Exception:
            return False
