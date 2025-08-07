"""
Request handling for the Maweng framework.

This module provides the Request class that wraps FastAPI's request object
with additional convenience methods and utilities for easier request handling.
"""

import json
from typing import Any, Dict, List, Optional, Union, Type
from urllib.parse import parse_qs

from fastapi import Request as FastAPIRequest
from pydantic import BaseModel, ValidationError


class Request:
    """
    Request wrapper class for Maweng applications.
    
    This class provides a convenient interface for accessing request data,
    including query parameters, form data, JSON body, and headers.
    """
    
    def __init__(self, request: FastAPIRequest) -> None:
        """
        Initialize the request wrapper.
        
        Args:
            request: FastAPI request object
        """
        self._request = request
        self._json_data: Optional[Dict[str, Any]] = None
        self._form_data: Optional[Dict[str, Any]] = None
        self._query_params: Optional[Dict[str, Any]] = None
    
    @property
    def method(self) -> str:
        """Get the HTTP method."""
        return self._request.method
    
    @property
    def url(self) -> str:
        """Get the request URL."""
        return str(self._request.url)
    
    @property
    def path(self) -> str:
        """Get the request path."""
        return self._request.url.path
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        return dict(self._request.headers)
    
    @property
    def cookies(self) -> Dict[str, str]:
        """Get request cookies."""
        return self._request.cookies
    
    @property
    def client(self) -> Optional[str]:
        """Get client IP address."""
        return self._request.client.host if self._request.client else None
    
    @property
    def user_agent(self) -> Optional[str]:
        """Get user agent string."""
        return self.headers.get("user-agent")
    
    @property
    def content_type(self) -> Optional[str]:
        """Get content type."""
        return self.headers.get("content-type")
    
    @property
    def content_length(self) -> Optional[int]:
        """Get content length."""
        length = self.headers.get("content-length")
        return int(length) if length else None
    
    async def json(self) -> Dict[str, Any]:
        """
        Get JSON data from request body.
        
        Returns:
            JSON data as dictionary
            
        Raises:
            ValueError: If request body is not valid JSON
        """
        if self._json_data is None:
            try:
                body = await self._request.body()
                if body:
                    self._json_data = json.loads(body)
                else:
                    self._json_data = {}
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in request body: {e}")
        
        return self._json_data
    
    async def form(self) -> Dict[str, Any]:
        """
        Get form data from request body.
        
        Returns:
            Form data as dictionary
        """
        if self._form_data is None:
            form = await self._request.form()
            self._form_data = dict(form)
        
        return self._form_data
    
    def query_params(self) -> Dict[str, Any]:
        """
        Get query parameters.
        
        Returns:
            Query parameters as dictionary
        """
        if self._query_params is None:
            self._query_params = dict(self._request.query_params)
        
        return self._query_params
    
    def get_query_param(self, key: str, default: Any = None) -> Any:
        """
        Get a specific query parameter.
        
        Args:
            key: Parameter key
            default: Default value if parameter not found
            
        Returns:
            Parameter value or default
        """
        return self.query_params().get(key, default)
    
    def get_query_param_list(self, key: str) -> List[str]:
        """
        Get a query parameter as a list (for multi-value parameters).
        
        Args:
            key: Parameter key
            
        Returns:
            List of parameter values
        """
        params = self.query_params()
        value = params.get(key)
        
        if isinstance(value, list):
            return value
        elif value is not None:
            return [value]
        else:
            return []
    
    def get_header(self, key: str, default: Any = None) -> Any:
        """
        Get a specific header value.
        
        Args:
            key: Header key
            default: Default value if header not found
            
        Returns:
            Header value or default
        """
        return self.headers.get(key.lower(), default)
    
    def get_cookie(self, key: str, default: Any = None) -> Any:
        """
        Get a specific cookie value.
        
        Args:
            key: Cookie key
            default: Default value if cookie not found
            
        Returns:
            Cookie value or default
        """
        return self.cookies.get(key, default)
    
    async def validate_json(self, model: Type[BaseModel]) -> BaseModel:
        """
        Validate JSON data against a Pydantic model.
        
        Args:
            model: Pydantic model class
            
        Returns:
            Validated model instance
            
        Raises:
            ValidationError: If data doesn't match model
        """
        data = await self.json()
        try:
            return model(**data)
        except ValidationError as e:
            raise ValidationError(errors=e.errors(), model=model)
    
    def is_json(self) -> bool:
        """
        Check if request has JSON content type.
        
        Returns:
            True if content type is JSON
        """
        content_type = self.content_type or ""
        return "application/json" in content_type.lower()
    
    def is_form(self) -> bool:
        """
        Check if request has form content type.
        
        Returns:
            True if content type is form data
        """
        content_type = self.content_type or ""
        return "application/x-www-form-urlencoded" in content_type.lower() or "multipart/form-data" in content_type.lower()
    
    def is_xml(self) -> bool:
        """
        Check if request has XML content type.
        
        Returns:
            True if content type is XML
        """
        content_type = self.content_type or ""
        return "application/xml" in content_type.lower() or "text/xml" in content_type.lower()
    
    def accepts_json(self) -> bool:
        """
        Check if client accepts JSON responses.
        
        Returns:
            True if client accepts JSON
        """
        accept = self.get_header("accept", "")
        return "application/json" in accept.lower() or "*/*" in accept.lower()
    
    def accepts_html(self) -> bool:
        """
        Check if client accepts HTML responses.
        
        Returns:
            True if client accepts HTML
        """
        accept = self.get_header("accept", "")
        return "text/html" in accept.lower() or "*/*" in accept.lower()
    
    def is_ajax(self) -> bool:
        """
        Check if request is an AJAX request.
        
        Returns:
            True if request is AJAX
        """
        return self.get_header("x-requested-with") == "XMLHttpRequest"
    
    def is_mobile(self) -> bool:
        """
        Check if request is from a mobile device.
        
        Returns:
            True if request is from mobile device
        """
        user_agent = self.user_agent or ""
        mobile_keywords = ["mobile", "android", "iphone", "ipad", "blackberry", "windows phone"]
        return any(keyword in user_agent.lower() for keyword in mobile_keywords)
    
    def get_language(self) -> Optional[str]:
        """
        Get preferred language from Accept-Language header.
        
        Returns:
            Preferred language code or None
        """
        accept_language = self.get_header("accept-language", "")
        if accept_language:
            # Parse Accept-Language header and return first language
            languages = [lang.strip().split(";")[0] for lang in accept_language.split(",")]
            return languages[0] if languages else None
        return None
    
    def get_user_agent_info(self) -> Dict[str, Any]:
        """
        Parse user agent string for browser/device information.
        
        Returns:
            Dictionary with browser and device information
        """
        user_agent = self.user_agent or ""
        
        info = {
            "browser": "Unknown",
            "browser_version": "Unknown",
            "os": "Unknown",
            "os_version": "Unknown",
            "device": "Unknown",
            "is_mobile": self.is_mobile(),
        }
        
        # Simple user agent parsing (in a real implementation, you might use a library like user-agents)
        ua_lower = user_agent.lower()
        
        # Browser detection
        if "chrome" in ua_lower:
            info["browser"] = "Chrome"
        elif "firefox" in ua_lower:
            info["browser"] = "Firefox"
        elif "safari" in ua_lower:
            info["browser"] = "Safari"
        elif "edge" in ua_lower:
            info["browser"] = "Edge"
        elif "opera" in ua_lower:
            info["browser"] = "Opera"
        
        # OS detection
        if "windows" in ua_lower:
            info["os"] = "Windows"
        elif "mac" in ua_lower:
            info["os"] = "macOS"
        elif "linux" in ua_lower:
            info["os"] = "Linux"
        elif "android" in ua_lower:
            info["os"] = "Android"
        elif "ios" in ua_lower:
            info["os"] = "iOS"
        
        return info
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert request to dictionary for logging/debugging.
        
        Returns:
            Request information as dictionary
        """
        return {
            "method": self.method,
            "url": self.url,
            "path": self.path,
            "headers": self.headers,
            "cookies": self.cookies,
            "client": self.client,
            "user_agent": self.user_agent,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "query_params": self.query_params(),
        }
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate unknown attributes to the underlying FastAPI request.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute value from FastAPI request
        """
        return getattr(self._request, name) 