"""User cache interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.users.value_objects import UserId


class UserCache(ABC):
    """Cache interface for User data.

    This interface defines the contract for caching user data
    in Redis with TTL support.
    """

    @abstractmethod
    def get(self, user_id: UserId) -> Optional[dict]:
        """Get user from cache.

        Args:
            user_id: User identifier

        Returns:
            User data dictionary if found, None otherwise
        """
        pass

    @abstractmethod
    def set(self, user_id: UserId, user_data: dict, ttl: int) -> None:
        """Set user in cache.

        Args:
            user_id: User identifier
            user_data: User data dictionary
            ttl: Time to live in seconds
        """
        pass

    @abstractmethod
    def delete(self, user_id: UserId) -> None:
        """Delete user from cache.

        Args:
            user_id: User identifier
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all user cache."""
        pass


