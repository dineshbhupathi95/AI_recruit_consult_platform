"""Unit tests for security utilities."""

from datetime import timedelta
from uuid import uuid4

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    validate_token_type,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify_password(self) -> None:
        password = "SecurePass123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPass123", hashed)


class TestAccessToken:
    def test_create_and_decode_access_token(self) -> None:
        user_id = uuid4()
        tenant_id = uuid4()
        token = create_access_token(
            subject=str(user_id),
            tenant_id=tenant_id,
            roles=["admin"],
            permissions=["users:read"],
        )
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["type"] == "access"
        assert payload["roles"] == ["admin"]

    def test_validate_token_type_rejects_wrong_type(self) -> None:
        user_id = uuid4()
        tenant_id = uuid4()
        token = create_access_token(str(user_id), tenant_id, [], [])
        payload = decode_token(token)
        with pytest.raises(JWTError):
            validate_token_type(payload, "refresh")


class TestRefreshToken:
    def test_create_refresh_token(self) -> None:
        user_id = uuid4()
        tenant_id = uuid4()
        token, expires_at, token_hash = create_refresh_token(str(user_id), tenant_id)
        assert token
        assert expires_at
        assert len(token_hash) == 64
        payload = decode_token(token)
        assert payload["type"] == "refresh"
        assert hash_token(token) == token_hash
