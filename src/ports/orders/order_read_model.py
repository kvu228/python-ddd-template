"""Order read model interface (read model)."""

from abc import abstractmethod
from typing import List

from src.domain.orders.value_objects import OrderId
from src.domain.users.value_objects import UserId
from src.ports.base_read_model import BaseReadModel


class OrderReadModel(BaseReadModel[OrderId]):
    """Read model interface for Order (read-optimized queries).

    This interface defines the contract for querying denormalized
    order data from the read database (MongoDB).

    Inherits common operations from BaseReadModel:
    - get_by_id(order_id: OrderId) -> Optional[dict]
    - create(data: dict) -> None
    - update(order_id: OrderId, data: dict) -> None
    - delete(order_id: OrderId) -> None
    """

    @abstractmethod
    def get_by_user_id(self, user_id: UserId) -> List[dict]:
        """Get orders by user ID (domain-specific query).

        Args:
            user_id: User identifier

        Returns:
            List of order data dictionaries
        """
        pass


