from typing import List

from .base_provider import BaseProvider
from ..models.question import Question


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = ""):
        self.api_key = api_key
        self.model = model or "gpt-4o"
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def generate_questions(self, jd: str, experience_level: str, num_questions: int, mode: str = "jd") -> List[Question]:
        client = self._get_client()
        prompt = self._build_prompt(jd, experience_level, num_questions, mode)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer. Always return only valid JSON arrays.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=8192,
        )
        return self._parse_questions(response.choices[0].message.content)

    def test_connection(self) -> bool:
        try:
            client = self._get_client()
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
            )
            return True
        except Exception:
            return False
