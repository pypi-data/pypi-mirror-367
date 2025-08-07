"""
Core application class for the Maweng framework.

This module provides the main App class that serves as the application container,
handling routing, middleware, configuration, and lifecycle management.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings

from .config import Config
from .exceptions import HTTPException
from .middleware import Middleware
from .view import View
from .orm.database import Database

logger = logging.getLogger(__name__)


class App:
    """
    Main application class for the Maweng framework.
    
    This class serves as the central container for the web application,
    managing routing, middleware, configuration, and the application lifecycle.
    """
    
    def __init__(
        self,
        name: str = "maweng",
        config: Optional[Union[Config, Dict[str, Any]]] = None,
        debug: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the Maweng application.
        
        Args:
            name: Application name
            config: Configuration object or dictionary
            debug: Debug mode flag
            **kwargs: Additional configuration options
        """
        self.name = name
        self.debug = debug
        self.config = self._setup_config(config, **kwargs)
        
        # Initialize FastAPI app
        self.fastapi_app = FastAPI(
            title=self.name,
            debug=self.debug,
            version="0.1.0",
            docs_url="/docs" if self.debug else None,
            redoc_url="/redoc" if self.debug else None,
        )
        
        # Setup components
        self.database = Database(self.config.DATABASE_URL)
        self.middleware: List[Middleware] = []
        self.views: List[View] = []
        self._setup_middleware()
        self._setup_routes()
        
        # Setup static files and templates
        self._setup_static_files()
        self._setup_templates()
        
        # Setup CORS
        if self.config.CORS_ENABLED:
            self._setup_cors()
    
    def _setup_config(
        self, 
        config: Optional[Union[Config, Dict[str, Any]]], 
        **kwargs: Any
    ) -> Config:
        """Setup application configuration."""
        if isinstance(config, dict):
            config = Config(**config)
        elif config is None:
            config = Config()
        
        # Override with kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def _setup_middleware(self) -> None:
        """Setup default middleware."""
        # Add default middleware here
        pass
    
    def _setup_routes(self) -> None:
        """Setup application routes."""
        # Routes will be added when views are registered
        pass
    
    def _setup_static_files(self) -> None:
        """Setup static file serving."""
        static_dir = Path(self.config.STATIC_DIR)
        if static_dir.exists():
            self.fastapi_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    def _setup_templates(self) -> None:
        """Setup template engine."""
        template_dir = Path(self.config.TEMPLATE_DIR)
        if template_dir.exists():
            self.templates = Jinja2Templates(directory=str(template_dir))
        else:
            self.templates = None
    
    def _setup_cors(self) -> None:
        """Setup CORS middleware."""
        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.CORS_ORIGINS,
            allow_credentials=self.config.CORS_ALLOW_CREDENTIALS,
            allow_methods=self.config.CORS_ALLOW_METHODS,
            allow_headers=self.config.CORS_ALLOW_HEADERS,
        )
    
    def add_middleware(self, middleware: Middleware) -> None:
        """
        Add middleware to the application.
        
        Args:
            middleware: Middleware instance to add
        """
        self.middleware.append(middleware)
        # Apply middleware to FastAPI app
        self.fastapi_app.add_middleware(middleware.__class__)
    
    def register_view(self, view: View) -> None:
        """
        Register a view with the application.
        
        Args:
            view: View instance to register
        """
        self.views.append(view)
        view.register_routes(self.fastapi_app)
    
    def register_blueprint(self, blueprint: 'Blueprint') -> None:
        """
        Register a blueprint with the application.
        
        Args:
            blueprint: Blueprint instance to register
        """
        blueprint.register(self)
    
    async def startup(self) -> None:
        """Application startup event."""
        logger.info(f"Starting {self.name} application...")
        
        # Initialize database
        await self.database.connect()
        
        # Run startup middleware
        for middleware in self.middleware:
            if hasattr(middleware, 'startup'):
                await middleware.startup()
        
        logger.info(f"{self.name} application started successfully")
    
    async def shutdown(self) -> None:
        """Application shutdown event."""
        logger.info(f"Shutting down {self.name} application...")
        
        # Run shutdown middleware
        for middleware in reversed(self.middleware):
            if hasattr(middleware, 'shutdown'):
                await middleware.shutdown()
        
        # Close database connection
        await self.database.disconnect()
        
        logger.info(f"{self.name} application shut down successfully")
    
    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        """
        Run the application using uvicorn.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            reload: Enable auto-reload
            **kwargs: Additional uvicorn options
        """
        if reload is None:
            reload = self.debug
        
        # Setup startup and shutdown events
        self.fastapi_app.add_event_handler("startup", self.startup)
        self.fastapi_app.add_event_handler("shutdown", self.shutdown)
        
        # Run with uvicorn
        uvicorn.run(
            self.fastapi_app,
            host=host,
            port=port,
            reload=reload,
            **kwargs
        )
    
    def test_client(self) -> 'TestClient':
        """
        Create a test client for the application.
        
        Returns:
            TestClient instance
        """
        from .testing import TestClient
        return TestClient(self.fastapi_app)


class Blueprint:
    """
    Blueprint for organizing application components.
    
    Blueprints allow you to organize related views, middleware, and other
    components into reusable modules.
    """
    
    def __init__(self, name: str, url_prefix: str = "") -> None:
        """
        Initialize a blueprint.
        
        Args:
            name: Blueprint name
            url_prefix: URL prefix for all routes in this blueprint
        """
        self.name = name
        self.url_prefix = url_prefix
        self.views: List[View] = []
        self.middleware: List[Middleware] = []
    
    def register_view(self, view: View) -> None:
        """
        Register a view with this blueprint.
        
        Args:
            view: View instance to register
        """
        self.views.append(view)
    
    def register_middleware(self, middleware: Middleware) -> None:
        """
        Register middleware with this blueprint.
        
        Args:
            middleware: Middleware instance to register
        """
        self.middleware.append(middleware)
    
    def register(self, app: App) -> None:
        """
        Register this blueprint with an application.
        
        Args:
            app: Application instance to register with
        """
        # Register middleware
        for middleware in self.middleware:
            app.add_middleware(middleware)
        
        # Register views with URL prefix
        for view in self.views:
            view.url_prefix = self.url_prefix
            app.register_view(view) 