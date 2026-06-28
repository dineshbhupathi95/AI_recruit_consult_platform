"""AI provider factory based on tenant settings or environment."""

from functools import lru_cache

from app.core.config import get_settings
from app.providers.base import AIProvider
from app.providers.factory import build_ai_provider
from app.providers.mock_provider import MockAIProvider


@lru_cache
def get_ai_provider() -> AIProvider:
    """Return the global AI provider from environment variables (fallback for tests)."""
    settings = get_settings()
    merged = {
        "ai_provider": settings.ai_provider,
        "openai_api_key": settings.openai_api_key,
        "openai_model": settings.openai_model,
        "openai_base_url": settings.openai_base_url,
        "ai_request_timeout_seconds": settings.ai_request_timeout_seconds,
    }
    if merged["ai_provider"].lower() == "mock":
        return MockAIProvider()
    return build_ai_provider(merged)
