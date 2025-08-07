"""
Shared Interfaces

This module defines shared interfaces that are used across multiple domains.
These interfaces ensure proper separation of concerns and enable dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Generic, TypeVar, Set

from url_analyzer.shared.domain import Entity, Identifier


# Generic type variables for use in generic interfaces
T = TypeVar('T', bound=Entity)
ID = TypeVar('ID')


class Repository(Generic[T, ID], ABC):
    """
    Generic interface for repositories.
    
    Repositories are responsible for storing and retrieving domain objects.
    They provide an abstraction over the underlying data storage mechanism.
    """
    
    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """
        Find an entity by its identifier.
        
        Args:
            id: Identifier of the entity to find
            
        Returns:
            Entity or None if not found
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[T]:
        """
        Find all entities.
        
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Save an entity.
        
        Args:
            entity: Entity to save
            
        Returns:
            Saved entity
        """
        pass
    
    @abstractmethod
    def delete(self, entity: T) -> None:
        """
        Delete an entity.
        
        Args:
            entity: Entity to delete
        """
        pass
    
    @abstractmethod
    def delete_by_id(self, id: ID) -> None:
        """
        Delete an entity by its identifier.
        
        Args:
            id: Identifier of the entity to delete
        """
        pass
    
    @abstractmethod
    def exists(self, id: ID) -> bool:
        """
        Check if an entity exists.
        
        Args:
            id: Identifier of the entity to check
            
        Returns:
            True if the entity exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Count the number of entities.
        
        Returns:
            Number of entities
        """
        pass


class Service(ABC):
    """
    Base interface for domain services.
    
    Domain services encapsulate domain logic that doesn't naturally fit within an entity or value object.
    They are stateless and operate on domain objects.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this service.
        
        Returns:
            Service name
        """
        pass