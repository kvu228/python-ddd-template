"""Base read model interface with common query operations."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

# Type variable for ID type
TId = TypeVar('TId')


class BaseReadModel(ABC, Generic[TId]):
    """Base read model interface with common query operations.

    This interface provides standard operations for read-optimized data models.
    Concrete read model interfaces can extend this and add domain-specific queries.

    Type Parameters:
        TId: The entity's identifier type (e.g., UserId, OrderId)

    Note:
        Read models work with dictionaries (denormalized data) rather than
        domain entities, as they're optimized for specific query patterns.

    Example:
        >>> class UserReadModel(BaseReadModel[UserId]):
        ...     # Inherits: get_by_id, create, update, delete
        ...     @abstractmethod
        ...     def search_by_email(self, email: str) -> List[dict]:
        ...         pass  # Domain-specific query
    """

    @abstractmethod
    def get_by_id(self, id: TId) -> Optional[dict]:
        """Get read model data by ID.

        Args:
            id: Entity identifier

        Returns:
            Data dictionary if found, None otherwise
        """
        pass

    @abstractmethod
    def create(self, data: dict) -> None:
        """Create read model entry.

        Args:
            data: Data dictionary to store
        """
        pass

    @abstractmethod
    def update(self, id: TId, data: dict) -> None:
        """Update read model entry.

        Args:
            id: Entity identifier
            data: Updated data dictionary
        """
        pass

    @abstractmethod
    def delete(self, id: TId) -> None:
        """Delete read model entry.

        Args:
            id: Entity identifier
        """
        pass