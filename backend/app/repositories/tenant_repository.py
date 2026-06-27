"""Tenant repository."""

import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Data access for tenants."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Tenant)

    async def get_by_slug(self, slug: str) -> Tenant | None:
        result = await self._session.execute(
            select(Tenant).where(Tenant.slug == slug, Tenant.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        tenant = await self.get_by_slug(slug)
        return tenant is not None

    @staticmethod
    def generate_slug(name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_-]+", "-", slug)
        return slug[:100]

    async def create_unique_slug(self, name: str) -> str:
        base_slug = self.generate_slug(name)
        slug = base_slug
        counter = 1
        while await self.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    async def create(
        self,
        name: str,
        slug: str,
        description: str | None = None,
        created_by: UUID | None = None,
    ) -> Tenant:
        tenant = Tenant(
            name=name,
            slug=slug,
            description=description,
            created_by=created_by,
        )
        return await self.add(tenant)
