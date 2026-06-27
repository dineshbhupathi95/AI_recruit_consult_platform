"""Authentication business logic."""

from datetime import datetime, timezone
from uuid import UUID

from jose import JWTError
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    validate_token_type,
    verify_password,
)
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    RoleResponse,
    TenantResponse,
    TokenResponse,
    UserResponse,
)

logger = get_logger(__name__)


class AuthService:
    """Service layer for authentication operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        tenant_repo: TenantRepository,
        role_repo: RoleRepository,
        refresh_token_repo: RefreshTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._tenant_repo = tenant_repo
        self._role_repo = role_repo
        self._refresh_token_repo = refresh_token_repo

    @staticmethod
    def _extract_permissions(user: User) -> list[str]:
        permissions: set[str] = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.code)
        return sorted(permissions)

    @staticmethod
    def _extract_roles(user: User) -> list[str]:
        return [role.name for role in user.roles]

    def _build_user_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            last_login_at=user.last_login_at,
            roles=[RoleResponse.model_validate(r) for r in user.roles],
            permissions=self._extract_permissions(user),
            created_at=user.created_at,
        )

    async def _issue_tokens(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        settings = get_settings()
        roles = self._extract_roles(user)
        permissions = self._extract_permissions(user)

        access_token = create_access_token(
            subject=str(user.id),
            tenant_id=user.tenant_id,
            roles=roles,
            permissions=permissions,
        )
        refresh_token, expires_at, token_hash = create_refresh_token(
            subject=str(user.id),
            tenant_id=user.tenant_id,
        )
        await self._refresh_token_repo.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def register(
        self,
        data: RegisterRequest,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponse:
        """Register a new tenant and admin user."""
        existing = await self._user_repo.get_by_email_global(data.email)
        if existing is not None:
            raise ConflictError("An account with this email already exists")

        slug = await self._tenant_repo.create_unique_slug(data.organization_name)

        try:
            tenant = await self._tenant_repo.create(
                name=data.organization_name,
                slug=slug,
                description=f"Recruitment consultancy: {data.organization_name}",
            )

            admin_role = await self._role_repo.create_tenant_admin_role(tenant.id)
            await self._role_repo.create_recruiter_role(tenant.id)

            user = await self._user_repo.create(
                tenant_id=tenant.id,
                email=data.email,
                password_hash=hash_password(data.password),
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone,
            )
            user = await self._user_repo.assign_roles(user, [admin_role])
        except IntegrityError as exc:
            raise ConflictError("Email or organization already exists") from exc

        user = await self._user_repo.get_by_id_with_roles(user.id)
        if user is None:
            raise ValidationError("Failed to create user")

        tokens = await self._issue_tokens(user, user_agent, ip_address)
        await self._user_repo.update_last_login(user.id)

        logger.info("tenant_registered", tenant_id=str(tenant.id), user_id=str(user.id))

        return AuthResponse(
            user=self._build_user_response(user),
            tenant=TenantResponse.model_validate(tenant),
            tokens=tokens,
        )

    async def login(
        self,
        data: LoginRequest,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponse:
        """Authenticate user and return tokens."""
        tenant_id: UUID | None = None
        if data.tenant_slug:
            tenant = await self._tenant_repo.get_by_slug(data.tenant_slug)
            if tenant is None:
                raise UnauthorizedError("Invalid credentials")
            tenant_id = tenant.id

        user = await self._user_repo.get_by_email(data.email, tenant_id)
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        tenant = user.tenant
        if tenant is None or not tenant.is_active or tenant.is_deleted:
            raise UnauthorizedError("Organization is inactive")

        tokens = await self._issue_tokens(user, user_agent, ip_address)
        await self._user_repo.update_last_login(user.id)

        logger.info("user_logged_in", user_id=str(user.id), tenant_id=str(user.tenant_id))

        return AuthResponse(
            user=self._build_user_response(user),
            tenant=TenantResponse.model_validate(tenant),
            tokens=tokens,
        )

    async def refresh_tokens(
        self,
        refresh_token: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """Rotate refresh token and issue new token pair."""
        try:
            payload = decode_token(refresh_token)
            validate_token_type(payload, "refresh")
            user_id = UUID(payload["sub"])
        except (JWTError, KeyError, ValueError) as exc:
            raise UnauthorizedError("Invalid refresh token") from exc

        token_hash = hash_token(refresh_token)
        stored_token = await self._refresh_token_repo.get_by_hash(token_hash)
        if stored_token is None:
            raise UnauthorizedError("Refresh token not found or revoked")

        if stored_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            await self._refresh_token_repo.revoke(stored_token)
            raise UnauthorizedError("Refresh token expired")

        user = await self._user_repo.get_by_id_with_roles(user_id)
        if user is None or not user.is_active or user.is_deleted:
            raise UnauthorizedError("User account is inactive")

        await self._refresh_token_repo.revoke(stored_token)
        return await self._issue_tokens(user, user_agent, ip_address)

    async def logout(self, refresh_token: str) -> MessageResponse:
        """Revoke a refresh token."""
        token_hash = hash_token(refresh_token)
        stored_token = await self._refresh_token_repo.get_by_hash(token_hash)
        if stored_token:
            await self._refresh_token_repo.revoke(stored_token)
        return MessageResponse(message="Logged out successfully")

    async def logout_all(self, user_id: UUID) -> MessageResponse:
        """Revoke all refresh tokens for a user."""
        await self._refresh_token_repo.revoke_all_for_user(user_id)
        return MessageResponse(message="All sessions revoked")

    async def get_current_user_profile(self, user_id: UUID) -> UserResponse:
        """Return the authenticated user's profile."""
        user = await self._user_repo.get_by_id_with_roles(user_id)
        if user is None or user.is_deleted:
            raise UnauthorizedError("User not found")
        return self._build_user_response(user)

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> MessageResponse:
        """Change user password after verifying current password."""
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("User not found")

        if not verify_password(current_password, user.password_hash):
            raise ValidationError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        await self._refresh_token_repo.revoke_all_for_user(user_id)
        return MessageResponse(message="Password changed successfully")
