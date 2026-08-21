"""
Request ID Middleware.

Assigns a unique request ID to every incoming request and
binds it to the logging context.
"""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.logging.context import (
    bind_request_id,
    clear_context,
)
from app.common.logging.logger import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a request ID to every request.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = str(uuid.uuid4())

        bind_request_id(request_id)

        request.state.request_id = request_id

        started_at = time.perf_counter()

        try:
            response = await call_next(request)

        except Exception:
            logger.exception(
                "Unhandled request exception.",
                request_id=request_id,
                path=request.url.path,
            )

            clear_context()
            raise

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed.",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        clear_context()

        return response