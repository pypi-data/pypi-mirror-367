"""
ORM (Object-Relational Mapping) system for the Maweng framework.

This package provides a high-level interface for database operations with
automatic model generation, migrations, and query building.
"""

from .model import Model
from .field import Field
from .relationship import Relationship
from .query import Query, query
from .database import Database

__all__ = [
    "Model",
    "Field", 
    "Relationship",
    "Query",
    "query",
    "Database",
] 