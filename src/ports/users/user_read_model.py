"""User read model interface (read model)."""

from abc import abstractmethod
from typing import List

from src.domain.users.value_objects import UserId
from src.ports.base_read_model import BaseReadModel


class UserReadModel(BaseReadModel[UserId]):
    """Read model interface for User (read-optimized queries).

    This interface defines the contract for querying denormalized
    user data from the read database (MongoDB).

    Inherits common operations from BaseReadModel:
    - get_by_id(user_id: UserId) -> Optional[dict]
    - create(data: dict) -> None
    - update(user_id: UserId, data: dict) -> None
    - delete(user_id: UserId) -> None
    """

    @abstractmethod
    def search_by_email(self, email: str) -> List[dict]:
        """Search users by email (domain-specific query).

        Args:
            email: Email to search (partial match)

        Returns:
            List of user data dictionaries
        """
        pass


