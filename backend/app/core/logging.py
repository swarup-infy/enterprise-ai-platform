"""
Enterprise logging compatibility module.

Re-exports the centralized logging API for application components.
"""

from __future__ import annotations

from app.common.logging.context import (
    bind_agent_id,
    bind_request_id,
    bind_user_id,
    clear_context,
)
from app.common.logging.decorators import log_execution_time
from app.common.logging.logger import (
    configure_logging,
    get_logger,
)

__all__ = [
    "configure_logging",
    "get_logger",
    "bind_request_id",
    "bind_user_id",
    "bind_agent_id",
    "clear_context",
    "log_execution_time",
]