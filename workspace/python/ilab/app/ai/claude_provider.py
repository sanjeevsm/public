from typing import List

from .base_provider import BaseProvider
from ..models.question import Question


class ClaudeProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "claude-opus-4-7", base_url: str = ""):
        self.api_key = api_key
        self.model = model or "claude-opus-4-7"
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = anthropic.Anthropic(**kwargs)
        return self._client

    def generate_questions(self, jd: str, experience_level: str, num_questions: int, mode: str = "jd") -> List[Question]:
        client = self._get_client()
        prompt = self._build_prompt(jd, experience_level, num_questions, mode)
        message = client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_questions(message.content[0].text)

    def test_connection(self) -> bool:
        try:
            client = self._get_client()
            client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception:
            return False
