"""FastAPI dependencies for dependency injection."""

from sqlalchemy.orm import Session

from src.application.orders.service import OrderApplicationService
from src.application.users.service import UserApplicationService
from src.config.settings import settings
from src.infrastructure.db_postgres.base import get_db_session
from src.infrastructure.db_mongo.client import get_mongo_database
from src.infrastructure.db_redis.client import get_redis_client
from src.infrastructure.db_mongo.order_read_model_impl import (
    MongoDBOrderReadModel,
)
from src.infrastructure.db_mongo.user_read_model_impl import MongoDBUserReadModel
from src.infrastructure.db_postgres.order_repository_impl import (
    PostgreSQLOrderRepository,
)
from src.infrastructure.db_postgres.user_repository_impl import (
    PostgreSQLUserRepository,
)
from src.infrastructure.db_redis.user_cache_impl import RedisUserCache
from src.infrastructure.external.email_service_impl import SMTPEmailService
from src.infrastructure.external.messaging_service_impl import (
    RedisMessagingService,
)


def get_user_service(db: Session = None) -> UserApplicationService:
    """Get user application service.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        UserApplicationService instance
    """
    if db is None:
        db = next(get_db_session())

    user_repository = PostgreSQLUserRepository(db)
    user_read_model = MongoDBUserReadModel(get_mongo_database())
    user_cache = RedisUserCache(get_redis_client())
    messaging_service = RedisMessagingService(get_redis_client())

    return UserApplicationService(
        user_repository=user_repository,
        user_read_model=user_read_model,
        user_cache=user_cache,
        messaging_service=messaging_service,
        cache_ttl=settings.USER_CACHE_TTL,
    )


def get_order_service(db: Session = None) -> OrderApplicationService:
    """Get order application service.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        OrderApplicationService instance
    """
    if db is None:
        db = next(get_db_session())

    order_repository = PostgreSQLOrderRepository(db)
    order_read_model = MongoDBOrderReadModel(get_mongo_database())
    messaging_service = RedisMessagingService(get_redis_client())

    return OrderApplicationService(
        order_repository=order_repository,
        order_read_model=order_read_model,
        messaging_service=messaging_service,
    )


def get_email_service() -> SMTPEmailService:
    """Get email service.

    Returns:
        SMTPEmailService instance
    """
    return SMTPEmailService()


