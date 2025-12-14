"""Order-related Celery tasks."""

import logging
from uuid import UUID

from src.domain.orders.value_objects import OrderId
from src.infrastructure.db_mongo.client import get_mongo_database
from src.infrastructure.db_mongo.order_read_model_impl import (
    MongoDBOrderReadModel,
)
from src.infrastructure.db_postgres.base import SessionLocal
from src.infrastructure.db_postgres.order_repository_impl import (
    PostgreSQLOrderRepository,
)
from src.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.orders.tasks.process_payment")
def process_payment(order_id: str, payment_method: str) -> bool:
    """Process payment for an order.

    Args:
        order_id: Order ID
        payment_method: Payment method (e.g., 'credit_card', 'paypal')

    Returns:
        True if payment was processed successfully, False otherwise
    """
    try:
        db = SessionLocal()
        try:
            order_repo = PostgreSQLOrderRepository(db)
            order = order_repo.get_by_id(OrderId(UUID(order_id)))
            if not order:
                logger.error(f"Order {order_id} not found")
                return False

            # Simulate payment processing
            logger.info(
                f"Processing payment for order {order_id} "
                f"using {payment_method}"
            )

            # In a real implementation, this would call a payment gateway
            # For now, just log it
            logger.info(f"Payment processed successfully for order {order_id}")
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to process payment for order {order_id}: {e}")
        return False


@celery_app.task(name="workers.orders.tasks.sync_order_to_read_model")
def sync_order_to_read_model(order_id: str) -> bool:
    """Sync order to read model (MongoDB).

    Args:
        order_id: Order ID

    Returns:
        True if sync was successful, False otherwise
    """
    try:
        db = SessionLocal()
        try:
            order_repo = PostgreSQLOrderRepository(db)
            order = order_repo.get_by_id(OrderId(UUID(order_id)))
            if not order:
                logger.error(f"Order {order_id} not found")
                return False

            # Convert to DTO and sync to read model
            from src.application.orders.service import OrderApplicationService
            from src.infrastructure.external.messaging_service_impl import (
                RedisMessagingService,
            )

            order_read_model = MongoDBOrderReadModel(get_mongo_database())
            messaging_service = RedisMessagingService()

            service = OrderApplicationService(
                order_repository=order_repo,
                order_read_model=order_read_model,
                messaging_service=messaging_service,
            )

            order_dto = service.get_order(UUID(order_id))
            if order_dto:
                order_read_model.update(
                    OrderId(UUID(order_id)),
                    service._to_read_model_dict(order_dto),
                )
                logger.info(f"Order {order_id} synced to read model")
                return True
            return False
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to sync order {order_id} to read model: {e}")
        return False


