"""
Enterprise AI Platform.

Main FastAPI application entrypoint.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.common.logging.logger import get_logger
from app.common.logging.middleware import LoggingMiddleware
from app.core.config import settings
from app.core.lifespan import lifespan


logger = get_logger(__name__)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json"
        if not settings.is_production
        else None,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=["Authorization", "Content-Type"],
    )

    application.add_middleware(LoggingMiddleware)

    application.include_router(
        api_router,
        prefix="/api",
    )

    @application.get(
        "/",
        tags=["System"],
        summary="Application information",
    )
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT.value,
            "status": "running",
        }

    @application.get(
        "/health",
        tags=["System"],
        summary="Application health check",
    )
    async def health() -> dict[str, str]:
        return {
            "status": "healthy",
        }

    @application.get(
        "/ready",
        tags=["System"],
        summary="Application readiness check",
    )
    async def readiness() -> dict[str, str]:
        return {
            "status": "ready",
        }

    return application


app = create_application()


logger.info(
    "Enterprise AI Platform initialized.",
    version=settings.APP_VERSION,
    environment=settings.ENVIRONMENT.value,
)