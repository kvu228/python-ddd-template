"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings
from src.infrastructure.db_postgres.base import Base

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def user_repository(db_session):
    """Create a user repository for testing."""
    from src.infrastructure.db_postgres.user_repository_impl import (
        PostgreSQLUserRepository,
    )

    return PostgreSQLUserRepository(db_session)


@pytest.fixture
def order_repository(db_session):
    """Create an order repository for testing."""
    from src.infrastructure.db_postgres.order_repository_impl import (
        PostgreSQLOrderRepository,
    )

    return PostgreSQLOrderRepository(db_session)


