"""
Middleware system for the Maweng framework.

This module provides the middleware base class and common middleware implementations
for request/response processing, authentication, logging, and other cross-cutting concerns.
"""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp

from .request import Request as MawengRequest
from .response import Response as MawengResponse

logger = logging.getLogger(__name__)


class Middleware(BaseHTTPMiddleware):
    """
    Base middleware class for Maweng applications.
    
    This class provides a foundation for creating custom middleware
    that can process requests and responses.
    """
    
    def __init__(self, app: ASGIApp) -> None:
        """
        Initialize the middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process the request and response.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint
            
        Returns:
            FastAPI response
        """
        # Convert to Maweng request
        maweng_request = MawengRequest(request)
        
        # Pre-process request
        await self.process_request(maweng_request)
        
        # Call next middleware/endpoint
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Post-process response
        maweng_response = MawengResponse(
            content=response.body,
            status=response.status_code,
            headers=dict(response.headers),
            content_type=response.media_type
        )
        
        await self.process_response(maweng_request, maweng_response, process_time)
        
        return response
    
    async def process_request(self, request: MawengRequest) -> None:
        """
        Process the incoming request.
        
        Args:
            request: Maweng request object
        """
        pass
    
    async def process_response(self, request: MawengRequest, response: MawengResponse, process_time: float) -> None:
        """
        Process the outgoing response.
        
        Args:
            request: Maweng request object
            response: Maweng response object
            process_time: Request processing time
        """
        pass
    
    async def startup(self) -> None:
        """Called when the application starts up."""
        pass
    
    async def shutdown(self) -> None:
        """Called when the application shuts down."""
        pass


class LoggingMiddleware(Middleware):
    """Middleware for request/response logging."""
    
    def __init__(self, app: ASGIApp, log_requests: bool = True, log_responses: bool = True) -> None:
        """
        Initialize the logging middleware.
        
        Args:
            app: ASGI application
            log_requests: Whether to log requests
            log_responses: Whether to log responses
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def process_request(self, request: MawengRequest) -> None:
        """Log incoming request."""
        if self.log_requests:
            logger.info(
                f"Request: {request.method} {request.path} "
                f"from {request.client} - {request.user_agent}"
            )
    
    async def process_response(self, request: MawengRequest, response: MawengResponse, process_time: float) -> None:
        """Log outgoing response."""
        if self.log_responses:
            logger.info(
                f"Response: {request.method} {request.path} "
                f"- {response.status_code} ({process_time:.3f}s)"
            )


class TimingMiddleware(Middleware):
    """Middleware for request timing."""
    
    def __init__(self, app: ASGIApp, add_header: bool = True) -> None:
        """
        Initialize the timing middleware.
        
        Args:
            app: ASGI application
            add_header: Whether to add timing header to response
        """
        super().__init__(app)
        self.add_header = add_header
    
    async def process_response(self, request: MawengRequest, response: MawengResponse, process_time: float) -> None:
        """Add timing information to response."""
        if self.add_header:
            response.set_header("X-Process-Time", f"{process_time:.3f}")


class CORSMiddleware(Middleware):
    """CORS middleware for handling cross-origin requests."""
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = True
    ) -> None:
        """
        Initialize the CORS middleware.
        
        Args:
            app: ASGI application
            allow_origins: Allowed origins
            allow_methods: Allowed HTTP methods
            allow_headers: Allowed headers
            allow_credentials: Allow credentials
        """
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
    
    async def process_request(self, request: MawengRequest) -> None:
        """Handle CORS preflight requests."""
        if request.method == "OPTIONS":
            # Handle preflight request
            pass
    
    async def process_response(self, request: MawengRequest, response: MawengResponse, process_time: float) -> None:
        """Add CORS headers to response."""
        origin = request.get_header("Origin")
        
        if origin and (origin in self.allow_origins or "*" in self.allow_origins):
            response.set_header("Access-Control-Allow-Origin", origin)
        
        response.set_header("Access-Control-Allow-Methods", ", ".join(self.allow_methods))
        response.set_header("Access-Control-Allow-Headers", ", ".join(self.allow_headers))
        
        if self.allow_credentials:
            response.set_header("Access-Control-Allow-Credentials", "true")


class AuthenticationMiddleware(Middleware):
    """Middleware for authentication."""
    
    def __init__(self, app: ASGIApp, auth_handler: Optional[Callable] = None) -> None:
        """
        Initialize the authentication middleware.
        
        Args:
            app: ASGI application
            auth_handler: Authentication handler function
        """
        super().__init__(app)
        self.auth_handler = auth_handler
    
    async def process_request(self, request: MawengRequest) -> None:
        """Process authentication."""
        if self.auth_handler:
            await self.auth_handler(request)


class RateLimitMiddleware(Middleware):
    """Middleware for rate limiting."""
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 100,
        key_func: Optional[Callable] = None
    ) -> None:
        """
        Initialize the rate limit middleware.
        
        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute
            key_func: Function to generate rate limit key
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.key_func = key_func or self._default_key_func
        self._request_counts: Dict[str, List[float]] = {}
    
    def _default_key_func(self, request: MawengRequest) -> str:
        """Default function to generate rate limit key."""
        return request.client or "unknown"
    
    async def process_request(self, request: MawengRequest) -> None:
        """Check rate limits."""
        key = self.key_func(request)
        now = time.time()
        
        # Clean old requests
        if key in self._request_counts:
            self._request_counts[key] = [
                req_time for req_time in self._request_counts[key]
                if now - req_time < 60
            ]
        
        # Check rate limit
        if key in self._request_counts and len(self._request_counts[key]) >= self.requests_per_minute:
            raise Exception("Rate limit exceeded")
        
        # Add current request
        if key not in self._request_counts:
            self._request_counts[key] = []
        self._request_counts[key].append(now)


class ErrorHandlingMiddleware(Middleware):
    """Middleware for error handling."""
    
    def __init__(self, app: ASGIApp, log_errors: bool = True) -> None:
        """
        Initialize the error handling middleware.
        
        Args:
            app: ASGI application
            log_errors: Whether to log errors
        """
        super().__init__(app)
        self.log_errors = log_errors
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle errors during request processing."""
        try:
            return await super().dispatch(request, call_next)
        except Exception as e:
            if self.log_errors:
                logger.error(f"Error processing request: {e}", exc_info=True)
            
            # Return error response
            error_response = MawengResponse.internal_server_error(
                message="Internal server error",
                error_code="INTERNAL_ERROR"
            )
            
            return error_response.to_fastapi_response()


class SecurityMiddleware(Middleware):
    """Middleware for security headers."""
    
    def __init__(self, app: ASGIApp) -> None:
        """Initialize the security middleware."""
        super().__init__(app)
    
    async def process_response(self, request: MawengRequest, response: MawengResponse, process_time: float) -> None:
        """Add security headers to response."""
        # Security headers
        response.set_header("X-Content-Type-Options", "nosniff")
        response.set_header("X-Frame-Options", "DENY")
        response.set_header("X-XSS-Protection", "1; mode=block")
        response.set_header("Referrer-Policy", "strict-origin-when-cross-origin")
        response.set_header("Content-Security-Policy", "default-src 'self'")


class CompressionMiddleware(Middleware):
    """Middleware for response compression."""
    
    def __init__(self, app: ASGIApp, min_size: int = 1024) -> None:
        """
        Initialize the compression middleware.
        
        Args:
            app: ASGI application
            min_size: Minimum size for compression
        """
        super().__init__(app)
        self.min_size = min_size
    
    async def process_response(self, request: MawengRequest, response: MawengResponse, process_time: float) -> None:
        """Compress response if needed."""
        # This would implement actual compression logic
        # For now, just add compression headers
        if len(str(response.content)) > self.min_size:
            response.set_header("Content-Encoding", "gzip")


# Middleware factory functions
def create_logging_middleware(log_requests: bool = True, log_responses: bool = True) -> type[LoggingMiddleware]:
    """Create a logging middleware class."""
    return type("LoggingMiddleware", (LoggingMiddleware,), {
        "__init__": lambda self, app: LoggingMiddleware.__init__(self, app, log_requests, log_responses)
    })


def create_cors_middleware(
    allow_origins: List[str] = None,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
    allow_credentials: bool = True
) -> type[CORSMiddleware]:
    """Create a CORS middleware class."""
    return type("CORSMiddleware", (CORSMiddleware,), {
        "__init__": lambda self, app: CORSMiddleware.__init__(
            self, app, allow_origins, allow_methods, allow_headers, allow_credentials
        )
    })


def create_rate_limit_middleware(
    requests_per_minute: int = 100,
    key_func: Optional[Callable] = None
) -> type[RateLimitMiddleware]:
    """Create a rate limit middleware class."""
    return type("RateLimitMiddleware", (RateLimitMiddleware,), {
        "__init__": lambda self, app: RateLimitMiddleware.__init__(
            self, app, requests_per_minute, key_func
        )
    })


# Middleware stack
class MiddlewareStack:
    """Stack for managing multiple middleware."""
    
    def __init__(self) -> None:
        """Initialize the middleware stack."""
        self.middleware: List[type[Middleware]] = []
    
    def add(self, middleware_class: type[Middleware]) -> 'MiddlewareStack':
        """
        Add middleware to the stack.
        
        Args:
            middleware_class: Middleware class to add
            
        Returns:
            Self for chaining
        """
        self.middleware.append(middleware_class)
        return self
    
    def apply(self, app: ASGIApp) -> ASGIApp:
        """
        Apply all middleware to the application.
        
        Args:
            app: ASGI application
            
        Returns:
            Application with middleware applied
        """
        for middleware_class in reversed(self.middleware):
            app = middleware_class(app)
        return app 