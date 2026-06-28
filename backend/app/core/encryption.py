"""Encrypt tenant secrets at rest using the application secret key."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

_ENCRYPTED_PREFIX = "enc:"


def _fernet() -> Fernet:
    digest = hashlib.sha256(get_settings().app_secret_key.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(value: str) -> str:
    token = _fernet().encrypt(value.encode()).decode()
    return f"{_ENCRYPTED_PREFIX}{token}"


def decrypt_value(value: str) -> str:
    if not value.startswith(_ENCRYPTED_PREFIX):
        return value
    token = value[len(_ENCRYPTED_PREFIX) :]
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt stored secret") from exc


def is_encrypted(value: str) -> bool:
    return value.startswith(_ENCRYPTED_PREFIX)
