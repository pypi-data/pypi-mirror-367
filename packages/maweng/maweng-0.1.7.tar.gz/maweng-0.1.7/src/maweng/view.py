"""
View system for the Maweng framework.

This module provides the View base class and routing decorators for creating
API endpoints with automatic OpenAPI documentation generation.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps

from fastapi import APIRouter, Depends, HTTPException, Request as FastAPIRequest
from pydantic import BaseModel

from .request import Request
from .response import Response
from .exceptions import HTTPException as MawengHTTPException


class View:
    """
    Base view class for creating API endpoints.
    
    Views provide a clean interface for defining API endpoints with automatic
    route registration and OpenAPI documentation generation.
    """
    
    def __init__(self, url_prefix: str = "") -> None:
        """
        Initialize the view.
        
        Args:
            url_prefix: URL prefix for all routes in this view
        """
        self.url_prefix = url_prefix
        self.router = APIRouter()
        self._routes: List[Dict[str, Any]] = []
    
    def register_routes(self, app) -> None:
        """
        Register all routes with the FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        # Register the router with the app
        app.include_router(self.router, prefix=self.url_prefix)
    
    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 200,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
        **kwargs: Any
    ) -> Callable:
        """
        Decorator for defining routes.
        
        Args:
            path: URL path
            methods: HTTP methods
            response_model: Response model for OpenAPI docs
            status_code: Default status code
            tags: OpenAPI tags
            summary: Route summary
            description: Route description
            dependencies: Route dependencies
            **kwargs: Additional FastAPI route parameters
            
        Returns:
            Decorated function
        """
        if methods is None:
            methods = ["GET"]
        
        def decorator(func: Callable) -> Callable:
            # Convert the function to handle Maweng Request/Response
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Call the original function
                    result = await func(*args, **kwargs)
                    
                    # Handle different response types
                    if isinstance(result, Response):
                        return result.to_fastapi_response()
                    elif isinstance(result, dict):
                        return Response.json(result, status=status_code).to_fastapi_response()
                    elif isinstance(result, (str, int, float, bool)):
                        return Response.json({"data": result}, status=status_code).to_fastapi_response()
                    else:
                        return Response.json(result, status=status_code).to_fastapi_response()
                        
                except MawengHTTPException as e:
                    raise HTTPException(status_code=e.status_code, detail=e.detail)
                except Exception as e:
                    # Log the error and return 500
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Unhandled exception in {func.__name__}: {e}")
                    raise HTTPException(status_code=500, detail="Internal server error")
            
            # Add route to router
            for method in methods:
                route_kwargs = {
                    "response_model": response_model,
                    "status_code": status_code,
                    "tags": tags or [self.__class__.__name__],
                    "summary": summary or func.__name__.replace("_", " ").title(),
                    "description": description,
                    "dependencies": dependencies,
                    **kwargs
                }
                
                # Remove None values
                route_kwargs = {k: v for k, v in route_kwargs.items() if v is not None}
                
                getattr(self.router, method.lower())(path, **route_kwargs)(wrapper)
            
            # Store route information
            self._routes.append({
                "path": path,
                "methods": methods,
                "function": func.__name__,
                "summary": summary or func.__name__.replace("_", " ").title(),
            })
            
            return wrapper
        
        return decorator
    
    def get(
        self,
        path: str,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 200,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
        **kwargs: Any
    ) -> Callable:
        """Decorator for GET routes."""
        return self.route(
            path=path,
            methods=["GET"],
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            summary=summary,
            description=description,
            dependencies=dependencies,
            **kwargs
        )
    
    def post(
        self,
        path: str,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 201,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
        **kwargs: Any
    ) -> Callable:
        """Decorator for POST routes."""
        return self.route(
            path=path,
            methods=["POST"],
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            summary=summary,
            description=description,
            dependencies=dependencies,
            **kwargs
        )
    
    def put(
        self,
        path: str,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 200,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
        **kwargs: Any
    ) -> Callable:
        """Decorator for PUT routes."""
        return self.route(
            path=path,
            methods=["PUT"],
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            summary=summary,
            description=description,
            dependencies=dependencies,
            **kwargs
        )
    
    def delete(
        self,
        path: str,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 204,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
        **kwargs: Any
    ) -> Callable:
        """Decorator for DELETE routes."""
        return self.route(
            path=path,
            methods=["DELETE"],
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            summary=summary,
            description=description,
            dependencies=dependencies,
            **kwargs
        )
    
    def patch(
        self,
        path: str,
        response_model: Optional[Type[BaseModel]] = None,
        status_code: int = 200,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dependencies: Optional[List[Depends]] = None,
        **kwargs: Any
    ) -> Callable:
        """Decorator for PATCH routes."""
        return self.route(
            path=path,
            methods=["PATCH"],
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            summary=summary,
            description=description,
            dependencies=dependencies,
            **kwargs
        )
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Get all registered routes for this view.
        
        Returns:
            List of route information dictionaries
        """
        return self._routes


# Convenience functions for creating views without inheritance
def view(url_prefix: str = "") -> Type[View]:
    """
    Create a view class with the given URL prefix.
    
    Args:
        url_prefix: URL prefix for all routes
        
    Returns:
        View class
    """
    return type("View", (View,), {"url_prefix": url_prefix})


def route(
    path: str,
    methods: Optional[List[str]] = None,
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    **kwargs: Any
) -> Callable:
    """
    Standalone route decorator for functions.
    
    Args:
        path: URL path
        methods: HTTP methods
        response_model: Response model for OpenAPI docs
        status_code: Default status code
        tags: OpenAPI tags
        summary: Route summary
        description: Route description
        dependencies: Route dependencies
        **kwargs: Additional FastAPI route parameters
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        # This would need to be used with a router or app instance
        # For now, just return the function as-is
        return func
    
    return decorator


# HTTP method decorators
def get(
    path: str,
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    **kwargs: Any
) -> Callable:
    """Decorator for GET routes."""
    return route(
        path=path,
        methods=["GET"],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        summary=summary,
        description=description,
        dependencies=dependencies,
        **kwargs
    )


def post(
    path: str,
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = 201,
    tags: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    **kwargs: Any
) -> Callable:
    """Decorator for POST routes."""
    return route(
        path=path,
        methods=["POST"],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        summary=summary,
        description=description,
        dependencies=dependencies,
        **kwargs
    )


def put(
    path: str,
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    **kwargs: Any
) -> Callable:
    """Decorator for PUT routes."""
    return route(
        path=path,
        methods=["PUT"],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        summary=summary,
        description=description,
        dependencies=dependencies,
        **kwargs
    )


def delete(
    path: str,
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = 204,
    tags: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    **kwargs: Any
) -> Callable:
    """Decorator for DELETE routes."""
    return route(
        path=path,
        methods=["DELETE"],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        summary=summary,
        description=description,
        dependencies=dependencies,
        **kwargs
    )


def patch(
    path: str,
    response_model: Optional[Type[BaseModel]] = None,
    status_code: int = 200,
    tags: Optional[List[str]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    dependencies: Optional[List[Depends]] = None,
    **kwargs: Any
) -> Callable:
    """Decorator for PATCH routes."""
    return route(
        path=path,
        methods=["PATCH"],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        summary=summary,
        description=description,
        dependencies=dependencies,
        **kwargs
    ) 