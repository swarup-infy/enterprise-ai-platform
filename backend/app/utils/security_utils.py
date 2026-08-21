"""
Security Utilities.

Common security helper functions.
"""

from __future__ import annotations

import hashlib
import secrets
import string
from pathlib import Path


# ==============================================================================
# SHA256
# ==============================================================================


def sha256(data: bytes) -> str:
    """
    Generate SHA256 hash.
    """

    return hashlib.sha256(data).hexdigest()


# ==============================================================================
# File Hash
# ==============================================================================


def file_sha256(path: str | Path) -> str:
    """
    Calculate SHA256 for a file.
    """

    digest = hashlib.sha256()

    with open(path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


# ==============================================================================
# Random Token
# ==============================================================================


def generate_token(
    length: int = 32,
) -> str:
    """
    Generate a cryptographically secure token.
    """

    alphabet = (
        string.ascii_letters +
        string.digits
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


# ==============================================================================
# API Key
# ==============================================================================


def generate_api_key() -> str:
    """
    Generate an API key.
    """

    return secrets.token_urlsafe(48)


# ==============================================================================
# Secure Filename
# ==============================================================================


def secure_filename(filename: str) -> str:
    """
    Remove unsafe filename characters.
    """

    allowed = (
        string.ascii_letters +
        string.digits +
        "._-"
    )

    return "".join(
        c if c in allowed else "_"
        for c in filename
    )


# ==============================================================================
# Constant-Time Compare
# ==============================================================================


def safe_compare(
    value1: str,
    value2: str,
) -> bool:
    """
    Constant-time string comparison.
    """

    return secrets.compare_digest(
        value1,
        value2,
    )


# ==============================================================================
# Random Password
# ==============================================================================


def generate_password(
    length: int = 20,
) -> str:
    """
    Generate a secure random password.
    """

    alphabet = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*()-_=+"
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )