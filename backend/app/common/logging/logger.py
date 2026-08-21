"""
Enterprise logger.

Central logger interface for the Enterprise AI Platform.
"""

from __future__ import annotations

import logging

import structlog

from app.common.logging.config import configure_logging

_CONFIGURED = False


def configure() -> None:
    """Configure logging once."""
    global _CONFIGURED

    if _CONFIGURED:
        return

    configure_logging()
    _CONFIGURED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Return a configured Structlog logger.
    """
    configure()
    return structlog.get_logger(name or "enterprise-ai-platform")


def get_stdlib_logger(name: str | None = None) -> logging.Logger:
    """
    Return a standard library logger.
    """
    configure()
    return logging.getLogger(name or "enterprise-ai-platform")


__all__ = [
    "configure",
    "get_logger",
    "get_stdlib_logger",
]