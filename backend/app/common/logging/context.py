"""
Logging Context Management.

Request-scoped context using contextvars and structlog.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
    get_contextvars,
)

_request_id: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)

_user_id: ContextVar[str | None] = ContextVar(
    "user_id",
    default=None,
)

_agent_id: ContextVar[str | None] = ContextVar(
    "agent_id",
    default=None,
)

_workflow_id: ContextVar[str | None] = ContextVar(
    "workflow_id",
    default=None,
)

_task_id: ContextVar[str | None] = ContextVar(
    "task_id",
    default=None,
)

_project_id: ContextVar[str | None] = ContextVar(
    "project_id",
    default=None,
)

_document_id: ContextVar[str | None] = ContextVar(
    "document_id",
    default=None,
)

_chat_id: ContextVar[str | None] = ContextVar(
    "chat_id",
    default=None,
)

_session_id: ContextVar[str | None] = ContextVar(
    "session_id",
    default=None,
)

_trace_id: ContextVar[str | None] = ContextVar(
    "trace_id",
    default=None,
)


def bind_request_id(request_id: str) -> None:
    _request_id.set(request_id)
    bind_contextvars(request_id=request_id)


def get_request_id() -> str | None:
    return _request_id.get()


def bind_user_id(user_id: str | int) -> None:
    value = str(user_id)
    _user_id.set(value)
    bind_contextvars(user_id=value)


def get_user_id() -> str | None:
    return _user_id.get()


def bind_agent_id(agent_id: str) -> None:
    _agent_id.set(agent_id)
    bind_contextvars(agent_id=agent_id)


def get_agent_id() -> str | None:
    return _agent_id.get()


def bind_workflow_id(workflow_id: str) -> None:
    _workflow_id.set(workflow_id)
    bind_contextvars(workflow_id=workflow_id)


def get_workflow_id() -> str | None:
    return _workflow_id.get()


def bind_task_id(task_id: str) -> None:
    _task_id.set(task_id)
    bind_contextvars(task_id=task_id)


def get_task_id() -> str | None:
    return _task_id.get()


def bind_project_id(project_id: str) -> None:
    _project_id.set(project_id)
    bind_contextvars(project_id=project_id)


def get_project_id() -> str | None:
    return _project_id.get()


def bind_document_id(document_id: str) -> None:
    _document_id.set(document_id)
    bind_contextvars(document_id=document_id)


def get_document_id() -> str | None:
    return _document_id.get()


def bind_chat_id(chat_id: str) -> None:
    _chat_id.set(chat_id)
    bind_contextvars(chat_id=chat_id)


def get_chat_id() -> str | None:
    return _chat_id.get()


def bind_session_id(session_id: str) -> None:
    _session_id.set(session_id)
    bind_contextvars(session_id=session_id)


def get_session_id() -> str | None:
    return _session_id.get()


def bind_trace_id(trace_id: str) -> None:
    _trace_id.set(trace_id)
    bind_contextvars(trace_id=trace_id)


def get_trace_id() -> str | None:
    return _trace_id.get()


def bind_context(**kwargs: Any) -> None:
    bind_contextvars(**kwargs)


def get_context() -> dict[str, Any]:
    return dict(get_contextvars())


def clear_context() -> None:
    clear_contextvars()

    _request_id.set(None)
    _user_id.set(None)
    _agent_id.set(None)
    _workflow_id.set(None)
    _task_id.set(None)
    _project_id.set(None)
    _document_id.set(None)
    _chat_id.set(None)
    _session_id.set(None)
    _trace_id.set(None)


__all__ = [
    "bind_request_id",
    "bind_user_id",
    "bind_agent_id",
    "bind_workflow_id",
    "bind_task_id",
    "bind_project_id",
    "bind_document_id",
    "bind_chat_id",
    "bind_session_id",
    "bind_trace_id",
    "bind_context",
    "get_context",
    "get_request_id",
    "get_user_id",
    "get_agent_id",
    "get_workflow_id",
    "get_task_id",
    "get_project_id",
    "get_document_id",
    "get_chat_id",
    "get_session_id",
    "get_trace_id",
    "clear_context",
]