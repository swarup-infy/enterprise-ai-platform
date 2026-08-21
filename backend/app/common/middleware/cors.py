"""
CORS Middleware Configuration.

Configures Cross-Origin Resource Sharing for the
Enterprise AI Platform.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS for the application.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )