"""Order repository interface (write model)."""

from abc import abstractmethod
from typing import List, Optional

from src.domain.orders.entities import Order
from src.domain.orders.value_objects import OrderId
from src.domain.users.value_objects import UserId
from src.ports.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order, OrderId]):
    """Repository interface for Order aggregate (write model).

    This interface defines the contract for persisting and retrieving
    Order aggregates from the write database (PostgreSQL).

    Inherits common CRUD operations from BaseRepository:
    - get_by_id(order_id: OrderId) -> Optional[Order]
    - add(order: Order) -> None
    - update(order: Order) -> None
    - delete(order_id: OrderId) -> None
    """

    @abstractmethod
    def get_by_user_id(self, user_id: UserId) -> List[Order]:
        """Get orders by user ID (domain-specific query).

        Args:
            user_id: User identifier

        Returns:
            List of Order entities
        """
        pass


