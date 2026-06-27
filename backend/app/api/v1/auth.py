"""Authentication API endpoints."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.dependencies import AuthServiceDep, CurrentUser
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _client_info(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


class ChangePasswordRequest(BaseModel):
    """Change password request body."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Register consultancy and admin user",
    description=(
        "Creates a new multi-tenant organization (recruitment consultancy) "
        "and registers the first admin user with full permissions."
    ),
)
async def register(
    data: RegisterRequest,
    request: Request,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    user_agent, ip_address = _client_info(request)
    return await auth_service.register(data, user_agent, ip_address)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login recruiter",
    description="Authenticate a recruiter and receive JWT access and refresh tokens.",
)
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    user_agent, ip_address = _client_info(request)
    return await auth_service.login(data, user_agent, ip_address)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access and refresh token pair.",
)
async def refresh_token(
    data: RefreshTokenRequest,
    request: Request,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    user_agent, ip_address = _client_info(request)
    return await auth_service.refresh_tokens(data.refresh_token, user_agent, ip_address)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Revoke the provided refresh token.",
)
async def logout(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    return await auth_service.logout(data.refresh_token)


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Logout all sessions",
    description="Revoke all refresh tokens for the current user.",
)
async def logout_all(
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    return await auth_service.logout_all(current_user.user_id)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Return the authenticated recruiter's profile and permissions.",
)
async def get_me(
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> UserResponse:
    return await auth_service.get_current_user_profile(current_user.user_id)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change the current user's password and revoke all active sessions.",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    return await auth_service.change_password(
        current_user.user_id,
        data.current_password,
        data.new_password,
    )
