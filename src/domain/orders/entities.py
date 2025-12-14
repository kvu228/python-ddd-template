"""Order aggregate root entity with OrderItem."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from src.domain.orders.exceptions import (
    InvalidOrderDataError,
    OrderCannotBeModifiedError,
    OrderItemNotFoundError,
)
from src.domain.orders.value_objects import (
    Money,
    OrderId,
    OrderStatus,
    ShippingAddress,
)
from src.domain.users.value_objects import UserId


@dataclass
class OrderItem:
    """Order item entity (part of Order aggregate).

    Example:
        >>> item = OrderItem.create(
        ...     product_id=UUID("..."),
        ...     product_name="Laptop",
        ...     price=Money(Decimal("999.99"), "USD"),
        ...     quantity=2
        ... )
    """

    id: UUID
    product_id: UUID
    product_name: str
    price: Money
    quantity: int

    @classmethod
    def create(
        cls,
        product_id: UUID,
        product_name: str,
        price: Money,
        quantity: int,
    ) -> "OrderItem":
        """Create a new order item.

        Args:
            product_id: Product identifier
            product_name: Product name
            price: Item price
            quantity: Item quantity

        Returns:
            New OrderItem instance

        Raises:
            InvalidOrderDataError: If data is invalid
        """
        if not product_name or not product_name.strip():
            raise InvalidOrderDataError("Product name cannot be empty")
        if quantity <= 0:
            raise InvalidOrderDataError("Quantity must be greater than 0")

        return cls(
            id=uuid4(),
            product_id=product_id,
            product_name=product_name.strip(),
            price=price,
            quantity=quantity,
        )

    def update_quantity(self, new_quantity: int) -> None:
        """Update item quantity.

        Args:
            new_quantity: New quantity

        Raises:
            InvalidOrderDataError: If quantity is invalid
        """
        if new_quantity <= 0:
            raise InvalidOrderDataError("Quantity must be greater than 0")
        self.quantity = new_quantity

    def calculate_total(self) -> Money:
        """Calculate total price for this item.

        Returns:
            Total price (price * quantity)
        """
        return self.price * Decimal(self.quantity)

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, OrderItem):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)


@dataclass
class Order:
    """Order aggregate root.

    This is the aggregate root for the order domain. All operations
    on order data should go through this entity.

    Example:
        >>> order_id = OrderId.generate()
        >>> user_id = UserId.generate()
        >>> address = ShippingAddress(...)
        >>> order = Order.create(order_id, user_id, address)
        >>> item = OrderItem.create(...)
        >>> order.add_item(item)
        >>> order.confirm()
    """

    id: OrderId
    user_id: UserId
    status: OrderStatus
    shipping_address: ShippingAddress
    items: List[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _domain_events: List[dict] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        order_id: OrderId,
        user_id: UserId,
        shipping_address: ShippingAddress,
    ) -> "Order":
        """Factory method to create a new order.

        Args:
            order_id: Unique order identifier
            user_id: User who created the order
            shipping_address: Shipping address

        Returns:
            New Order instance
        """
        order = cls(
            id=order_id,
            user_id=user_id,
            status=OrderStatus.PENDING,
            shipping_address=shipping_address,
        )
        order._add_domain_event("order_created", {"order_id": str(order.id)})
        return order

    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order.

        Args:
            item: Order item to add

        Raises:
            OrderCannotBeModifiedError: If order cannot be modified
        """
        if self.status != OrderStatus.PENDING:
            raise OrderCannotBeModifiedError(
                f"Cannot modify order with status {self.status}"
            )

        # Check if item with same product_id already exists
        existing_item = next(
            (i for i in self.items if i.product_id == item.product_id), None
        )
        if existing_item:
            existing_item.update_quantity(existing_item.quantity + item.quantity)
        else:
            self.items.append(item)

        self.updated_at = datetime.utcnow()
        self._add_domain_event(
            "order_item_added",
            {"order_id": str(self.id), "item_id": str(item.id)},
        )

    def remove_item(self, item_id: UUID) -> None:
        """Remove an item from the order.

        Args:
            item_id: ID of item to remove

        Raises:
            OrderCannotBeModifiedError: If order cannot be modified
            OrderItemNotFoundError: If item is not found
        """
        if self.status != OrderStatus.PENDING:
            raise OrderCannotBeModifiedError(
                f"Cannot modify order with status {self.status}"
            )

        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            raise OrderItemNotFoundError(f"Item {item_id} not found in order")

        self.items.remove(item)
        self.updated_at = datetime.utcnow()
        self._add_domain_event(
            "order_item_removed",
            {"order_id": str(self.id), "item_id": str(item_id)},
        )

    def confirm(self) -> None:
        """Confirm the order.

        Raises:
            OrderCannotBeModifiedError: If order cannot be confirmed
            InvalidOrderDataError: If order has no items
        """
        if self.status != OrderStatus.PENDING:
            raise OrderCannotBeModifiedError(
                f"Cannot confirm order with status {self.status}"
            )

        if not self.items:
            raise InvalidOrderDataError("Cannot confirm order with no items")

        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
        self._add_domain_event("order_confirmed", {"order_id": str(self.id)})

    def cancel(self) -> None:
        """Cancel the order.

        Raises:
            OrderCannotBeModifiedError: If order cannot be cancelled
        """
        if self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise OrderCannotBeModifiedError(
                f"Cannot cancel order with status {self.status}"
            )

        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self._add_domain_event("order_cancelled", {"order_id": str(self.id)})

    def calculate_total(self) -> Money:
        """Calculate total price of the order.

        Returns:
            Total price of all items
        """
        if not self.items:
            return Money(Decimal("0.00"), "USD")

        total = Money(Decimal("0.00"), self.items[0].price.currency)
        for item in self.items:
            total = total + item.calculate_total()
        return total

    def _add_domain_event(self, event_type: str, data: dict) -> None:
        """Add a domain event.

        Args:
            event_type: Type of the event
            data: Event data
        """
        self._domain_events.append(
            {
                "event_type": event_type,
                "data": data,
                "occurred_at": datetime.utcnow().isoformat(),
            }
        )

    def get_domain_events(self) -> List[dict]:
        """Get and clear domain events.

        Returns:
            List of domain events
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Order):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)


