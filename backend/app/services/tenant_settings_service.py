"""Resolve tenant AI configuration and build provider instances."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.config.ai_providers import (
    AI_PROVIDER_DEFINITIONS,
    COMMON_AI_FIELDS,
    SECRET_FIELD_TYPES,
    all_secret_keys,
    get_provider_definition,
)
from app.core.config import Settings, get_settings
from app.core.encryption import decrypt_value, encrypt_value
from app.core.exceptions import ValidationError
from app.providers.base import AIProvider
from app.providers.mock_provider import MockAIProvider
from app.providers.openai_provider import OpenAIProvider
from app.repositories.tenant_settings_repository import TenantSettingsRepository
from app.schemas.settings import (
    AIProviderSchema,
    SettingFieldSchema,
    SettingValueResponse,
    SettingsSchemaResponse,
    TenantSettingsResponse,
    TestAIConnectionResponse,
)

SECRET_MASK = "********"


@dataclass
class ResolvedAIConfig:
    provider: str
    api_key: str | None
    model: str
    base_url: str
    timeout: float
    azure_api_version: str | None = None
    require_auth: bool = True
    use_json_response_format: bool = True


class TenantSettingsService:
    """Manage tenant settings with env fallbacks and encrypted secrets."""

    def __init__(self, repo: TenantSettingsRepository) -> None:
        self._repo = repo

    def get_schema(self) -> SettingsSchemaResponse:
        providers = [
            AIProviderSchema(
                id=p["id"],
                label=p["label"],
                description=p["description"],
                env_prefix=p["env_prefix"],
                fields=[SettingFieldSchema(**f) for f in p["fields"]],
            )
            for p in AI_PROVIDER_DEFINITIONS
        ]
        common = [SettingFieldSchema(**f) for f in COMMON_AI_FIELDS]
        return SettingsSchemaResponse(ai_providers=providers, common_ai_fields=common)

    def _env_defaults(self, settings: Settings) -> dict[str, Any]:
        return {
            "ai_provider": settings.ai_provider,
            "openai_api_key": settings.openai_api_key,
            "openai_model": settings.openai_model,
            "openai_base_url": settings.openai_base_url,
            "gemini_api_key": settings.gemini_api_key,
            "gemini_model": settings.gemini_model,
            "gemini_base_url": settings.gemini_base_url,
            "groq_api_key": settings.groq_api_key,
            "groq_model": settings.groq_model,
            "groq_base_url": settings.groq_base_url,
            "ollama_base_url": settings.ollama_base_url,
            "ollama_model": settings.ollama_model,
            "ollama_api_key": settings.ollama_api_key,
            "ai_request_timeout_seconds": settings.ai_request_timeout_seconds,
        }

    def _field_definitions(self, provider_id: str) -> list[dict[str, Any]]:
        provider = get_provider_definition(provider_id)
        if provider is None:
            return []
        return list(provider["fields"]) + list(COMMON_AI_FIELDS)

    def _decrypt_settings(self, raw: dict[str, Any]) -> dict[str, Any]:
        secret_keys = all_secret_keys()
        result: dict[str, Any] = {}
        for key, value in raw.items():
            if key in secret_keys and isinstance(value, str) and value:
                result[key] = decrypt_value(value)
            else:
                result[key] = value
        return result

    def _encrypt_settings(self, values: dict[str, Any]) -> dict[str, Any]:
        secret_keys = all_secret_keys()
        result: dict[str, Any] = {}
        for key, value in values.items():
            if key in secret_keys and isinstance(value, str) and value:
                result[key] = encrypt_value(value)
            else:
                result[key] = value
        return result

    async def get_raw_settings(self, tenant_id: UUID) -> dict[str, Any]:
        record = await self._repo.get_by_tenant(tenant_id)
        if record is None:
            return {}
        return self._decrypt_settings(record.settings)

    async def get_merged_settings(self, tenant_id: UUID) -> dict[str, Any]:
        env = self._env_defaults(get_settings())
        tenant = await self.get_raw_settings(tenant_id)
        merged = {**env, **{k: v for k, v in tenant.items() if v is not None and v != ""}}
        return merged

    async def get_settings_response(self, tenant_id: UUID) -> TenantSettingsResponse:
        env = get_settings()
        env_defaults = self._env_defaults(env)
        tenant_raw = await self.get_raw_settings(tenant_id)
        record = await self._repo.get_by_tenant(tenant_id)

        provider_id = str(tenant_raw.get("ai_provider") or env_defaults["ai_provider"])
        fields = self._field_definitions(provider_id)
        secret_keys = all_secret_keys()

        values: list[SettingValueResponse] = []
        for field in fields:
            key = field["key"]
            is_secret = field["type"] in SECRET_FIELD_TYPES
            tenant_val = tenant_raw.get(key)
            env_val = env_defaults.get(key)

            if tenant_val is not None and tenant_val != "":
                display = SECRET_MASK if is_secret else tenant_val
                values.append(
                    SettingValueResponse(
                        key=key, value=display, is_set=True, is_secret=is_secret, source="tenant"
                    )
                )
            elif env_val is not None and env_val != "":
                display = SECRET_MASK if is_secret else env_val
                values.append(
                    SettingValueResponse(
                        key=key, value=display, is_set=True, is_secret=is_secret, source="environment"
                    )
                )
            else:
                default = field.get("default")
                values.append(
                    SettingValueResponse(
                        key=key,
                        value=default,
                        is_set=False,
                        is_secret=is_secret,
                        source="default",
                    )
                )

        return TenantSettingsResponse(
            ai_provider=provider_id,
            values=values,
            updated_at=record.updated_at.isoformat() if record else None,
        )

    async def update_settings(
        self, tenant_id: UUID, ai_provider: str, values: dict[str, Any], user_id: UUID
    ) -> TenantSettingsResponse:
        if get_provider_definition(ai_provider) is None:
            raise ValidationError(f"Unsupported AI provider: {ai_provider}")

        existing = await self.get_raw_settings(tenant_id)
        fields = self._field_definitions(ai_provider)
        merged: dict[str, Any] = dict(existing)
        merged["ai_provider"] = ai_provider

        for field in fields:
            key = field["key"]
            if key not in values:
                continue
            incoming = values[key]
            if field["type"] in SECRET_FIELD_TYPES:
                if incoming in (None, "", SECRET_MASK):
                    continue
                merged[key] = str(incoming)
            elif incoming is not None and incoming != "":
                merged[key] = incoming

        stored = self._encrypt_settings(merged)
        await self._repo.upsert(tenant_id, stored, user_id)
        return await self.get_settings_response(tenant_id)

    def resolve_ai_config(self, merged: dict[str, Any]) -> ResolvedAIConfig:
        provider = str(merged.get("ai_provider", "openai")).lower()
        timeout = float(merged.get("ai_request_timeout_seconds") or 120)

        if provider == "mock":
            return ResolvedAIConfig(provider="mock", api_key=None, model="", base_url="", timeout=timeout)

        if provider == "openai":
            return ResolvedAIConfig(
                provider=provider,
                api_key=merged.get("openai_api_key"),
                model=str(merged.get("openai_model") or "gpt-4o-mini"),
                base_url=str(merged.get("openai_base_url") or "https://api.openai.com/v1").rstrip("/"),
                timeout=timeout,
            )

        if provider == "azure_openai":
            endpoint = str(merged.get("azure_openai_endpoint") or "").rstrip("/")
            deployment = str(merged.get("azure_openai_deployment") or "")
            api_version = str(merged.get("azure_openai_api_version") or "2024-02-15-preview")
            base_url = f"{endpoint}/openai/deployments/{deployment}"
            return ResolvedAIConfig(
                provider=provider,
                api_key=merged.get("azure_openai_api_key"),
                model=deployment,
                base_url=base_url,
                timeout=timeout,
                azure_api_version=api_version,
            )

        if provider == "deepseek":
            return ResolvedAIConfig(
                provider=provider,
                api_key=merged.get("deepseek_api_key"),
                model=str(merged.get("deepseek_model") or "deepseek-chat"),
                base_url=str(merged.get("deepseek_base_url") or "https://api.deepseek.com/v1").rstrip("/"),
                timeout=timeout,
            )

        if provider == "groq":
            return ResolvedAIConfig(
                provider=provider,
                api_key=merged.get("groq_api_key"),
                model=str(merged.get("groq_model") or "llama-3.1-8b-instant"),
                base_url=str(merged.get("groq_base_url") or "https://api.groq.com/openai/v1").rstrip("/"),
                timeout=timeout,
            )

        if provider == "gemini":
            return ResolvedAIConfig(
                provider=provider,
                api_key=merged.get("gemini_api_key"),
                model=str(merged.get("gemini_model") or "gemini-2.0-flash"),
                base_url=str(
                    merged.get("gemini_base_url")
                    or "https://generativelanguage.googleapis.com/v1beta/openai"
                ).rstrip("/"),
                timeout=timeout,
            )

        if provider == "ollama":
            return ResolvedAIConfig(
                provider=provider,
                api_key=merged.get("ollama_api_key"),
                model=str(merged.get("ollama_model") or "llama3.2"),
                base_url=str(merged.get("ollama_base_url") or "http://localhost:11434/v1").rstrip("/"),
                timeout=timeout,
                require_auth=bool(merged.get("ollama_api_key")),
                use_json_response_format=False,
            )

        raise ValidationError(f"Unsupported AI provider: {provider}")

    def create_ai_provider(self, config: ResolvedAIConfig) -> AIProvider:
        if config.provider == "mock":
            return MockAIProvider()

        if config.require_auth and not config.api_key:
            raise ValidationError(
                f"AI provider '{config.provider}' is not configured. "
                "Set credentials in Settings or environment variables."
            )

        api_key = config.api_key or "local"

        if config.provider == "azure_openai" and config.azure_api_version:
            return OpenAIProvider(
                api_key=api_key,
                model=config.model,
                base_url=config.base_url,
                timeout=config.timeout,
                azure_api_version=config.azure_api_version,
                use_api_key_header=True,
                require_auth=config.require_auth,
                use_json_response_format=config.use_json_response_format,
            )

        return OpenAIProvider(
            api_key=api_key,
            model=config.model,
            base_url=config.base_url,
            timeout=config.timeout,
            require_auth=config.require_auth,
            use_json_response_format=config.use_json_response_format,
        )

    async def get_ai_provider(self, tenant_id: UUID) -> AIProvider:
        merged = await self.get_merged_settings(tenant_id)
        config = self.resolve_ai_config(merged)
        return self.create_ai_provider(config)

    async def test_ai_connection(self, tenant_id: UUID) -> TestAIConnectionResponse:
        try:
            merged = await self.get_merged_settings(tenant_id)
            config = self.resolve_ai_config(merged)
            if config.provider == "mock":
                return TestAIConnectionResponse(
                    success=True, message="Mock provider is always available", provider=config.provider
                )
            provider = self.create_ai_provider(config)
            await provider.parse_resume("Test resume: Jane Doe, Python developer.")
            return TestAIConnectionResponse(
                success=True,
                message="AI provider connection successful",
                provider=config.provider,
            )
        except Exception as exc:
            merged = await self.get_merged_settings(tenant_id)
            provider = str(merged.get("ai_provider", "unknown"))
            return TestAIConnectionResponse(success=False, message=str(exc), provider=provider)
