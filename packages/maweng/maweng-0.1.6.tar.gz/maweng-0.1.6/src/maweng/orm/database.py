"""
Database management for the Maweng ORM system.

This module provides database connection management, session handling,
and the core database interface for the ORM system.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Union
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Global metadata and base for all models
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Database:
    """
    Database manager for Maweng applications.
    
    This class handles database connections, session management, and provides
    a unified interface for database operations.
    """
    
    def __init__(
        self,
        url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        **kwargs: Any
    ) -> None:
        """
        Initialize the database manager.
        
        Args:
            url: Database connection URL
            echo: Echo SQL queries for debugging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            **kwargs: Additional database configuration
        """
        self.url = url
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.kwargs = kwargs
        
        # Initialize engines and sessions
        self._async_engine: Optional[Any] = None
        self._sync_engine: Optional[Any] = None
        self._async_session_factory: Optional[Any] = None
        self._sync_session_factory: Optional[Any] = None
        
        # Track if database is connected
        self._connected = False
    
    @property
    def is_async(self) -> bool:
        """Check if the database URL supports async operations."""
        return self.url.startswith(("postgresql+asyncpg://", "mysql+asyncmy://", "sqlite+aiosqlite://"))
    
    @property
    def is_sqlite(self) -> bool:
        """Check if the database is SQLite."""
        return "sqlite" in self.url.lower()
    
    def _create_async_engine(self) -> Any:
        """Create async database engine."""
        if self.is_sqlite:
            # SQLite async configuration
            engine_kwargs = {
                "echo": self.echo,
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
                **self.kwargs
            }
        else:
            # PostgreSQL/MySQL async configuration
            engine_kwargs = {
                "echo": self.echo,
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                **self.kwargs
            }
        
        return create_async_engine(self.url, **engine_kwargs)
    
    def _create_sync_engine(self) -> Any:
        """Create sync database engine."""
        # Convert async URL to sync URL
        sync_url = self.url.replace("+asyncpg", "").replace("+asyncmy", "").replace("+aiosqlite", "")
        
        if self.is_sqlite:
            engine_kwargs = {
                "echo": self.echo,
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
                **self.kwargs
            }
        else:
            engine_kwargs = {
                "echo": self.echo,
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                **self.kwargs
            }
        
        return create_engine(sync_url, **engine_kwargs)
    
    async def connect(self) -> None:
        """Connect to the database and initialize engines."""
        if self._connected:
            return
        
        try:
            # Create async engine
            self._async_engine = self._create_async_engine()
            self._async_session_factory = async_sessionmaker(
                self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create sync engine for migrations
            self._sync_engine = self._create_sync_engine()
            self._sync_session_factory = sessionmaker(
                self._sync_engine,
                expire_on_commit=False
            )
            
            # Test connection
            async with self._async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            self._connected = True
            logger.info(f"Connected to database: {self.url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if not self._connected:
            return
        
        try:
            if self._async_engine:
                await self._async_engine.dispose()
            if self._sync_engine:
                self._sync_engine.dispose()
            
            self._connected = False
            logger.info("Disconnected from database")
            
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
    
    @asynccontextmanager
    async def session(self):
        """
        Get a database session.
        
        Yields:
            Database session
        """
        if not self._connected:
            await self.connect()
        
        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def create_tables(self) -> None:
        """Create all tables defined in models."""
        if not self._connected:
            await self.connect()
        
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Created all database tables")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def drop_tables(self) -> None:
        """Drop all tables (use with caution!)."""
        if not self._connected:
            await self.connect()
        
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Dropped all database tables")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a raw SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        if not self._connected:
            await self.connect()
        
        async with self.session() as session:
            result = await session.execute(query, params or {})
            return result
    
    async def execute_many(self, query: str, params_list: list) -> Any:
        """
        Execute a raw SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter dictionaries
            
        Returns:
            Query result
        """
        if not self._connected:
            await self.connect()
        
        async with self.session() as session:
            result = await session.execute(query, params_list)
            return result
    
    def get_sync_session(self):
        """
        Get a synchronous database session (for migrations).
        
        Returns:
            Synchronous database session
        """
        if not self._sync_session_factory:
            raise RuntimeError("Database not connected")
        
        return self._sync_session_factory()
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the database connection.
        
        Returns:
            True if database is healthy
        """
        try:
            if not self._connected:
                await self.connect()
            
            async with self._async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_metadata(self) -> MetaData:
        """
        Get the SQLAlchemy metadata object.
        
        Returns:
            SQLAlchemy metadata
        """
        return metadata
    
    def get_base(self) -> Any:
        """
        Get the SQLAlchemy declarative base.
        
        Returns:
            SQLAlchemy declarative base
        """
        return Base


# Global database instance
_database: Optional[Database] = None


def get_database() -> Database:
    """
    Get the global database instance.
    
    Returns:
        Database instance
    """
    global _database
    if _database is None:
        raise RuntimeError("Database not initialized. Call app.database.connect() first.")
    return _database


def set_database(database: Database) -> None:
    """
    Set the global database instance.
    
    Args:
        database: Database instance
    """
    global _database
    _database = database 