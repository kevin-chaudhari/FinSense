"""
FinSense AI — Custom Exception Hierarchy

Clean, typed exception classes with consistent HTTP status codes.
"""

from __future__ import annotations

from fastapi import status


class FinSenseException(Exception):
    """Base exception for all FinSense domain errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, status_code: int | None = None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class AuthenticationError(FinSenseException):
    """Raised when credentials are invalid or missing."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_FAILED"


class AuthorizationError(FinSenseException):
    """Raised when user lacks permission."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_FAILED"


class ValidationError(FinSenseException):
    """Raised when input validation fails."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"


class NotFoundError(FinSenseException):
    """Raised when a resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"


class ConflictError(FinSenseException):
    """Raised when a resource already exists."""
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"


class RateLimitError(FinSenseException):
    """Raised when rate limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"


class AgentError(FinSenseException):
    """Raised when the LangGraph agent encounters an error."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "AGENT_ERROR"


class EmbeddingError(FinSenseException):
    """Raised when embedding generation fails."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "EMBEDDING_ERROR"


class VectorStoreError(FinSenseException):
    """Raised when vector store operations fail."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "VECTOR_STORE_ERROR"


class LLMError(FinSenseException):
    """Raised when LLM calls fail."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "LLM_ERROR"


class StorageError(FinSenseException):
    """Raised when file/data storage operations fail."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "STORAGE_ERROR"
