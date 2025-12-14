"""Order repository PostgreSQL implementation."""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.orders.entities import Order, OrderItem
from src.domain.orders.value_objects import (
    Money,
    OrderId,
    OrderStatus,
    ShippingAddress,
)
from src.domain.users.value_objects import UserId
from src.infrastructure.db_postgres.order_models import OrderItemModel, OrderModel
from src.ports.orders.order_repository import OrderRepository


class PostgreSQLOrderRepository(OrderRepository):
    """PostgreSQL implementation of OrderRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy database session
        """
        self._session = session

    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Get order by ID."""
        model = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == order_id.value)
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def get_by_user_id(self, user_id: UserId) -> List[Order]:
        """Get orders by user ID."""
        models = (
            self._session.query(OrderModel)
            .filter(OrderModel.user_id == user_id.value)
            .all()
        )
        return [self._to_entity(model) for model in models]

    def add(self, order: Order) -> None:
        """Add a new order."""
        model = self._to_model(order)
        self._session.add(model)
        self._session.flush()

    def update(self, order: Order) -> None:
        """Update an existing order."""
        model = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == order.id.value)
            .first()
        )
        if model:
            model.status = order.status.value
            model.shipping_address = {
                "street": order.shipping_address.street,
                "city": order.shipping_address.city,
                "state": order.shipping_address.state,
                "zip_code": order.shipping_address.zip_code,
                "country": order.shipping_address.country,
            }
            model.updated_at = order.updated_at

            # Update items
            # Delete existing items
            self._session.query(OrderItemModel).filter(
                OrderItemModel.order_id == order.id.value
            ).delete()

            # Add new items
            for item in order.items:
                item_model = OrderItemModel(
                    id=item.id,
                    order_id=order.id.value,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=item.price.amount,
                    currency=item.price.currency,
                    quantity=item.quantity,
                )
                self._session.add(item_model)

            self._session.flush()

    def delete(self, order_id: OrderId) -> None:
        """Delete an order."""
        model = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == order_id.value)
            .first()
        )
        if model:
            self._session.delete(model)
            self._session.flush()

    def _to_entity(self, model: OrderModel) -> Order:
        """Convert ORM model to domain entity."""
        from src.domain.orders.entities import Order

        shipping_address = ShippingAddress(
            street=model.shipping_address["street"],
            city=model.shipping_address["city"],
            state=model.shipping_address["state"],
            zip_code=model.shipping_address["zip_code"],
            country=model.shipping_address["country"],
        )

        items = [
            OrderItem(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=Money(item.price, item.currency),
                quantity=item.quantity,
            )
            for item in model.items
        ]

        order = Order(
            id=OrderId(model.id),
            user_id=UserId(model.user_id),
            status=OrderStatus(model.status),
            shipping_address=shipping_address,
            items=items,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

        return order

    def _to_model(self, order: Order) -> OrderModel:
        """Convert domain entity to ORM model."""
        model = OrderModel(
            id=order.id.value,
            user_id=order.user_id.value,
            status=order.status.value,
            shipping_address={
                "street": order.shipping_address.street,
                "city": order.shipping_address.city,
                "state": order.shipping_address.state,
                "zip_code": order.shipping_address.zip_code,
                "country": order.shipping_address.country,
            },
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

        # Add items
        for item in order.items:
            item_model = OrderItemModel(
                id=item.id,
                order_id=order.id.value,
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price.amount,
                currency=item.price.currency,
                quantity=item.quantity,
            )
            model.items.append(item_model)

        return model


