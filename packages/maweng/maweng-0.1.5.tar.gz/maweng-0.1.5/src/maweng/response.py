"""
Response handling for the Maweng framework.

This module provides the Response class that offers a clean interface for
creating HTTP responses with various content types and status codes.
"""

import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, FileResponse, RedirectResponse


class Response:
    """
    Response class for Maweng applications.
    
    This class provides a convenient interface for creating HTTP responses
    with various content types and status codes.
    """
    
    def __init__(
        self,
        content: Any = None,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the response.
        
        Args:
            content: Response content
            status: HTTP status code
            headers: Response headers
            content_type: Content type header
            **kwargs: Additional response parameters
        """
        self.content = content
        self.status_code = status
        self.headers = headers or {}
        self.content_type = content_type
        self.kwargs = kwargs
    
    @classmethod
    def json(
        cls,
        data: Any,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a JSON response.
        
        Args:
            data: Data to serialize as JSON
            status: HTTP status code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls(
            content=data,
            status=status,
            headers=headers,
            content_type="application/json",
            **kwargs
        )
    
    @classmethod
    def html(
        cls,
        content: str,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create an HTML response.
        
        Args:
            content: HTML content
            status: HTTP status code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls(
            content=content,
            status=status,
            headers=headers,
            content_type="text/html",
            **kwargs
        )
    
    @classmethod
    def text(
        cls,
        content: str,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a plain text response.
        
        Args:
            content: Text content
            status: HTTP status code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls(
            content=content,
            status=status,
            headers=headers,
            content_type="text/plain",
            **kwargs
        )
    
    @classmethod
    def file(
        cls,
        file_path: Union[str, Path],
        filename: Optional[str] = None,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a file response.
        
        Args:
            file_path: Path to the file
            filename: Optional filename for download
            status: HTTP status code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls(
            content={"file_path": str(file_path), "filename": filename},
            status=status,
            headers=headers,
            content_type="application/octet-stream",
            **kwargs
        )
    
    @classmethod
    def redirect(
        cls,
        url: str,
        status: int = 302,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a redirect response.
        
        Args:
            url: URL to redirect to
            status: HTTP status code (302 for temporary, 301 for permanent)
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls(
            content={"url": url},
            status=status,
            headers=headers,
            content_type="text/html",
            **kwargs
        )
    
    @classmethod
    def error(
        cls,
        message: str,
        status: int = 400,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create an error response.
        
        Args:
            message: Error message
            status: HTTP status code
            error_code: Optional error code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        error_data = {"error": message}
        if error_code:
            error_data["error_code"] = error_code
        
        return cls.json(error_data, status=status, headers=headers, **kwargs)
    
    @classmethod
    def success(
        cls,
        data: Any = None,
        message: Optional[str] = None,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a success response.
        
        Args:
            data: Response data
            message: Success message
            status: HTTP status code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        response_data = {}
        if data is not None:
            response_data["data"] = data
        if message:
            response_data["message"] = message
        
        return cls.json(response_data, status=status, headers=headers, **kwargs)
    
    @classmethod
    def created(
        cls,
        data: Any = None,
        location: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 201 Created response.
        
        Args:
            data: Response data
            location: Location header for the created resource
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        response_headers = headers or {}
        if location:
            response_headers["Location"] = location
        
        return cls.success(data=data, status=201, headers=response_headers, **kwargs)
    
    @classmethod
    def no_content(
        cls,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 204 No Content response.
        
        Args:
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls(content=None, status=204, headers=headers, **kwargs)
    
    @classmethod
    def not_found(
        cls,
        message: str = "Resource not found",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 404 Not Found response.
        
        Args:
            message: Error message
            error_code: Optional error code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls.error(message, status=404, error_code=error_code, headers=headers, **kwargs)
    
    @classmethod
    def unauthorized(
        cls,
        message: str = "Unauthorized",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 401 Unauthorized response.
        
        Args:
            message: Error message
            error_code: Optional error code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls.error(message, status=401, error_code=error_code, headers=headers, **kwargs)
    
    @classmethod
    def forbidden(
        cls,
        message: str = "Forbidden",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 403 Forbidden response.
        
        Args:
            message: Error message
            error_code: Optional error code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls.error(message, status=403, error_code=error_code, headers=headers, **kwargs)
    
    @classmethod
    def bad_request(
        cls,
        message: str = "Bad request",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 400 Bad Request response.
        
        Args:
            message: Error message
            error_code: Optional error code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls.error(message, status=400, error_code=error_code, headers=headers, **kwargs)
    
    @classmethod
    def internal_server_error(
        cls,
        message: str = "Internal server error",
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> 'Response':
        """
        Create a 500 Internal Server Error response.
        
        Args:
            message: Error message
            error_code: Optional error code
            headers: Response headers
            **kwargs: Additional response parameters
            
        Returns:
            Response instance
        """
        return cls.error(message, status=500, error_code=error_code, headers=headers, **kwargs)
    
    def set_header(self, key: str, value: str) -> 'Response':
        """
        Set a response header.
        
        Args:
            key: Header key
            value: Header value
            
        Returns:
            Self for chaining
        """
        self.headers[key] = value
        return self
    
    def set_cookie(
        self,
        key: str,
        value: str,
        max_age: Optional[int] = None,
        expires: Optional[str] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Optional[str] = None
    ) -> 'Response':
        """
        Set a cookie in the response.
        
        Args:
            key: Cookie key
            value: Cookie value
            max_age: Cookie max age in seconds
            expires: Cookie expiration date
            path: Cookie path
            domain: Cookie domain
            secure: Secure flag
            httponly: HttpOnly flag
            samesite: SameSite attribute
            
        Returns:
            Self for chaining
        """
        cookie_parts = [f"{key}={value}"]
        
        if max_age is not None:
            cookie_parts.append(f"Max-Age={max_age}")
        if expires:
            cookie_parts.append(f"Expires={expires}")
        if path:
            cookie_parts.append(f"Path={path}")
        if domain:
            cookie_parts.append(f"Domain={domain}")
        if secure:
            cookie_parts.append("Secure")
        if httponly:
            cookie_parts.append("HttpOnly")
        if samesite:
            cookie_parts.append(f"SameSite={samesite}")
        
        cookie_header = "; ".join(cookie_parts)
        
        if "Set-Cookie" in self.headers:
            self.headers["Set-Cookie"] += f", {cookie_header}"
        else:
            self.headers["Set-Cookie"] = cookie_header
        
        return self
    
    def to_fastapi_response(self) -> FastAPIResponse:
        """
        Convert to FastAPI response.
        
        Returns:
            FastAPI response object
        """
        if self.content_type == "application/json":
            return JSONResponse(
                content=self.content,
                status_code=self.status_code,
                headers=self.headers,
                **self.kwargs
            )
        elif self.content_type == "text/html":
            return HTMLResponse(
                content=self.content,
                status_code=self.status_code,
                headers=self.headers,
                **self.kwargs
            )
        elif self.content_type == "text/plain":
            return PlainTextResponse(
                content=self.content,
                status_code=self.status_code,
                headers=self.headers,
                **self.kwargs
            )
        elif self.content_type == "application/octet-stream" and isinstance(self.content, dict):
            # File response
            file_path = self.content.get("file_path")
            filename = self.content.get("filename")
            return FileResponse(
                path=file_path,
                filename=filename,
                status_code=self.status_code,
                headers=self.headers,
                **self.kwargs
            )
        elif isinstance(self.content, dict) and "url" in self.content:
            # Redirect response
            return RedirectResponse(
                url=self.content["url"],
                status_code=self.status_code,
                headers=self.headers,
                **self.kwargs
            )
        else:
            # Default response
            return FastAPIResponse(
                content=self.content,
                status_code=self.status_code,
                headers=self.headers,
                media_type=self.content_type,
                **self.kwargs
            ) 