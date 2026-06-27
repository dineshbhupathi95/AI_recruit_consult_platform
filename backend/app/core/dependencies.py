"""FastAPI dependency injection providers."""

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token, validate_token_type
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

security_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: DbSession) -> UserRepository:
    return UserRepository(session)


def get_tenant_repository(session: DbSession) -> TenantRepository:
    return TenantRepository(session)


def get_role_repository(session: DbSession) -> RoleRepository:
    return RoleRepository(session)


def get_refresh_token_repository(session: DbSession) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    tenant_repo: Annotated[TenantRepository, Depends(get_tenant_repository)],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
) -> AuthService:
    return AuthService(user_repo, tenant_repo, role_repo, refresh_token_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


class CurrentUserContext:
    """Authenticated user context extracted from JWT."""

    def __init__(
        self,
        user_id: UUID,
        tenant_id: UUID,
        email: str,
        roles: list[str],
        permissions: list[str],
    ) -> None:
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.email = email
        self.roles = roles
        self.permissions = permissions

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or "admin" in self.roles

    def require_permission(self, permission: str) -> None:
        if not self.has_permission(permission):
            raise ForbiddenError(f"Missing required permission: {permission}")


async def get_current_user_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> CurrentUserContext:
    """Extract and validate the current user from the JWT access token."""
    if credentials is None:
        raise UnauthorizedError("Authentication credentials required")

    try:
        payload = decode_token(credentials.credentials)
        validate_token_type(payload, "access")
        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])
    except (JWTError, KeyError, ValueError) as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    user = await user_repo.get_by_id(user_id)
    if user is None or user.is_deleted or not user.is_active:
        raise UnauthorizedError("User account is inactive or not found")

    if user.tenant_id != tenant_id:
        raise UnauthorizedError("Invalid tenant context")

    return CurrentUserContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
    )


CurrentUser = Annotated[CurrentUserContext, Depends(get_current_user_context)]


def require_permissions(*required_permissions: str) -> Callable[..., CurrentUserContext]:
    """Dependency factory that enforces one or more permissions."""

    async def _dependency(current_user: CurrentUser) -> CurrentUserContext:
        for permission in required_permissions:
            current_user.require_permission(permission)
        return current_user

    return _dependency


async def get_request_id(x_request_id: Annotated[str | None, Header()] = None) -> str:
    """Return request ID from header or generate a placeholder."""
    return x_request_id or "unknown"
