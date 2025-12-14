"""Event handlers for domain events."""

import json
import logging
from typing import Any, Dict

from redis import Redis

from src.infrastructure.db_redis.client import get_redis_client
from src.workers.orders.tasks import process_payment, sync_order_to_read_model
from src.workers.users.tasks import send_order_confirmation, send_welcome_email

logger = logging.getLogger(__name__)


def handle_user_registered(event_data: Dict[str, Any]) -> None:
    """Handle user registered event.

    Args:
        event_data: Event data dictionary
    """
    try:
        user_id = event_data.get("user_id")
        if user_id:
            # Get user email from database
            from src.domain.users.value_objects import UserId
            from src.infrastructure.db_postgres.base import SessionLocal
            from src.infrastructure.db_postgres.user_repository_impl import (
                PostgreSQLUserRepository,
            )

            db = SessionLocal()
            try:
                user_repo = PostgreSQLUserRepository(db)
                user = user_repo.get_by_id(UserId(user_id))
                if user:
                    send_welcome_email.delay(str(user.id), str(user.email))
                    logger.info(f"Triggered welcome email for user {user_id}")
            finally:
                db.close()
    except Exception as e:
        logger.error(f"Failed to handle user_registered event: {e}")


def handle_order_created(event_data: Dict[str, Any]) -> None:
    """Handle order created event.

    Args:
        event_data: Event data dictionary
    """
    try:
        order_id = event_data.get("order_id")
        if order_id:
            sync_order_to_read_model.delay(order_id)
            logger.info(f"Triggered sync to read model for order {order_id}")
    except Exception as e:
        logger.error(f"Failed to handle order_created event: {e}")


def handle_order_confirmed(event_data: Dict[str, Any]) -> None:
    """Handle order confirmed event.

    Args:
        event_data: Event data dictionary
    """
    try:
        order_id = event_data.get("order_id")
        if order_id:
            send_order_confirmation.delay(order_id)
            process_payment.delay(order_id, "credit_card")
            logger.info(f"Triggered order confirmation tasks for order {order_id}")
    except Exception as e:
        logger.error(f"Failed to handle order_confirmed event: {e}")


def start_event_listener() -> None:
    """Start listening to domain events from Redis pub/sub."""
    redis_client: Redis = get_redis_client()
    pubsub = redis_client.pubsub()

    # Subscribe to event channels
    pubsub.psubscribe("events:*")

    logger.info("Event listener started")

    try:
        for message in pubsub.listen():
            if message["type"] == "pmessage":
                try:
                    data = json.loads(message["data"])
                    event_type = data.get("event_type")
                    event_data = data.get("data", {})

                    if event_type == "user_registered":
                        handle_user_registered(event_data)
                    elif event_type == "order_created":
                        handle_order_created(event_data)
                    elif event_type == "order_confirmed":
                        handle_order_confirmed(event_data)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
    except KeyboardInterrupt:
        logger.info("Event listener stopped")
    finally:
        pubsub.close()


