"""Order ORM models for PostgreSQL."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import relationship

from src.infrastructure.db_postgres.base import Base


class OrderModel(Base):
    """Order ORM model for PostgreSQL."""

    __tablename__ = "orders"

    id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    user_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    status = Column(String(50), nullable=False, default="pending", index=True)
    shipping_address = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<OrderModel(id={self.id}, status={self.status})>"


class OrderItemModel(Base):
    """Order item ORM model for PostgreSQL."""

    __tablename__ = "order_items"

    id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    order_id = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )
    product_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    quantity = Column(Integer, nullable=False)

    # Relationship
    order = relationship("OrderModel", back_populates="items")

    def __repr__(self) -> str:
        """String representation."""
        return f"<OrderItemModel(id={self.id}, product_name={self.product_name})>"


