"""Redis client configuration."""

import redis
from redis import Redis

from src.config.settings import settings

# Create Redis client
redis_client: Redis = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


def get_redis_client() -> Redis:
    """Get Redis client instance.

    Returns:
        Redis client
    """
    return redis_client


