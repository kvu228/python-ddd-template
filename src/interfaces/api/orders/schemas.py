"""Order API schemas (Pydantic models)."""

from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class ShippingAddressSchema(BaseModel):
    """Shipping address schema."""

    street: str = Field(..., min_length=1, description="Street address")
    city: str = Field(..., min_length=1, description="City")
    state: str = Field(..., min_length=1, description="State/Province")
    zip_code: str = Field(..., min_length=1, description="ZIP/Postal code")
    country: str = Field(..., min_length=1, description="Country")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA",
            }
        }


class OrderItemSchema(BaseModel):
    """Order item schema."""

    id: UUID = Field(..., description="Item ID")
    product_id: UUID = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    price: Decimal = Field(..., description="Item price")
    currency: str = Field(..., description="Currency code")
    quantity: int = Field(..., gt=0, description="Item quantity")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateOrderRequest(BaseModel):
    """Request schema for creating an order."""

    user_id: UUID = Field(..., description="User ID")
    shipping_address: ShippingAddressSchema = Field(
        ..., description="Shipping address"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                    "country": "USA",
                },
            }
        }


class AddOrderItemRequest(BaseModel):
    """Request schema for adding an item to order."""

    product_id: UUID = Field(..., description="Product ID")
    product_name: str = Field(..., min_length=1, description="Product name")
    price: Decimal = Field(..., gt=0, description="Item price")
    currency: str = Field(default="USD", description="Currency code")
    quantity: int = Field(..., gt=0, description="Item quantity")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "product_name": "Laptop",
                "price": "999.99",
                "currency": "USD",
                "quantity": 2,
            }
        }


class OrderResponse(BaseModel):
    """Response schema for order data."""

    id: UUID = Field(..., description="Order ID")
    user_id: UUID = Field(..., description="User ID")
    status: str = Field(..., description="Order status")
    shipping_address: ShippingAddressSchema = Field(
        ..., description="Shipping address"
    )
    items: List[OrderItemSchema] = Field(..., description="Order items")
    total_amount: Decimal = Field(..., description="Total amount")
    total_currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001",
                    "country": "USA",
                },
                "items": [],
                "total_amount": "0.00",
                "total_currency": "USD",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }


