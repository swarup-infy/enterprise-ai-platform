"""
Enterprise exception hierarchy.

Shared application exceptions for consistent error handling.
"""

from __future__ import annotations


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str = "Application error") -> None:
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    """Validation failure."""


class AuthenticationError(AppError):
    """Authentication failure."""


class AuthorizationError(AppError):
    """Authorization failure."""


class ResourceNotFoundError(AppError):
    """Resource not found."""


class ConflictError(AppError):
    """Resource conflict."""


class DatabaseError(AppError):
    """Database operation failed."""


class ExternalServiceError(AppError):
    """External dependency failed."""


class AIServiceError(AppError):
    """AI model/provider error."""


__all__ = [
    "AppError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "AIServiceError",
]