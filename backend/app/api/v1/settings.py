"""Tenant settings API endpoints."""

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, TenantSettingsServiceDep
from app.schemas.settings import (
    SettingsSchemaResponse,
    TenantSettingsResponse,
    TestAIConnectionResponse,
    UpdateTenantSettingsRequest,
)

router = APIRouter(tags=["Settings"])


@router.get("/settings/schema", response_model=SettingsSchemaResponse)
async def get_settings_schema(
    current_user: CurrentUser,
    service: TenantSettingsServiceDep,
) -> SettingsSchemaResponse:
    current_user.require_permission("settings:read")
    return service.get_schema()


@router.get("/settings", response_model=TenantSettingsResponse)
async def get_settings(
    current_user: CurrentUser,
    service: TenantSettingsServiceDep,
) -> TenantSettingsResponse:
    current_user.require_permission("settings:read")
    return await service.get_settings_response(current_user.tenant_id)


@router.put("/settings", response_model=TenantSettingsResponse)
async def update_settings(
    data: UpdateTenantSettingsRequest,
    current_user: CurrentUser,
    service: TenantSettingsServiceDep,
) -> TenantSettingsResponse:
    current_user.require_permission("settings:write")
    return await service.update_settings(
        current_user.tenant_id,
        data.ai_provider,
        data.values,
        current_user.user_id,
    )


@router.post("/settings/test-ai", response_model=TestAIConnectionResponse)
async def test_ai_connection(
    current_user: CurrentUser,
    service: TenantSettingsServiceDep,
) -> TestAIConnectionResponse:
    current_user.require_permission("settings:write")
    return await service.test_ai_connection(current_user.tenant_id)
