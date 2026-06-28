"""Security utilities for password hashing and JWT tokens."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    subject: str,
    tenant_id: UUID,
    roles: list[str],
    permissions: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "tenant_id": str(tenant_id),
        "roles": roles,
        "permissions": permissions,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, tenant_id: UUID) -> tuple[str, datetime, str]:
    """Create a JWT refresh token and return token, expiry, and token hash."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    jti = secrets.token_urlsafe(32)
    payload: dict[str, Any] = {
        "sub": subject,
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    token_hash = hash_token(token)
    return token, expire, token_hash


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def hash_token(token: str) -> str:
    """Create a SHA-256 hash of a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def validate_token_type(payload: dict[str, Any], expected_type: str) -> None:
    """Ensure the token payload has the expected type."""
    if payload.get("type") != expected_type:
        raise JWTError("Invalid token type")
