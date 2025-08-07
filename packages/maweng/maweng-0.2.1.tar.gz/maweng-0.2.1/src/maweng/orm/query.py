"""
Query building system for the Maweng ORM.

This module provides the Query class that offers a fluent interface for
building database queries with filtering, ordering, pagination, and aggregation.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Tuple, Generic
from sqlalchemy import select, update, delete, func, desc, asc, and_, or_, not_
from sqlalchemy.orm import selectinload, joinedload, subqueryload
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_database

T = TypeVar('T')


class Query(Generic[T]):
    """
    Query builder for Maweng ORM.
    
    This class provides a fluent interface for building database queries
    with filtering, ordering, pagination, and aggregation capabilities.
    """
    
    def __init__(self, model_class: Type[T]) -> None:
        """
        Initialize the query builder.
        
        Args:
            model_class: The model class to query
        """
        self.model_class = model_class
        self._select_stmt = select(model_class)
        self._filters = []
        self._order_by = []
        self._limit = None
        self._offset = None
        self._joins = []
        self._options = []
        self._group_by = []
        self._having = []
        self._distinct = False
    
    def filter(self, **kwargs: Any) -> 'Query[T]':
        """
        Add filter conditions to the query.
        
        Args:
            **kwargs: Filter conditions as field=value pairs
            
        Returns:
            Self for chaining
        """
        for field, value in kwargs.items():
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                if value is not None:
                    self._filters.append(column == value)
                else:
                    self._filters.append(column.is_(None))
        return self
    
    def exclude(self, **kwargs: Any) -> 'Query[T]':
        """
        Add exclusion conditions to the query.
        
        Args:
            **kwargs: Exclusion conditions as field=value pairs
            
        Returns:
            Self for chaining
        """
        for field, value in kwargs.items():
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                if value is not None:
                    self._filters.append(column != value)
                else:
                    self._filters.append(column.is_not(None))
        return self
    
    def filter_by(self, **kwargs: Any) -> 'Query[T]':
        """
        Alias for filter method.
        
        Args:
            **kwargs: Filter conditions
            
        Returns:
            Self for chaining
        """
        return self.filter(**kwargs)
    
    def where(self, condition: Any) -> 'Query[T]':
        """
        Add a custom filter condition.
        
        Args:
            condition: SQLAlchemy filter condition
            
        Returns:
            Self for chaining
        """
        self._filters.append(condition)
        return self
    
    def order_by(self, *fields: Any) -> 'Query[T]':
        """
        Add ordering to the query.
        
        Args:
            *fields: Fields to order by (use desc() for descending)
            
        Returns:
            Self for chaining
        """
        for field in fields:
            if isinstance(field, str):
                if field.startswith('-'):
                    column = getattr(self.model_class, field[1:])
                    self._order_by.append(desc(column))
                else:
                    column = getattr(self.model_class, field)
                    self._order_by.append(asc(column))
            else:
                self._order_by.append(field)
        return self
    
    def limit(self, limit: int) -> 'Query[T]':
        """
        Limit the number of results.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            Self for chaining
        """
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'Query[T]':
        """
        Set the offset for pagination.
        
        Args:
            offset: Number of records to skip
            
        Returns:
            Self for chaining
        """
        self._offset = offset
        return self
    
    def page(self, page: int, page_size: int) -> 'Query[T]':
        """
        Set pagination parameters.
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
            
        Returns:
            Self for chaining
        """
        self._offset = (page - 1) * page_size
        self._limit = page_size
        return self
    
    def join(self, target: Any, condition: Optional[Any] = None) -> 'Query[T]':
        """
        Add a join to the query.
        
        Args:
            target: Target table or relationship
            condition: Join condition
            
        Returns:
            Self for chaining
        """
        self._joins.append((target, condition))
        return self
    
    def left_join(self, target: Any, condition: Optional[Any] = None) -> 'Query[T]':
        """
        Add a left join to the query.
        
        Args:
            target: Target table or relationship
            condition: Join condition
            
        Returns:
            Self for chaining
        """
        # This would need to be implemented with proper SQLAlchemy join syntax
        return self.join(target, condition)
    
    def select_related(self, *fields: str) -> 'Query[T]':
        """
        Eager load related objects.
        
        Args:
            *fields: Relationship fields to load
            
        Returns:
            Self for chaining
        """
        for field in fields:
            if hasattr(self.model_class, field):
                self._options.append(selectinload(getattr(self.model_class, field)))
        return self
    
    def prefetch_related(self, *fields: str) -> 'Query[T]':
        """
        Prefetch related objects.
        
        Args:
            *fields: Relationship fields to prefetch
            
        Returns:
            Self for chaining
        """
        return self.select_related(*fields)
    
    def distinct(self) -> 'Query[T]':
        """
        Make the query distinct.
        
        Returns:
            Self for chaining
        """
        self._distinct = True
        return self
    
    def group_by(self, *fields: Any) -> 'Query[T]':
        """
        Add group by clause.
        
        Args:
            *fields: Fields to group by
            
        Returns:
            Self for chaining
        """
        for field in fields:
            if isinstance(field, str):
                column = getattr(self.model_class, field)
                self._group_by.append(column)
            else:
                self._group_by.append(field)
        return self
    
    def having(self, condition: Any) -> 'Query[T]':
        """
        Add having condition for grouped queries.
        
        Args:
            condition: Having condition
            
        Returns:
            Self for chaining
        """
        self._having.append(condition)
        return self
    
    def _build_select(self) -> Any:
        """Build the select statement."""
        stmt = self._select_stmt
        
        # Add filters
        if self._filters:
            stmt = stmt.where(and_(*self._filters))
        
        # Add joins
        for target, condition in self._joins:
            if condition:
                stmt = stmt.join(target, condition)
            else:
                stmt = stmt.join(target)
        
        # Add group by
        if self._group_by:
            stmt = stmt.group_by(*self._group_by)
        
        # Add having
        if self._having:
            stmt = stmt.having(and_(*self._having))
        
        # Add order by
        if self._order_by:
            stmt = stmt.order_by(*self._order_by)
        
        # Add limit and offset
        if self._limit is not None:
            stmt = stmt.limit(self._limit)
        if self._offset is not None:
            stmt = stmt.offset(self._offset)
        
        # Add distinct
        if self._distinct:
            stmt = stmt.distinct()
        
        return stmt
    
    async def all(self) -> List[T]:
        """
        Execute the query and return all results.
        
        Returns:
            List of model instances
        """
        database = get_database()
        stmt = self._build_select()
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def first(self) -> Optional[T]:
        """
        Execute the query and return the first result.
        
        Returns:
            First model instance or None
        """
        database = get_database()
        stmt = self._build_select().limit(1)
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def one(self) -> T:
        """
        Execute the query and return exactly one result.
        
        Returns:
            Single model instance
            
        Raises:
            ValueError: If no results or multiple results
        """
        database = get_database()
        stmt = self._build_select()
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one()
    
    async def one_or_none(self) -> Optional[T]:
        """
        Execute the query and return one result or None.
        
        Returns:
            Single model instance or None
        """
        database = get_database()
        stmt = self._build_select()
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def count(self) -> int:
        """
        Count the number of results.
        
        Returns:
            Number of results
        """
        database = get_database()
        stmt = select(func.count()).select_from(self.model_class)
        
        # Add filters
        if self._filters:
            stmt = stmt.where(and_(*self._filters))
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return result.scalar()
    
    async def exists(self) -> bool:
        """
        Check if any results exist.
        
        Returns:
            True if results exist
        """
        return await self.count() > 0
    
    async def update(self, **kwargs: Any) -> int:
        """
        Update all matching records.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            Number of updated records
        """
        database = get_database()
        stmt = update(self.model_class)
        
        # Add filters
        if self._filters:
            stmt = stmt.where(and_(*self._filters))
        
        # Add update values
        stmt = stmt.values(**kwargs)
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return result.rowcount
    
    async def delete(self) -> int:
        """
        Delete all matching records.
        
        Returns:
            Number of deleted records
        """
        database = get_database()
        stmt = delete(self.model_class)
        
        # Add filters
        if self._filters:
            stmt = stmt.where(and_(*self._filters))
        
        async with database.session() as session:
            result = await session.execute(stmt)
            return result.rowcount
    
    async def paginate(self, page: int, page_size: int) -> Dict[str, Any]:
        """
        Get paginated results.
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
            
        Returns:
            Dictionary with pagination info and results
        """
        total = await self.count()
        results = await self.page(page, page_size).all()
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "items": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }


# Global query object for convenience
class QueryManager:
    """Global query manager for convenience methods."""
    
    def __getattr__(self, name: str) -> Any:
        """Delegate to Query class methods."""
        return getattr(Query, name)


# Create global query instance
query = QueryManager()


# Convenience functions
async def get_all(model_class: Type[T], **filters: Any) -> List[T]:
    """
    Get all instances of a model with optional filters.
    
    Args:
        model_class: Model class
        **filters: Filter conditions
        
    Returns:
        List of model instances
    """
    return await Query(model_class).filter(**filters).all()


async def get_first(model_class: Type[T], **filters: Any) -> Optional[T]:
    """
    Get the first instance of a model with optional filters.
    
    Args:
        model_class: Model class
        **filters: Filter conditions
        
    Returns:
        First model instance or None
    """
    return await Query(model_class).filter(**filters).first()


async def get_one(model_class: Type[T], **filters: Any) -> T:
    """
    Get exactly one instance of a model with filters.
    
    Args:
        model_class: Model class
        **filters: Filter conditions
        
    Returns:
        Single model instance
        
    Raises:
        ValueError: If no results or multiple results
    """
    return await Query(model_class).filter(**filters).one()


async def count_instances(model_class: Type[T], **filters: Any) -> int:
    """
    Count instances of a model with optional filters.
    
    Args:
        model_class: Model class
        **filters: Filter conditions
        
    Returns:
        Number of instances
    """
    return await Query(model_class).filter(**filters).count()


async def exists_instance(model_class: Type[T], **filters: Any) -> bool:
    """
    Check if any instances exist with optional filters.
    
    Args:
        model_class: Model class
        **filters: Filter conditions
        
    Returns:
        True if instances exist
    """
    return await Query(model_class).filter(**filters).exists() 