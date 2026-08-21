"""
Enterprise security module.

JWT authentication and password hashing utilities.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password securely."""
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its hash."""
    return password_hash.verify(
        password,
        hashed_password,
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed JWT access token."""

    now = datetime.now(UTC)

    expire = now + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "type": "access",
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""

    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token."
        ) from exc


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """Decode and validate an access token."""

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")

    if not payload.get("sub"):
        raise ValueError("Token subject is missing.")

    return payload


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "decode_access_token",
]