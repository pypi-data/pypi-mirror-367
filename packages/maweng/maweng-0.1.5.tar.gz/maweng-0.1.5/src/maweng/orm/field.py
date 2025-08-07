"""
Field definitions for the Maweng ORM system.

This module provides the Field class and field types for defining database
columns with various data types, constraints, and validation rules.
"""

from typing import Any, Callable, Dict, List, Optional, Type, Union
from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date, Time,
    Float, Numeric, LargeBinary, ForeignKey, UniqueConstraint,
    CheckConstraint, Index, Table, MetaData
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.hybrid import hybrid_property


class Field:
    """
    Field class for defining database columns.
    
    This class provides a clean interface for defining database columns
    with various data types, constraints, and validation rules.
    """
    
    class Integer:
        """Integer field type."""
        
        def __init__(
            self,
            primary_key: bool = False,
            autoincrement: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.autoincrement = autoincrement
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Integer,
                primary_key=self.primary_key,
                autoincrement=self.autoincrement,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class String:
        """String field type."""
        
        def __init__(
            self,
            max_length: Optional[int] = None,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.max_length = max_length
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                String(self.max_length),
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Text:
        """Text field type for long strings."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Text,
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Boolean:
        """Boolean field type."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Boolean,
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class DateTime:
        """DateTime field type."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            timezone: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.timezone = timezone
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                DateTime(timezone=self.timezone),
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Date:
        """Date field type."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Date,
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Time:
        """Time field type."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            timezone: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.timezone = timezone
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Time(timezone=self.timezone),
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Float:
        """Float field type."""
        
        def __init__(
            self,
            precision: Optional[int] = None,
            scale: Optional[int] = None,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.precision = precision
            self.scale = scale
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Float(precision=self.precision),
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Decimal:
        """Decimal field type for precise numeric values."""
        
        def __init__(
            self,
            precision: int = 10,
            scale: int = 2,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.precision = precision
            self.scale = scale
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                Numeric(precision=self.precision, scale=self.scale),
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Binary:
        """Binary field type for storing binary data."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                LargeBinary,
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class ForeignKey:
        """Foreign key field type."""
        
        def __init__(
            self,
            reference: str,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            ondelete: Optional[str] = None,
            onupdate: Optional[str] = None,
            **kwargs: Any
        ) -> None:
            self.reference = reference
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.ondelete = ondelete
            self.onupdate = onupdate
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            return Column(
                ForeignKey(self.reference, ondelete=self.ondelete, onupdate=self.onupdate),
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class JSON:
        """JSON field type for storing JSON data."""
        
        def __init__(
            self,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            from sqlalchemy.dialects.postgresql import JSON
            return Column(
                JSON,
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )
    
    class Enum:
        """Enum field type."""
        
        def __init__(
            self,
            enum_class: Type,
            primary_key: bool = False,
            nullable: bool = True,
            default: Optional[Any] = None,
            unique: bool = False,
            index: bool = False,
            **kwargs: Any
        ) -> None:
            from sqlalchemy import Enum as SQLAlchemyEnum
            self.enum_class = enum_class
            self.primary_key = primary_key
            self.nullable = nullable
            self.default = default
            self.unique = unique
            self.index = index
            self.kwargs = kwargs
        
        def __call__(self) -> Column:
            """Create SQLAlchemy Column."""
            from sqlalchemy import Enum as SQLAlchemyEnum
            return Column(
                SQLAlchemyEnum(self.enum_class),
                primary_key=self.primary_key,
                nullable=self.nullable,
                default=self.default,
                unique=self.unique,
                index=self.index,
                **self.kwargs
            )


# Convenience functions for common field patterns
def primary_key() -> Column:
    """Create a primary key field."""
    return Field.Integer(primary_key=True, autoincrement=True)()


def foreign_key(reference: str, **kwargs: Any) -> Column:
    """Create a foreign key field."""
    return Field.ForeignKey(reference, **kwargs)()


def unique_string(max_length: Optional[int] = None, **kwargs: Any) -> Column:
    """Create a unique string field."""
    return Field.String(max_length=max_length, unique=True, **kwargs)()


def indexed_string(max_length: Optional[int] = None, **kwargs: Any) -> Column:
    """Create an indexed string field."""
    return Field.String(max_length=max_length, index=True, **kwargs)()


def email_field(**kwargs: Any) -> Column:
    """Create an email field with validation."""
    return Field.String(max_length=255, unique=True, index=True, **kwargs)()


def password_field(**kwargs: Any) -> Column:
    """Create a password field."""
    return Field.String(max_length=255, **kwargs)()


def url_field(**kwargs: Any) -> Column:
    """Create a URL field."""
    return Field.String(max_length=2048, **kwargs)()


def slug_field(**kwargs: Any) -> Column:
    """Create a slug field."""
    return Field.String(max_length=255, unique=True, index=True, **kwargs)()


def money_field(precision: int = 10, scale: int = 2, **kwargs: Any) -> Column:
    """Create a money/decimal field."""
    return Field.Decimal(precision=precision, scale=scale, **kwargs)()


def timestamp_field(**kwargs: Any) -> Column:
    """Create a timestamp field."""
    return Field.DateTime(default=datetime.utcnow, **kwargs)()


def created_at_field(**kwargs: Any) -> Column:
    """Create a created_at timestamp field."""
    return Field.DateTime(default=datetime.utcnow, nullable=False, **kwargs)()


def updated_at_field(**kwargs: Any) -> Column:
    """Create an updated_at timestamp field."""
    return Field.DateTime(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, **kwargs)() 