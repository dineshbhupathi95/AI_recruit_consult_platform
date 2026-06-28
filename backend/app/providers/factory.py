"""Build AI providers from resolved configuration."""

from typing import Any

from app.core.exceptions import ValidationError
from app.providers.base import AIProvider
from app.providers.mock_provider import MockAIProvider
from app.providers.openai_provider import OpenAIProvider
from app.services.tenant_settings_service import ResolvedAIConfig, TenantSettingsService


def build_ai_provider(merged: dict[str, Any]) -> AIProvider:
    """Create an AI provider from merged tenant/env settings."""
    service = TenantSettingsService.__new__(TenantSettingsService)
    config = service.resolve_ai_config(merged)
    return service.create_ai_provider(config)


def build_ai_provider_from_config(config: ResolvedAIConfig) -> AIProvider:
    service = TenantSettingsService.__new__(TenantSettingsService)
    return service.create_ai_provider(config)
