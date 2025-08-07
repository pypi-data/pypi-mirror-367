"""
Exception handling for the Maweng framework.

This module provides custom HTTP exceptions and error handling utilities
for consistent error responses across the framework.
"""

from typing import Any, Dict, Optional


class HTTPException(Exception):
    """
    Base HTTP exception class for Maweng applications.
    
    This class provides a consistent interface for HTTP errors with
    status codes, error messages, and additional details.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the HTTP exception.
        
        Args:
            status_code: HTTP status code
            detail: Error detail message
            error_code: Optional error code for programmatic handling
            headers: Optional response headers
            **kwargs: Additional error details
        """
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.headers = headers or {}
        self.kwargs = kwargs
        super().__init__(detail)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON responses.
        
        Returns:
            Exception data as dictionary
        """
        error_data = {
            "error": self.detail,
            "status_code": self.status_code,
        }
        
        if self.error_code:
            error_data["error_code"] = self.error_code
        
        # Add additional kwargs
        error_data.update(self.kwargs)
        
        return error_data


class BadRequest(HTTPException):
    """400 Bad Request exception."""
    
    def __init__(
        self,
        detail: str = "Bad request",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(400, detail, error_code, headers, **kwargs)


class Unauthorized(HTTPException):
    """401 Unauthorized exception."""
    
    def __init__(
        self,
        detail: str = "Unauthorized",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(401, detail, error_code, headers, **kwargs)


class Forbidden(HTTPException):
    """403 Forbidden exception."""
    
    def __init__(
        self,
        detail: str = "Forbidden",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(403, detail, error_code, headers, **kwargs)


class NotFound(HTTPException):
    """404 Not Found exception."""
    
    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(404, detail, error_code, headers, **kwargs)


class MethodNotAllowed(HTTPException):
    """405 Method Not Allowed exception."""
    
    def __init__(
        self,
        detail: str = "Method not allowed",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(405, detail, error_code, headers, **kwargs)


class Conflict(HTTPException):
    """409 Conflict exception."""
    
    def __init__(
        self,
        detail: str = "Conflict",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(409, detail, error_code, headers, **kwargs)


class UnprocessableEntity(HTTPException):
    """422 Unprocessable Entity exception."""
    
    def __init__(
        self,
        detail: str = "Unprocessable entity",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(422, detail, error_code, headers, **kwargs)


class TooManyRequests(HTTPException):
    """429 Too Many Requests exception."""
    
    def __init__(
        self,
        detail: str = "Too many requests",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(429, detail, error_code, headers, **kwargs)


class InternalServerError(HTTPException):
    """500 Internal Server Error exception."""
    
    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(500, detail, error_code, headers, **kwargs)


class NotImplemented(HTTPException):
    """501 Not Implemented exception."""
    
    def __init__(
        self,
        detail: str = "Not implemented",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(501, detail, error_code, headers, **kwargs)


class BadGateway(HTTPException):
    """502 Bad Gateway exception."""
    
    def __init__(
        self,
        detail: str = "Bad gateway",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(502, detail, error_code, headers, **kwargs)


class ServiceUnavailable(HTTPException):
    """503 Service Unavailable exception."""
    
    def __init__(
        self,
        detail: str = "Service unavailable",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(503, detail, error_code, headers, **kwargs)


class GatewayTimeout(HTTPException):
    """504 Gateway Timeout exception."""
    
    def __init__(
        self,
        detail: str = "Gateway timeout",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(504, detail, error_code, headers, **kwargs)


# Validation exceptions
class ValidationError(HTTPException):
    """Validation error exception."""
    
    def __init__(
        self,
        detail: str = "Validation error",
        errors: Optional[list] = None,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(422, detail, error_code, headers, errors=errors, **kwargs)


# Authentication exceptions
class AuthenticationError(Unauthorized):
    """Authentication error exception."""
    
    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


class AuthorizationError(Forbidden):
    """Authorization error exception."""
    
    def __init__(
        self,
        detail: str = "Authorization failed",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


# Database exceptions
class DatabaseError(InternalServerError):
    """Database error exception."""
    
    def __init__(
        self,
        detail: str = "Database error",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


class DatabaseConnectionError(DatabaseError):
    """Database connection error exception."""
    
    def __init__(
        self,
        detail: str = "Database connection error",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


# File handling exceptions
class FileError(HTTPException):
    """Base file error exception."""
    
    def __init__(
        self,
        detail: str = "File error",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(500, detail, error_code, headers, **kwargs)


class FileNotFound(NotFound):
    """File not found exception."""
    
    def __init__(
        self,
        detail: str = "File not found",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


class FileTooLarge(BadRequest):
    """File too large exception."""
    
    def __init__(
        self,
        detail: str = "File too large",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


class InvalidFileType(BadRequest):
    """Invalid file type exception."""
    
    def __init__(
        self,
        detail: str = "Invalid file type",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(detail, error_code, headers, **kwargs)


# Rate limiting exceptions
class RateLimitExceeded(TooManyRequests):
    """Rate limit exceeded exception."""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        if retry_after and headers is None:
            headers = {"Retry-After": str(retry_after)}
        super().__init__(detail, error_code, headers, retry_after=retry_after, **kwargs)


# Utility functions for exception handling
def handle_exception(exception: Exception) -> HTTPException:
    """
    Convert a generic exception to an appropriate HTTP exception.
    
    Args:
        exception: The exception to convert
        
    Returns:
        Appropriate HTTP exception
    """
    if isinstance(exception, HTTPException):
        return exception
    
    # Convert common exceptions to HTTP exceptions
    if isinstance(exception, ValueError):
        return BadRequest(str(exception))
    elif isinstance(exception, KeyError):
        return BadRequest(f"Missing required field: {exception}")
    elif isinstance(exception, TypeError):
        return BadRequest(f"Invalid type: {exception}")
    elif isinstance(exception, FileNotFoundError):
        return FileNotFound(str(exception))
    elif isinstance(exception, PermissionError):
        return Forbidden(str(exception))
    elif isinstance(exception, TimeoutError):
        return GatewayTimeout(str(exception))
    else:
        # Log the original exception for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
        
        return InternalServerError("An unexpected error occurred")


def create_error_response(
    exception: HTTPException,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Create a standardized error response from an HTTP exception.
    
    Args:
        exception: HTTP exception
        include_traceback: Whether to include traceback in response
        
    Returns:
        Standardized error response dictionary
    """
    response = exception.to_dict()
    
    if include_traceback:
        import traceback
        response["traceback"] = traceback.format_exc()
    
    return response 