"""User repository."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role, user_roles
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for users."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email_global(self, email: str) -> User | None:
        """Find user by email across all tenants."""
        result = await self._session.execute(
            select(User).where(User.email == email.lower(), User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, tenant_id: UUID | None = None) -> User | None:
        query = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.tenant),
            )
            .where(User.email == email.lower(), User.is_deleted.is_(False))
        )
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_roles(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.tenant),
            )
            .where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def email_exists_in_tenant(self, email: str, tenant_id: UUID) -> bool:
        result = await self._session.execute(
            select(User.id).where(
                User.email == email.lower(),
                User.tenant_id == tenant_id,
                User.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        tenant_id: UUID,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone: str | None = None,
        created_by: UUID | None = None,
    ) -> User:
        user = User(
            tenant_id=tenant_id,
            email=email.lower(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            created_by=created_by,
        )
        return await self.add(user)

    async def update_last_login(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            await self._session.flush()

    async def assign_roles(self, user: User, roles: list[Role]) -> User:
        await self._session.execute(delete(user_roles).where(user_roles.c.user_id == user.id))
        for role in roles:
            await self._session.execute(
                user_roles.insert().values(user_id=user.id, role_id=role.id)
            )
        await self._session.flush()
        assigned = await self.get_by_id_with_roles(user.id)
        if assigned is None:
            raise ValueError("User not found after role assignment")
        return assigned
