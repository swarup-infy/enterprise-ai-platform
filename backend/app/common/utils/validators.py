"""
Validation Utilities.

Common validation helpers used across the Enterprise AI Platform.
"""

from __future__ import annotations

import re
from pathlib import Path


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

USERNAME_PATTERN = re.compile(
    r"^[A-Za-z0-9_]{3,50}$"
)


def is_valid_email(email: str) -> bool:
    """Validate an email address."""
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def is_valid_username(username: str) -> bool:
    """Validate a username."""
    return bool(USERNAME_PATTERN.fullmatch(username.strip()))


def is_valid_password(password: str) -> bool:
    """Validate basic password requirements."""
    return (
        len(password) >= 8
        and len(password) <= 128
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
    )


def is_allowed_extension(
    filename: str,
    allowed_extensions: set[str],
) -> bool:
    """Check whether a filename has an allowed extension."""
    return Path(filename).suffix.lower() in {
        extension.lower()
        for extension in allowed_extensions
    }


def validate_file_size(
    size: int,
    max_size: int,
) -> bool:
    """Check whether a file is within the allowed size."""
    return 0 <= size <= max_size


def is_non_empty(value: str | None) -> bool:
    """Check whether a string contains meaningful content."""
    return bool(value and value.strip())


def validate_pagination(
    page: int,
    page_size: int,
    max_page_size: int = 100,
) -> tuple[int, int]:
    """Validate pagination values."""
    if page < 1:
        raise ValueError("Page must be greater than or equal to 1.")

    if page_size < 1:
        raise ValueError("Page size must be greater than or equal to 1.")

    if page_size > max_page_size:
        raise ValueError(
            f"Page size cannot exceed {max_page_size}."
        )

    return page, page_size