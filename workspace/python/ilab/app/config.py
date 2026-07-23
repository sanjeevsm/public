import json
from pathlib import Path
from typing import Any, Dict

CONFIG_FILE = Path(__file__).parent.parent / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "ai_provider": "groq",
    "providers": {
        "claude": {
            "api_key": "",
            "model": "claude-opus-4-7",
            "base_url": "",
        },
        "openai": {
            "api_key": "",
            "model": "gpt-4o",
            "base_url": "",
        },
        "gemini": {
            "api_key": "",
            "model": "gemini-1.5-pro",
            "base_url": "",
        },
        "groq": {
            "api_key": "",
            "model": "llama-3.3-70b-versatile",
            "base_url": "",
        },
        "ollama": {
            "api_key": "",
            "model": "llama3.2",
            "base_url": "",
        },
        "xai": {
            "api_key": "",
            "model": "grok-3-mini",
            "base_url": "",
        },
    },
    "timer_seconds": 0,
    "num_questions": 10,
    "experience_level": "mid",
    "appearance_mode": "dark",
}


class Config:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f)
                merged = _deep_merge(DEFAULT_CONFIG, saved)
                return merged
            except (json.JSONDecodeError, KeyError, OSError):
                pass
        return _deep_merge({}, DEFAULT_CONFIG)

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except OSError:
            pass

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def get_provider_config(self, provider: str = None) -> Dict[str, Any]:
        if provider is None:
            provider = self._data.get("ai_provider", "claude")
        return self._data.get("providers", {}).get(provider, {})

    def set_provider_config(self, provider: str, key: str, value: Any):
        self._data.setdefault("providers", {}).setdefault(provider, {})[key] = value

    @property
    def ai_provider(self) -> str:
        return self._data.get("ai_provider", "claude")

    @property
    def timer_seconds(self) -> int:
        return int(self._data.get("timer_seconds", 30))

    @property
    def num_questions(self) -> int:
        return int(self._data.get("num_questions", 10))

    @property
    def experience_level(self) -> str:
        return self._data.get("experience_level", "mid")


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
