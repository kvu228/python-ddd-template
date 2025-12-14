"""User repository interface (write model)."""

from abc import abstractmethod
from typing import Optional

from src.domain.users.entities import User
from src.domain.users.value_objects import Email, UserId
from src.ports.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserId]):
    """Repository interface for User aggregate (write model).

    This interface defines the contract for persisting and retrieving
    User aggregates from the write database (PostgreSQL).

    Inherits common CRUD operations from BaseRepository:
    - get_by_id(user_id: UserId) -> Optional[User]
    - add(user: User) -> None
    - update(user: User) -> None
    - delete(user_id: UserId) -> None
    """

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email (domain-specific query).

        Args:
            email: User email

        Returns:
            User entity if found, None otherwise
        """
        pass


