"""Base repository interface with common CRUD operations."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

# Type variables for entity and ID types
TEntity = TypeVar('TEntity')
TId = TypeVar('TId')


class BaseRepository(ABC, Generic[TEntity, TId]):
    """Base repository interface with common CRUD operations.

    This interface provides standard CRUD operations that most repositories need.
    Concrete repository interfaces can extend this and add domain-specific methods.

    Type Parameters:
        TEntity: The domain entity type (e.g., User, Order)
        TId: The entity's identifier type (e.g., UserId, OrderId)

    Example:
        >>> class UserRepository(BaseRepository[User, UserId]):
        ...     # Inherits: get_by_id, add, update, delete
        ...     @abstractmethod
        ...     def get_by_email(self, email: Email) -> Optional[User]:
        ...         pass  # Domain-specific method
    """

    @abstractmethod
    def get_by_id(self, id: TId) -> Optional[TEntity]:
        """Get entity by ID.

        Args:
            id: Entity identifier

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def add(self, entity: TEntity) -> None:
        """Add a new entity.

        Args:
            entity: Entity to save
        """
        pass

    @abstractmethod
    def update(self, entity: TEntity) -> None:
        """Update an existing entity.

        Args:
            entity: Entity to update
        """
        pass

    @abstractmethod
    def delete(self, id: TId) -> None:
        """Delete an entity.

        Args:
            id: Entity identifier
        """
        pass