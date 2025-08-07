"""
Maweng Framework - A lightweight, modern Python web framework.

Maweng combines the simplicity of Flask with the power of FastAPI,
featuring an intuitive ORM, auto-generated API documentation,
and developer-friendly tooling.
"""

__version__ = "0.1.0"
__author__ = "Maweng Framework Team"
__email__ = "team@maweng.dev"

# Core framework imports
from .app import App
from .view import View
from .response import Response
from .request import Request
from .config import Config
from .exceptions import (
    HTTPException,
    NotFound,
    BadRequest,
    Unauthorized,
    Forbidden,
    InternalServerError,
)

# ORM imports
from .orm import Model, Field, Relationship, query
from .orm.database import Database

# Middleware imports
from .middleware import Middleware

# Testing imports
from .testing import TestClient

# CLI imports - import from main CLI file, not CLI package
from .cli import main as cli_main

__all__ = [
    # Core
    "App",
    "View", 
    "Response",
    "Request",
    "Config",
    
    # Exceptions
    "HTTPException",
    "NotFound",
    "BadRequest", 
    "Unauthorized",
    "Forbidden",
    "InternalServerError",
    
    # ORM
    "Model",
    "Field",
    "Relationship", 
    "query",
    "Database",
    
    # Middleware
    "Middleware",
    
    # Testing
    "TestClient",
    
    # CLI
    "cli_main",
] 