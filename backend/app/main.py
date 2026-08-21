"""
Enterprise AI Platform

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

# ==============================================================================
# Logger
# ==============================================================================

logger = get_logger(__name__)

# ==============================================================================
# FastAPI App
# ==============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Multi-Agent AI Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ==============================================================================
# Middleware
# ==============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

# ==============================================================================
# Routers
# ==============================================================================

app.include_router(
    api_router,
    prefix="/api",
)

# ==============================================================================
# Root Endpoint
# ==============================================================================

@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


# ==============================================================================
# Health Check
# ==============================================================================

@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


# ==============================================================================
# Startup Log
# ==============================================================================

logger.info(
    "Enterprise AI Platform initialized.",
    version=settings.APP_VERSION,
)