"""
Application Exceptions.

Custom exception hierarchy for the Enterprise AI Platform.
"""

from __future__ import annotations

from typing import Any


class EnterpriseAIException(Exception):
    """
    Base application exception.
    """

    status_code: int = 500
    detail: str = "Internal Server Error"

    def __init__(
        self,
        detail: str | None = None,
        **extra: Any,
    ) -> None:
        self.detail = detail or self.detail
        self.extra = extra
        super().__init__(self.detail)


# ==============================================================================
# Authentication
# ==============================================================================


class AuthenticationError(EnterpriseAIException):
    status_code = 401
    detail = "Authentication failed."


class AuthorizationError(EnterpriseAIException):
    status_code = 403
    detail = "Permission denied."


class InvalidTokenError(AuthenticationError):
    detail = "Invalid or expired token."


# ==============================================================================
# Users
# ==============================================================================


class UserNotFoundError(EnterpriseAIException):
    status_code = 404
    detail = "User not found."


class UserAlreadyExistsError(EnterpriseAIException):
    status_code = 409
    detail = "User already exists."


# ==============================================================================
# Documents
# ==============================================================================


class DocumentNotFoundError(EnterpriseAIException):
    status_code = 404
    detail = "Document not found."


class InvalidFileTypeError(EnterpriseAIException):
    status_code = 400
    detail = "Unsupported file type."


class FileTooLargeError(EnterpriseAIException):
    status_code = 413
    detail = "Uploaded file exceeds the allowed size."


class DocumentProcessingError(EnterpriseAIException):
    status_code = 500
    detail = "Document processing failed."


# ==============================================================================
# RAG
# ==============================================================================


class EmbeddingError(EnterpriseAIException):
    status_code = 500
    detail = "Embedding generation failed."


class VectorStoreError(EnterpriseAIException):
    status_code = 500
    detail = "Vector database operation failed."


class RetrievalError(EnterpriseAIException):
    status_code = 500
    detail = "Document retrieval failed."


class LLMError(EnterpriseAIException):
    status_code = 500
    detail = "Language model request failed."


# ==============================================================================
# Agents
# ==============================================================================


class AgentExecutionError(EnterpriseAIException):
    status_code = 500
    detail = "Agent execution failed."


class WorkflowError(EnterpriseAIException):
    status_code = 500
    detail = "Workflow execution failed."


# ==============================================================================
# Database
# ==============================================================================


class DatabaseError(EnterpriseAIException):
    status_code = 500
    detail = "Database operation failed."


# ==============================================================================
# Validation
# ==============================================================================


class ValidationError(EnterpriseAIException):
    status_code = 422
    detail = "Validation failed."