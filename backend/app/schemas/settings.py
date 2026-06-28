"""Pydantic schemas for tenant settings API."""

from typing import Any, Literal

from pydantic import BaseModel, Field

FieldType = Literal["text", "password", "url", "number", "select"]


class SettingFieldSchema(BaseModel):
    key: str
    label: str
    type: FieldType
    required: bool = False
    default: str | int | None = None
    placeholder: str | None = None
    env_var: str | None = None
    options: list[dict[str, str]] | None = None


class AIProviderSchema(BaseModel):
    id: str
    label: str
    description: str
    env_prefix: str
    fields: list[SettingFieldSchema]


class SettingsSchemaResponse(BaseModel):
    ai_providers: list[AIProviderSchema]
    common_ai_fields: list[SettingFieldSchema]
    secret_mask: str = "********"


class SettingValueResponse(BaseModel):
    key: str
    value: str | int | None
    is_set: bool = False
    is_secret: bool = False
    source: Literal["tenant", "environment", "default"] = "default"


class TenantSettingsResponse(BaseModel):
    ai_provider: str
    values: list[SettingValueResponse]
    updated_at: str | None = None


class UpdateTenantSettingsRequest(BaseModel):
    ai_provider: str = Field(..., min_length=1, max_length=50)
    values: dict[str, Any] = Field(default_factory=dict)


class TestAIConnectionResponse(BaseModel):
    success: bool
    message: str
    provider: str
