"""
Model base class for the Maweng ORM system.

This module provides the Model base class that defines the core ORM functionality
including CRUD operations, query building, and model lifecycle hooks.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_database, Base
from .query import Query

T = TypeVar('T', bound='Model')


class Model(Base):
    """
    Base model class for Maweng ORM.
    
    This class provides the foundation for all database models with automatic
    table creation, CRUD operations, and query building capabilities.
    """
    
    __abstract__ = True
    
    # Default primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + 's'
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the model with the given attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Model data as dictionary
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def to_json(self) -> Dict[str, Any]:
        """
        Convert model instance to JSON-serializable dictionary.
        
        Returns:
            JSON-serializable dictionary
        """
        return self.to_dict()
    
    @classmethod
    async def create(cls: Type[T], **kwargs: Any) -> T:
        """
        Create a new model instance and save it to the database.
        
        Args:
            **kwargs: Model attributes
            
        Returns:
            Created model instance
        """
        instance = cls(**kwargs)
        await instance.save()
        return instance
    
    async def save(self) -> None:
        """Save the model instance to the database."""
        database = get_database()
        async with database.session() as session:
            session.add(self)
            await session.flush()
    
    async def update(self, **kwargs: Any) -> None:
        """
        Update the model instance with new values.
        
        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def delete(self, hard: bool = False) -> None:
        """
        Delete the model instance from the database.
        
        Args:
            hard: If True, permanently delete the record
        """
        database = get_database()
        async with database.session() as session:
            if hard:
                await session.delete(self)
            else:
                self.is_deleted = True
                self.updated_at = datetime.utcnow()
                session.add(self)
    
    @classmethod
    async def get(cls: Type[T], id: Any) -> Optional[T]:
        """
        Get a model instance by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            Model instance or None if not found
        """
        database = get_database()
        async with database.session() as session:
            result = await session.get(cls, id)
            if result and result.is_deleted:
                return None
            return result
    
    @classmethod
    async def get_or_create(cls: Type[T], defaults: Optional[Dict[str, Any]] = None, **kwargs: Any) -> tuple[T, bool]:
        """
        Get a model instance or create it if it doesn't exist.
        
        Args:
            defaults: Default values for creation
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (instance, created)
        """
        instance = await cls.filter(**kwargs).first()
        if instance:
            return instance, False
        
        create_kwargs = kwargs.copy()
        if defaults:
            create_kwargs.update(defaults)
        
        instance = await cls.create(**create_kwargs)
        return instance, True
    
    @classmethod
    async def update_or_create(cls: Type[T], defaults: Optional[Dict[str, Any]] = None, **kwargs: Any) -> tuple[T, bool]:
        """
        Update a model instance or create it if it doesn't exist.
        
        Args:
            defaults: Default values for creation/update
            **kwargs: Lookup parameters
            
        Returns:
            Tuple of (instance, created)
        """
        instance = await cls.filter(**kwargs).first()
        if instance:
            if defaults:
                await instance.update(**defaults)
            return instance, False
        
        create_kwargs = kwargs.copy()
        if defaults:
            create_kwargs.update(defaults)
        
        instance = await cls.create(**create_kwargs)
        return instance, True
    
    @classmethod
    def filter(cls: Type[T], **kwargs: Any) -> Query[T]:
        """
        Create a query with filters.
        
        Args:
            **kwargs: Filter conditions
            
        Returns:
            Query object
        """
        return Query(cls).filter(**kwargs)
    
    @classmethod
    def all(cls: Type[T]) -> Query[T]:
        """
        Get all model instances.
        
        Returns:
            Query object for all instances
        """
        return Query(cls)
    
    @classmethod
    def count(cls: Type[T]) -> Query[T]:
        """
        Count all model instances.
        
        Returns:
            Query object for counting
        """
        return Query(cls).count()
    
    @classmethod
    async def bulk_create(cls: Type[T], instances: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple model instances in bulk.
        
        Args:
            instances: List of instance data dictionaries
            
        Returns:
            List of created instances
        """
        database = get_database()
        created_instances = []
        
        async with database.session() as session:
            for instance_data in instances:
                instance = cls(**instance_data)
                session.add(instance)
                created_instances.append(instance)
            
            await session.flush()
        
        return created_instances
    
    @classmethod
    async def bulk_update(cls: Type[T], instances: List[T], fields: List[str]) -> None:
        """
        Update multiple model instances in bulk.
        
        Args:
            instances: List of model instances to update
            fields: List of field names to update
        """
        database = get_database()
        async with database.session() as session:
            for instance in instances:
                instance.updated_at = datetime.utcnow()
                session.add(instance)
    
    @classmethod
    async def bulk_delete(cls: Type[T], ids: List[Any], hard: bool = False) -> None:
        """
        Delete multiple model instances in bulk.
        
        Args:
            ids: List of primary key values
            hard: If True, permanently delete the records
        """
        database = get_database()
        async with database.session() as session:
            if hard:
                await session.execute(
                    cls.__table__.delete().where(cls.id.in_(ids))
                )
            else:
                await session.execute(
                    cls.__table__.update().where(cls.id.in_(ids)).values(
                        is_deleted=True,
                        updated_at=datetime.utcnow()
                    )
                )
    
    # Lifecycle hooks
    async def before_create(self) -> None:
        """Hook called before creating the model instance."""
        pass
    
    async def after_create(self) -> None:
        """Hook called after creating the model instance."""
        pass
    
    async def before_update(self) -> None:
        """Hook called before updating the model instance."""
        pass
    
    async def after_update(self) -> None:
        """Hook called after updating the model instance."""
        pass
    
    async def before_delete(self) -> None:
        """Hook called before deleting the model instance."""
        pass
    
    async def after_delete(self) -> None:
        """Hook called after deleting the model instance."""
        pass
    
    def __repr__(self) -> str:
        """String representation of the model instance."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'None')})>"
    
    def __eq__(self, other: Any) -> bool:
        """Compare model instances by ID."""
        if not isinstance(other, self.__class__):
            return False
        return getattr(self, 'id', None) == getattr(other, 'id', None)
    
    def __hash__(self) -> int:
        """Hash model instance by ID."""
        return hash(getattr(self, 'id', None))


# Convenience functions for model operations
async def create_model(model_class: Type[T], **kwargs: Any) -> T:
    """
    Create a new model instance.
    
    Args:
        model_class: Model class
        **kwargs: Model attributes
        
    Returns:
        Created model instance
    """
    return await model_class.create(**kwargs)


async def get_model(model_class: Type[T], id: Any) -> Optional[T]:
    """
    Get a model instance by ID.
    
    Args:
        model_class: Model class
        id: Primary key value
        
    Returns:
        Model instance or None
    """
    return await model_class.get(id)


async def update_model(instance: T, **kwargs: Any) -> None:
    """
    Update a model instance.
    
    Args:
        instance: Model instance
        **kwargs: Attributes to update
    """
    await instance.update(**kwargs)


async def delete_model(instance: T, hard: bool = False) -> None:
    """
    Delete a model instance.
    
    Args:
        instance: Model instance
        hard: If True, permanently delete
    """
    await instance.delete(hard=hard) 