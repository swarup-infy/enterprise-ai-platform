"""
Global Exception Handlers.

Registers FastAPI exception handlers for the
Enterprise AI Platform.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.exceptions.exceptions import EnterpriseAIException
from app.common.logging.logger import get_logger

logger = get_logger(__name__)


# ==============================================================================
# Enterprise Exceptions
# ==============================================================================


async def enterprise_exception_handler(
    request: Request,
    exc: EnterpriseAIException,
) -> JSONResponse:
    logger.exception(
        exc.detail,
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "type": exc.__class__.__name__,
            "extra": exc.extra,
        },
    )


# ==============================================================================
# Validation Errors
# ==============================================================================


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "Validation failed.",
        path=request.url.path,
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed.",
            "details": exc.errors(),
        },
    )


# ==============================================================================
# Unhandled Exceptions
# ==============================================================================


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled exception.",
        path=request.url.path,
        error=str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
        },
    )


# ==============================================================================
# Register
# ==============================================================================


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register all application exception handlers.
    """

    app.add_exception_handler(
        EnterpriseAIException,
        enterprise_exception_handler,
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )