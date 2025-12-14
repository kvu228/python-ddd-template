"""Order value objects."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class OrderId:
    """Order ID value object."""

    value: UUID

    def __post_init__(self) -> None:
        """Validate order ID."""
        if not isinstance(self.value, UUID):
            raise ValueError("OrderId must be a UUID")

    @classmethod
    def generate(cls) -> "OrderId":
        """Generate a new OrderId."""
        return cls(uuid4())

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)


@dataclass(frozen=True)
class Money:
    """Money value object with currency."""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        """Validate money."""
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")

    def __add__(self, other: "Money") -> "Money":
        """Add two money objects."""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, multiplier: Decimal) -> "Money":
        """Multiply money by a number."""
        return Money(self.amount * multiplier, self.currency)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class ShippingAddress:
    """Shipping address value object."""

    street: str
    city: str
    state: str
    zip_code: str
    country: str

    def __post_init__(self) -> None:
        """Validate shipping address."""
        if not self.street or not self.street.strip():
            raise ValueError("Street cannot be empty")
        if not self.city or not self.city.strip():
            raise ValueError("City cannot be empty")
        if not self.country or not self.country.strip():
            raise ValueError("Country cannot be empty")

    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self.street}, {self.city}, {self.state} "
            f"{self.zip_code}, {self.country}"
        )


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


