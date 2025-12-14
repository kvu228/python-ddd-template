"""User cache Redis implementation."""

import json
from typing import Optional

from redis import Redis

from src.domain.users.value_objects import UserId
from src.infrastructure.db_redis.client import get_redis_client
from src.ports.users.user_cache import UserCache


class RedisUserCache(UserCache):
    """Redis implementation of UserCache."""

    def __init__(self, redis_client: Optional[Redis] = None) -> None:
        """Initialize cache with Redis client.

        Args:
            redis_client: Redis client instance (defaults to global client)
        """
        self._redis = redis_client or get_redis_client()
        self._key_prefix = "user:"

    def get(self, user_id: UserId) -> Optional[dict]:
        """Get user from cache."""
        key = f"{self._key_prefix}{user_id.value}"
        data = self._redis.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, user_id: UserId, user_data: dict, ttl: int) -> None:
        """Set user in cache."""
        key = f"{self._key_prefix}{user_id.value}"
        self._redis.setex(key, ttl, json.dumps(user_data))

    def delete(self, user_id: UserId) -> None:
        """Delete user from cache."""
        key = f"{self._key_prefix}{user_id.value}"
        self._redis.delete(key)

    def clear(self) -> None:
        """Clear all user cache."""
        pattern = f"{self._key_prefix}*"
        keys = self._redis.keys(pattern)
        if keys:
            self._redis.delete(*keys)


