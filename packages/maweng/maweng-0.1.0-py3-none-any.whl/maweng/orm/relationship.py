"""
Relationship definitions for the Maweng ORM system.

This module provides the Relationship class for defining model relationships
including foreign keys, one-to-many, many-to-many, and other relationship types.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import relationship, backref

T = TypeVar('T')


class Relationship:
    """
    Relationship class for defining model relationships.
    
    This class provides a clean interface for defining various types of
    relationships between models including foreign keys, one-to-many,
    many-to-many, and other relationship types.
    """
    
    def __init__(
        self,
        target: Union[str, Type[T]],
        back_populates: Optional[str] = None,
        backref: Optional[str] = None,
        foreign_key: Optional[str] = None,
        primaryjoin: Optional[str] = None,
        secondaryjoin: Optional[str] = None,
        secondary: Optional[Union[str, Table]] = None,
        uselist: bool = True,
        lazy: str = "select",
        cascade: str = "save-update, merge",
        **kwargs: Any
    ) -> None:
        """
        Initialize the relationship.
        
        Args:
            target: Target model class or table name
            back_populates: Back reference attribute name
            backref: Back reference configuration
            foreign_key: Foreign key column name
            primaryjoin: Primary join condition
            secondaryjoin: Secondary join condition
            secondary: Secondary table for many-to-many
            uselist: Whether to return a list or single object
            lazy: Loading strategy
            cascade: Cascade options
            **kwargs: Additional relationship options
        """
        self.target = target
        self.back_populates = back_populates
        self.backref = backref
        self.foreign_key = foreign_key
        self.primaryjoin = primaryjoin
        self.secondaryjoin = secondaryjoin
        self.secondary = secondary
        self.uselist = uselist
        self.lazy = lazy
        self.cascade = cascade
        self.kwargs = kwargs
    
    def __call__(self) -> Any:
        """Create SQLAlchemy relationship."""
        # Build relationship arguments
        args = {
            "lazy": self.lazy,
            "cascade": self.cascade,
            "uselist": self.uselist,
            **self.kwargs
        }
        
        if self.back_populates:
            args["back_populates"] = self.back_populates
        
        if self.backref:
            args["backref"] = self.backref
        
        if self.primaryjoin:
            args["primaryjoin"] = self.primaryjoin
        
        if self.secondaryjoin:
            args["secondaryjoin"] = self.secondaryjoin
        
        if self.secondary:
            args["secondary"] = self.secondary
        
        return relationship(self.target, **args)
    
    @classmethod
    def foreign_key(
        cls,
        target: Union[str, Type[T]],
        back_populates: Optional[str] = None,
        **kwargs: Any
    ) -> 'Relationship':
        """
        Create a foreign key relationship.
        
        Args:
            target: Target model class
            back_populates: Back reference attribute name
            **kwargs: Additional relationship options
            
        Returns:
            Relationship instance
        """
        return cls(target, back_populates=back_populates, uselist=False, **kwargs)
    
    @classmethod
    def one_to_many(
        cls,
        target: Union[str, Type[T]],
        back_populates: Optional[str] = None,
        **kwargs: Any
    ) -> 'Relationship':
        """
        Create a one-to-many relationship.
        
        Args:
            target: Target model class
            back_populates: Back reference attribute name
            **kwargs: Additional relationship options
            
        Returns:
            Relationship instance
        """
        return cls(target, back_populates=back_populates, uselist=True, **kwargs)
    
    @classmethod
    def many_to_one(
        cls,
        target: Union[str, Type[T]],
        back_populates: Optional[str] = None,
        **kwargs: Any
    ) -> 'Relationship':
        """
        Create a many-to-one relationship.
        
        Args:
            target: Target model class
            back_populates: Back reference attribute name
            **kwargs: Additional relationship options
            
        Returns:
            Relationship instance
        """
        return cls(target, back_populates=back_populates, uselist=False, **kwargs)
    
    @classmethod
    def many_to_many(
        cls,
        target: Union[str, Type[T]],
        secondary: Union[str, Table],
        back_populates: Optional[str] = None,
        **kwargs: Any
    ) -> 'Relationship':
        """
        Create a many-to-many relationship.
        
        Args:
            target: Target model class
            secondary: Secondary table for the relationship
            back_populates: Back reference attribute name
            **kwargs: Additional relationship options
            
        Returns:
            Relationship instance
        """
        return cls(
            target,
            secondary=secondary,
            back_populates=back_populates,
            uselist=True,
            **kwargs
        )
    
    @classmethod
    def one_to_one(
        cls,
        target: Union[str, Type[T]],
        back_populates: Optional[str] = None,
        **kwargs: Any
    ) -> 'Relationship':
        """
        Create a one-to-one relationship.
        
        Args:
            target: Target model class
            back_populates: Back reference attribute name
            **kwargs: Additional relationship options
            
        Returns:
            Relationship instance
        """
        return cls(target, back_populates=back_populates, uselist=False, **kwargs)


# Convenience functions for common relationship patterns
def has_one(target: Union[str, Type[T]], back_populates: Optional[str] = None, **kwargs: Any) -> Relationship:
    """
    Create a has-one relationship.
    
    Args:
        target: Target model class
        back_populates: Back reference attribute name
        **kwargs: Additional relationship options
        
    Returns:
        Relationship instance
    """
    return Relationship.one_to_one(target, back_populates=back_populates, **kwargs)


def has_many(target: Union[str, Type[T]], back_populates: Optional[str] = None, **kwargs: Any) -> Relationship:
    """
    Create a has-many relationship.
    
    Args:
        target: Target model class
        back_populates: Back reference attribute name
        **kwargs: Additional relationship options
        
    Returns:
        Relationship instance
    """
    return Relationship.one_to_many(target, back_populates=back_populates, **kwargs)


def belongs_to(target: Union[str, Type[T]], back_populates: Optional[str] = None, **kwargs: Any) -> Relationship:
    """
    Create a belongs-to relationship.
    
    Args:
        target: Target model class
        back_populates: Back reference attribute name
        **kwargs: Additional relationship options
        
    Returns:
        Relationship instance
    """
    return Relationship.many_to_one(target, back_populates=back_populates, **kwargs)


def has_and_belongs_to_many(
    target: Union[str, Type[T]],
    secondary: Union[str, Table],
    back_populates: Optional[str] = None,
    **kwargs: Any
) -> Relationship:
    """
    Create a has-and-belongs-to-many relationship.
    
    Args:
        target: Target model class
        secondary: Secondary table for the relationship
        back_populates: Back reference attribute name
        **kwargs: Additional relationship options
        
    Returns:
        Relationship instance
    """
    return Relationship.many_to_many(target, secondary, back_populates=back_populates, **kwargs)


# Utility functions for creating association tables
def create_association_table(
    table_name: str,
    left_table: str,
    right_table: str,
    left_column: str = "id",
    right_column: str = "id",
    **kwargs: Any
) -> Table:
    """
    Create an association table for many-to-many relationships.
    
    Args:
        table_name: Name of the association table
        left_table: Name of the left table
        right_table: Name of the right table
        left_column: Name of the left table's primary key
        right_column: Name of the right table's primary key
        **kwargs: Additional table options
        
    Returns:
        Association table
    """
    return Table(
        table_name,
        Column(f"{left_table}_{left_column}", Integer, ForeignKey(f"{left_table}.{left_column}")),
        Column(f"{right_table}_{right_column}", Integer, ForeignKey(f"{right_table}.{right_column}")),
        **kwargs
    )


# Example usage patterns
class RelationshipPatterns:
    """Example relationship patterns for common use cases."""
    
    @staticmethod
    def user_posts() -> Dict[str, Any]:
        """User has many posts pattern."""
        return {
            "posts": has_many("Post", back_populates="author"),
        }
    
    @staticmethod
    def post_author() -> Dict[str, Any]:
        """Post belongs to user pattern."""
        return {
            "author": belongs_to("User", back_populates="posts"),
        }
    
    @staticmethod
    def user_profile() -> Dict[str, Any]:
        """User has one profile pattern."""
        return {
            "profile": has_one("Profile", back_populates="user"),
        }
    
    @staticmethod
    def profile_user() -> Dict[str, Any]:
        """Profile belongs to user pattern."""
        return {
            "user": belongs_to("User", back_populates="profile"),
        }
    
    @staticmethod
    def user_roles() -> Dict[str, Any]:
        """User has and belongs to many roles pattern."""
        user_roles_table = create_association_table("user_roles", "users", "roles")
        return {
            "roles": has_and_belongs_to_many("Role", user_roles_table, back_populates="users"),
        }
    
    @staticmethod
    def role_users() -> Dict[str, Any]:
        """Role has and belongs to many users pattern."""
        user_roles_table = create_association_table("user_roles", "users", "roles")
        return {
            "users": has_and_belongs_to_many("User", user_roles_table, back_populates="roles"),
        }
    
    @staticmethod
    def category_products() -> Dict[str, Any]:
        """Category has many products pattern."""
        return {
            "products": has_many("Product", back_populates="category"),
        }
    
    @staticmethod
    def product_category() -> Dict[str, Any]:
        """Product belongs to category pattern."""
        return {
            "category": belongs_to("Category", back_populates="products"),
        }
    
    @staticmethod
    def order_items() -> Dict[str, Any]:
        """Order has many order items pattern."""
        return {
            "items": has_many("OrderItem", back_populates="order"),
        }
    
    @staticmethod
    def order_item_order() -> Dict[str, Any]:
        """Order item belongs to order pattern."""
        return {
            "order": belongs_to("Order", back_populates="items"),
        }
    
    @staticmethod
    def order_item_product() -> Dict[str, Any]:
        """Order item belongs to product pattern."""
        return {
            "product": belongs_to("Product", back_populates="order_items"),
        }
    
    @staticmethod
    def product_order_items() -> Dict[str, Any]:
        """Product has many order items pattern."""
        return {
            "order_items": has_many("OrderItem", back_populates="product"),
        } 