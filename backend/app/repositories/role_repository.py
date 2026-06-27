"""Role and permission repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Permission, Role
from app.repositories.base import BaseRepository


DEFAULT_PERMISSIONS: list[dict[str, str]] = [
    {"code": "users:read", "resource": "users", "action": "read", "description": "View users"},
    {"code": "users:write", "resource": "users", "action": "write", "description": "Manage users"},
    {"code": "clients:read", "resource": "clients", "action": "read", "description": "View clients"},
    {"code": "clients:write", "resource": "clients", "action": "write", "description": "Manage clients"},
    {"code": "jobs:read", "resource": "jobs", "action": "read", "description": "View job requirements"},
    {"code": "jobs:write", "resource": "jobs", "action": "write", "description": "Manage job requirements"},
    {"code": "candidates:read", "resource": "candidates", "action": "read", "description": "View candidates"},
    {"code": "candidates:write", "resource": "candidates", "action": "write", "description": "Manage candidates"},
    {"code": "interviews:read", "resource": "interviews", "action": "read", "description": "View interviews"},
    {"code": "interviews:write", "resource": "interviews", "action": "write", "description": "Manage interviews"},
    {"code": "settings:read", "resource": "settings", "action": "read", "description": "View settings"},
    {"code": "settings:write", "resource": "settings", "action": "write", "description": "Manage settings"},
    {"code": "analytics:read", "resource": "analytics", "action": "read", "description": "View analytics"},
    {"code": "audit:read", "resource": "audit", "action": "read", "description": "View audit logs"},
]


class RoleRepository(BaseRepository[Role]):
    """Data access for roles and permissions."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Role)

    async def get_by_name(self, name: str, tenant_id: UUID | None = None) -> Role | None:
        query = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == name, Role.is_deleted.is_(False))
        )
        if tenant_id is not None:
            query = query.where(Role.tenant_id == tenant_id)
        else:
            query = query.where(Role.tenant_id.is_(None))
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_permission_by_code(self, code: str) -> Permission | None:
        result = await self._session.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()

    async def ensure_default_permissions(self) -> list[Permission]:
        permissions: list[Permission] = []
        for perm_data in DEFAULT_PERMISSIONS:
            existing = await self.get_permission_by_code(perm_data["code"])
            if existing:
                permissions.append(existing)
            else:
                permission = Permission(**perm_data)
                self._session.add(permission)
                permissions.append(permission)
        await self._session.flush()
        return permissions

    async def create_tenant_admin_role(self, tenant_id: UUID) -> Role:
        permissions = await self.ensure_default_permissions()
        role = Role(
            tenant_id=tenant_id,
            name="admin",
            description="Tenant administrator with full access",
            is_system=True,
        )
        role.permissions = permissions
        return await self.add(role)

    async def create_recruiter_role(self, tenant_id: UUID) -> Role:
        permissions = await self.ensure_default_permissions()
        recruiter_codes = {
            "clients:read", "clients:write",
            "jobs:read", "jobs:write",
            "candidates:read", "candidates:write",
            "interviews:read", "interviews:write",
            "analytics:read",
        }
        role = Role(
            tenant_id=tenant_id,
            name="recruiter",
            description="Standard recruiter role",
            is_system=True,
        )
        role.permissions = [p for p in permissions if p.code in recruiter_codes]
        return await self.add(role)
