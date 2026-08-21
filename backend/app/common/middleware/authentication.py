"""
Authentication Middleware.

Authenticates incoming JWT Bearer tokens and attaches the
authenticated user to the request state.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.logging.context import bind_user_id
from app.common.logging.logger import get_logger
from app.core.security import decode_access_token

logger = get_logger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication middleware.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request.state.user = None

        authorization = request.headers.get("Authorization")

        if authorization and authorization.startswith("Bearer "):

            token = authorization.removeprefix(
                "Bearer "
            ).strip()

            try:
                payload = decode_access_token(token)

                request.state.user = payload

                if "sub" in payload:
                    bind_user_id(payload["sub"])

            except JWTError:

                logger.warning(
                    "Invalid JWT token.",
                    path=request.url.path,
                )

                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "Invalid or expired token.",
                    },
                )

            except Exception as exc:

                logger.exception(
                    "Authentication middleware failed.",
                    error=str(exc),
                )

                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": "Authentication failed.",
                    },
                )

        return await call_next(request)