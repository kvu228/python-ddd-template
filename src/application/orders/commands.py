"""Order commands (CQRS pattern)."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.application.orders.dto import AddOrderItemDTO, ShippingAddressDTO


@dataclass
class CreateOrderCommand:
    """Command to create a new order."""

    user_id: UUID
    shipping_address: ShippingAddressDTO


@dataclass
class AddOrderItemCommand:
    """Command to add an item to order."""

    order_id: UUID
    product_id: UUID
    product_name: str
    price: Decimal
    currency: str
    quantity: int


@dataclass
class RemoveOrderItemCommand:
    """Command to remove an item from order."""

    order_id: UUID
    item_id: UUID


@dataclass
class ConfirmOrderCommand:
    """Command to confirm an order."""

    order_id: UUID


@dataclass
class CancelOrderCommand:
    """Command to cancel an order."""

    order_id: UUID


