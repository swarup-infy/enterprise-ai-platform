"""
API Router.

Registers all API routes for the
Enterprise Multi-Agent AI Platform.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.chat_history import router as chat_history_router
from app.api.v1.documents import router as documents_router
from app.api.v1.users import router as users_router


api_router = APIRouter()


# ==============================================================================
# Health
# ==============================================================================

@api_router.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
)
async def health_check() -> dict[str, str]:
    """Verify that the API is running."""

    return {
        "status": "healthy",
        "service": "Enterprise AI Platform",
    }


# ==============================================================================
# Authentication
# ==============================================================================

for route in auth_router.routes:
    api_router.routes.append(route)


# ==============================================================================
# Users
# ==============================================================================

for route in users_router.routes:
    api_router.routes.append(route)


# ==============================================================================
# Documents
# ==============================================================================

for route in documents_router.routes:
    api_router.routes.append(route)


# ==============================================================================
# Chat
# ==============================================================================

for route in chat_router.routes:
    api_router.routes.append(route)


# ==============================================================================
# Chat History
# ==============================================================================

for route in chat_history_router.routes:
    api_router.routes.append(route)


__all__ = ["api_router"]