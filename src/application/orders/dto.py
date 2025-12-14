"""Order DTOs (Data Transfer Objects)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID


@dataclass
class OrderItemDTO:
    """DTO for order item."""

    id: UUID
    product_id: UUID
    product_name: str
    price: Decimal
    currency: str
    quantity: int


@dataclass
class ShippingAddressDTO:
    """DTO for shipping address."""

    street: str
    city: str
    state: str
    zip_code: str
    country: str


@dataclass
class CreateOrderDTO:
    """DTO for creating an order."""

    user_id: UUID
    shipping_address: ShippingAddressDTO


@dataclass
class AddOrderItemDTO:
    """DTO for adding an item to order."""

    product_id: UUID
    product_name: str
    price: Decimal
    currency: str
    quantity: int


@dataclass
class OrderDTO:
    """DTO for order data."""

    id: UUID
    user_id: UUID
    status: str
    shipping_address: ShippingAddressDTO
    items: List[OrderItemDTO]
    total_amount: Decimal
    total_currency: str
    created_at: datetime
    updated_at: datetime


