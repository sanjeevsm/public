from .base_provider import BaseProvider
from .claude_provider import ClaudeProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from ..config import get_config

_NO_KEY_REQUIRED = {"ollama"}


def _build_provider(provider_name: str, api_key: str, model: str, base_url: str) -> BaseProvider:
    if not api_key and provider_name not in _NO_KEY_REQUIRED:
        raise ValueError(
            f"No API key provided for provider '{provider_name}'.\n"
            "Please configure your API key in Settings."
        )
    if provider_name == "claude":
        return ClaudeProvider(api_key=api_key, model=model, base_url=base_url)
    elif provider_name in ("openai", "groq", "ollama", "xai"):
        return OpenAIProvider(api_key=api_key or "ollama", model=model, base_url=base_url)
    elif provider_name == "gemini":
        return GeminiProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown AI provider: '{provider_name}'")


def get_provider(provider_name: str = None) -> BaseProvider:
    """Desktop mode: reads credentials from config.json."""
    cfg = get_config()
    if provider_name is None:
        provider_name = cfg.ai_provider
    p = cfg.get_provider_config(provider_name)
    return _build_provider(provider_name, p.get("api_key", ""), p.get("model", ""), p.get("base_url", ""))


def get_provider_with_creds(provider_name: str, api_key: str, model: str = "", base_url: str = "") -> BaseProvider:
    """Web mode: credentials supplied per-request from the browser (never stored server-side)."""
    return _build_provider(provider_name, api_key, model, base_url)
