"""
Standard API Response Models.

Reusable response schemas for the Enterprise AI Platform.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ==============================================================================
# Base Response
# ==============================================================================


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response.
    """

    success: bool = True

    message: str = "Success"

    data: T | None = None

    meta: dict[str, Any] | None = None


# ==============================================================================
# Error Response
# ==============================================================================


class ErrorResponse(BaseModel):
    """
    Standard error response.
    """

    success: bool = False

    error: str

    code: int

    details: dict[str, Any] | None = None


# ==============================================================================
# Pagination
# ==============================================================================


class Pagination(BaseModel):
    page: int = Field(ge=1)

    page_size: int = Field(ge=1)

    total_items: int

    total_pages: int


class PaginatedResponse(APIResponse[list[T]], Generic[T]):
    pagination: Pagination


# ==============================================================================
# Health
# ==============================================================================


class HealthResponse(BaseModel):
    status: str

    version: str

    environment: str


# ==============================================================================
# Message
# ==============================================================================


class MessageResponse(BaseModel):
    success: bool = True

    message: str