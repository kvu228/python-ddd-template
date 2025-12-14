"""Order application service."""

import logging
from typing import List, Optional
from uuid import UUID

from src.application.orders.commands import (
    AddOrderItemCommand,
    CancelOrderCommand,
    ConfirmOrderCommand,
    CreateOrderCommand,
    RemoveOrderItemCommand,
)
from src.application.orders.dto import (
    AddOrderItemDTO,
    OrderDTO,
    OrderItemDTO,
    ShippingAddressDTO,
)
from src.domain.orders.entities import Order, OrderItem
from src.domain.orders.exceptions import OrderNotFoundError
from src.domain.orders.value_objects import (
    Money,
    OrderId,
    OrderStatus,
    ShippingAddress,
)
from src.domain.users.value_objects import UserId
from src.ports.external.messaging_service import MessagingService
from src.ports.orders.order_read_model import OrderReadModel
from src.ports.orders.order_repository import OrderRepository

logger = logging.getLogger(__name__)


class OrderApplicationService:
    """Application service for order use cases.

    This service orchestrates order-related operations, coordinating
    between domain entities, repositories, and external services.

    Example:
        >>> service = OrderApplicationService(
        ...     order_repository=...,
        ...     order_read_model=...,
        ...     messaging_service=...
        ... )
        >>> order_dto = service.create_order(CreateOrderCommand(...))
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        order_read_model: OrderReadModel,
        messaging_service: MessagingService,
    ) -> None:
        """Initialize order application service.

        Args:
            order_repository: Order repository (write model)
            order_read_model: Order read model (read model)
            messaging_service: Messaging service for events
        """
        self._order_repository = order_repository
        self._order_read_model = order_read_model
        self._messaging_service = messaging_service

    def create_order(self, command: CreateOrderCommand) -> OrderDTO:
        """Create a new order.

        Args:
            command: Create order command

        Returns:
            Created order DTO
        """
        order_id = OrderId.generate()
        user_id = UserId(command.user_id)

        shipping_address = ShippingAddress(
            street=command.shipping_address.street,
            city=command.shipping_address.city,
            state=command.shipping_address.state,
            zip_code=command.shipping_address.zip_code,
            country=command.shipping_address.country,
        )

        # Create domain entity
        order = Order.create(order_id, user_id, shipping_address)

        # Save to write model
        self._order_repository.add(order)

        # Publish domain events
        events = order.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Create read model
        order_dto = self._to_dto(order)
        try:
            self._order_read_model.create(self._to_read_model_dict(order_dto))
        except Exception as e:
            logger.error(f"Failed to create read model: {e}")

        logger.info(f"Order created: {order_id}")
        return order_dto

    def get_order(self, order_id: UUID) -> Optional[OrderDTO]:
        """Get order by ID.

        Args:
            order_id: Order identifier

        Returns:
            Order DTO if found, None otherwise
        """
        oid = OrderId(order_id)

        # Try read model first
        read_data = self._order_read_model.get_by_id(oid)
        if read_data:
            return self._from_read_model_dict(read_data)

        # Fallback to write model
        order = self._order_repository.get_by_id(oid)
        if order:
            return self._to_dto(order)

        return None

    def add_item_to_order(self, command: AddOrderItemCommand) -> OrderDTO:
        """Add an item to an order.

        Args:
            command: Add order item command

        Returns:
            Updated order DTO

        Raises:
            OrderNotFoundError: If order is not found
        """
        order_id = OrderId(command.order_id)
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        # Create order item
        price = Money(command.price, command.currency)
        item = OrderItem.create(
            product_id=command.product_id,
            product_name=command.product_name,
            price=price,
            quantity=command.quantity,
        )

        # Add to order
        order.add_item(item)

        # Save to write model
        self._order_repository.update(order)

        # Publish domain events
        events = order.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Update read model
        order_dto = self._to_dto(order)
        try:
            self._order_read_model.update(
                order_id, self._to_read_model_dict(order_dto)
            )
        except Exception as e:
            logger.error(f"Failed to update read model: {e}")

        logger.info(f"Item added to order: {order_id}")
        return order_dto

    def remove_item_from_order(
        self, command: RemoveOrderItemCommand
    ) -> OrderDTO:
        """Remove an item from an order.

        Args:
            command: Remove order item command

        Returns:
            Updated order DTO

        Raises:
            OrderNotFoundError: If order is not found
        """
        order_id = OrderId(command.order_id)
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        # Remove item
        order.remove_item(command.item_id)

        # Save to write model
        self._order_repository.update(order)

        # Publish domain events
        events = order.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Update read model
        order_dto = self._to_dto(order)
        try:
            self._order_read_model.update(
                order_id, self._to_read_model_dict(order_dto)
            )
        except Exception as e:
            logger.error(f"Failed to update read model: {e}")

        logger.info(f"Item removed from order: {order_id}")
        return order_dto

    def confirm_order(self, command: ConfirmOrderCommand) -> OrderDTO:
        """Confirm an order.

        Args:
            command: Confirm order command

        Returns:
            Updated order DTO

        Raises:
            OrderNotFoundError: If order is not found
        """
        order_id = OrderId(command.order_id)
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        # Confirm order
        order.confirm()

        # Save to write model
        self._order_repository.update(order)

        # Publish domain events
        events = order.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Update read model
        order_dto = self._to_dto(order)
        try:
            self._order_read_model.update(
                order_id, self._to_read_model_dict(order_dto)
            )
        except Exception as e:
            logger.error(f"Failed to update read model: {e}")

        logger.info(f"Order confirmed: {order_id}")
        return order_dto

    def cancel_order(self, command: CancelOrderCommand) -> OrderDTO:
        """Cancel an order.

        Args:
            command: Cancel order command

        Returns:
            Updated order DTO

        Raises:
            OrderNotFoundError: If order is not found
        """
        order_id = OrderId(command.order_id)
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        # Cancel order
        order.cancel()

        # Save to write model
        self._order_repository.update(order)

        # Publish domain events
        events = order.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Update read model
        order_dto = self._to_dto(order)
        try:
            self._order_read_model.update(
                order_id, self._to_read_model_dict(order_dto)
            )
        except Exception as e:
            logger.error(f"Failed to update read model: {e}")

        logger.info(f"Order cancelled: {order_id}")
        return order_dto

    def get_orders_by_user(self, user_id: UUID) -> List[OrderDTO]:
        """Get orders by user ID.

        Args:
            user_id: User identifier

        Returns:
            List of order DTOs
        """
        uid = UserId(user_id)

        # Try read model first
        read_data_list = self._order_read_model.get_by_user_id(uid)
        if read_data_list:
            return [
                self._from_read_model_dict(data) for data in read_data_list
            ]

        # Fallback to write model
        orders = self._order_repository.get_by_user_id(uid)
        return [self._to_dto(order) for order in orders]

    def _to_dto(self, order: Order) -> OrderDTO:
        """Convert Order entity to DTO."""
        total = order.calculate_total()
        return OrderDTO(
            id=order.id.value,
            user_id=order.user_id.value,
            status=order.status.value,
            shipping_address=ShippingAddressDTO(
                street=order.shipping_address.street,
                city=order.shipping_address.city,
                state=order.shipping_address.state,
                zip_code=order.shipping_address.zip_code,
                country=order.shipping_address.country,
            ),
            items=[
                OrderItemDTO(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=item.price.amount,
                    currency=item.price.currency,
                    quantity=item.quantity,
                )
                for item in order.items
            ],
            total_amount=total.amount,
            total_currency=total.currency,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    def _to_read_model_dict(self, dto: OrderDTO) -> dict:
        """Convert DTO to read model dictionary."""
        return {
            "id": str(dto.id),
            "user_id": str(dto.user_id),
            "status": dto.status,
            "shipping_address": {
                "street": dto.shipping_address.street,
                "city": dto.shipping_address.city,
                "state": dto.shipping_address.state,
                "zip_code": dto.shipping_address.zip_code,
                "country": dto.shipping_address.country,
            },
            "items": [
                {
                    "id": str(item.id),
                    "product_id": str(item.product_id),
                    "product_name": item.product_name,
                    "price": str(item.price),
                    "currency": item.currency,
                    "quantity": item.quantity,
                }
                for item in dto.items
            ],
            "total_amount": str(dto.total_amount),
            "total_currency": dto.total_currency,
            "created_at": dto.created_at.isoformat(),
            "updated_at": dto.updated_at.isoformat(),
        }

    def _from_read_model_dict(self, data: dict) -> OrderDTO:
        """Convert read model dictionary to DTO."""
        from datetime import datetime
        from decimal import Decimal

        return OrderDTO(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            status=data["status"],
            shipping_address=ShippingAddressDTO(**data["shipping_address"]),
            items=[
                OrderItemDTO(
                    id=UUID(item["id"]),
                    product_id=UUID(item["product_id"]),
                    product_name=item["product_name"],
                    price=Decimal(item["price"]),
                    currency=item["currency"],
                    quantity=item["quantity"],
                )
                for item in data["items"]
            ],
            total_amount=Decimal(data["total_amount"]),
            total_currency=data["total_currency"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


