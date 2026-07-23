from .base_provider import BaseProvider
from .claude_provider import ClaudeProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from ..config import get_config


def get_provider(provider_name: str = None) -> BaseProvider:
    cfg = get_config()
    if provider_name is None:
        provider_name = cfg.ai_provider

    p = cfg.get_provider_config(provider_name)
    api_key = p.get("api_key", "")
    model = p.get("model", "")
    base_url = p.get("base_url", "")

    _no_key_required = {"ollama"}
    if not api_key and provider_name not in _no_key_required:
        raise ValueError(
            f"No API key configured for provider '{provider_name}'.\n"
            "Please open Settings and add your API key."
        )

    if provider_name == "claude":
        return ClaudeProvider(api_key=api_key, model=model, base_url=base_url)
    elif provider_name in ("openai", "groq", "ollama", "xai"):
        return OpenAIProvider(api_key=api_key or "ollama", model=model, base_url=base_url)
    elif provider_name == "gemini":
        return GeminiProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown AI provider: '{provider_name}'")
