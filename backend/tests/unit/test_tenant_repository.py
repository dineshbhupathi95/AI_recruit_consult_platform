"""Unit tests for tenant repository."""

import pytest

from app.repositories.tenant_repository import TenantRepository


class TestTenantRepository:
    @pytest.mark.asyncio
    async def test_generate_slug(self) -> None:
        assert TenantRepository.generate_slug("Acme Recruiters Inc.") == "acme-recruiters-inc"

    @pytest.mark.asyncio
    async def test_create_unique_slug(self, db_session) -> None:
        repo = TenantRepository(db_session)
        await repo.create(name="Acme Corp", slug="acme-corp")
        slug = await repo.create_unique_slug("Acme Corp")
        assert slug == "acme-corp-1"
