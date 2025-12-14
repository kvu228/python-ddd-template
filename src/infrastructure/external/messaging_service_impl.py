"""Messaging service implementation using Redis."""

import json
import logging
from typing import Any, Dict

from redis import Redis

from src.infrastructure.db_redis.client import get_redis_client
from src.ports.external.messaging_service import MessagingService

logger = logging.getLogger(__name__)


class RedisMessagingService(MessagingService):
    """Redis implementation of MessagingService."""

    def __init__(self, redis_client: Redis = None) -> None:
        """Initialize messaging service with Redis client.

        Args:
            redis_client: Redis client instance (defaults to global client)
        """
        self._redis = redis_client or get_redis_client()
        self._channel_prefix = "events:"

    def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish a domain event to Redis pub/sub."""
        channel = f"{self._channel_prefix}{event_type}"
        message = {
            "event_type": event_type,
            "data": event_data,
        }
        try:
            self._redis.publish(channel, json.dumps(message))
            logger.info(f"Event published: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")


