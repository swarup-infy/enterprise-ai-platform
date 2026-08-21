"""
Application lifespan management.

Handles startup and shutdown events for the Enterprise AI Platform.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.logging.logger import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage application startup and shutdown.
    """

    configure_logging()

    logger.info(
        "Starting Enterprise AI Platform."
    )

    try:
        # Startup resources will be initialized here.
        yield

    except Exception:
        logger.exception(
            "Application lifecycle error."
        )
        raise

    finally:
        # Shutdown resources will be released here.
        logger.info(
            "Shutting down Enterprise AI Platform."
        )