"""Tenant settings data access."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant_settings import TenantSettings
from app.repositories.base import BaseRepository


class TenantSettingsRepository(BaseRepository[TenantSettings]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TenantSettings)

    async def get_by_tenant(self, tenant_id: UUID) -> TenantSettings | None:
        result = await self._session.execute(
            select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, tenant_id: UUID, settings: dict, user_id: UUID | None = None) -> TenantSettings:
        existing = await self.get_by_tenant(tenant_id)
        if existing:
            existing.settings = settings
            existing.updated_by = user_id
            await self._session.flush()
            return existing
        record = TenantSettings(
            tenant_id=tenant_id,
            settings=settings,
            created_by=user_id,
            updated_by=user_id,
        )
        return await self.add(record)
