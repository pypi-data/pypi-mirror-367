"""
Shared Domain Models

This module defines shared domain models and value objects that are used across multiple domains.
These models represent core concepts that are common to multiple domains.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime
import uuid


class Entity(ABC):
    """
    Base class for all entities in the domain model.
    
    Entities are objects that have an identity that persists over time.
    They are defined by their identity rather than their attributes.
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """
        Get the unique identifier for this entity.
        
        Returns:
            Unique identifier as a string
        """
        pass
    
    def __eq__(self, other: object) -> bool:
        """
        Compare two entities for equality based on their identifiers.
        
        Args:
            other: Object to compare with
            
        Returns:
            True if the entities have the same identifier, False otherwise
        """
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """
        Generate a hash code for this entity based on its identifier.
        
        Returns:
            Hash code
        """
        return hash(self.id)


class ValueObject(ABC):
    """
    Base class for all value objects in the domain model.
    
    Value objects are objects that have no identity. They are defined by their attributes.
    Two value objects with the same attributes are considered equal.
    """
    
    def __eq__(self, other: object) -> bool:
        """
        Compare two value objects for equality based on their attributes.
        
        Args:
            other: Object to compare with
            
        Returns:
            True if the value objects have the same attributes, False otherwise
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """
        Generate a hash code for this value object based on its attributes.
        
        Returns:
            Hash code
        """
        return hash(tuple(sorted(self.__dict__.items())))


@dataclass(frozen=True)
class Identifier(ValueObject):
    """
    Value object representing a unique identifier.
    
    This class provides a standardized way to create and work with identifiers
    across the domain model.
    """
    
    value: str
    
    @classmethod
    def create(cls) -> 'Identifier':
        """
        Create a new identifier with a random UUID.
        
        Returns:
            Identifier instance
        """
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'Identifier':
        """
        Create an identifier from an existing string.
        
        Args:
            value: String value for the identifier
            
        Returns:
            Identifier instance
        """
        return cls(value=value)
    
    def __str__(self) -> str:
        """
        Convert the identifier to a string.
        
        Returns:
            String representation of the identifier
        """
        return self.value