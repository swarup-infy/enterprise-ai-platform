"""
API package.

Exports shared FastAPI dependencies and the main API router.
"""

from .deps import (
    AdminUser,
    CurrentUser,
    DBSession,
    get_current_user,
    require_admin,
)
from .router import api_router

__all__ = [
    "DBSession",
    "CurrentUser",
    "AdminUser",
    "get_current_user",
    "require_admin",
    "api_router",
]