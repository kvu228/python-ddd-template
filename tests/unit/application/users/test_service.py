"""Unit tests for UserApplicationService."""

from unittest.mock import Mock

import pytest

from src.application.users.commands import CreateUserCommand
from src.application.users.service import UserApplicationService
from src.domain.users.exceptions import (
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from src.domain.users.value_objects import Email, UserId


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    return Mock()


@pytest.fixture
def mock_user_read_model():
    """Create a mock user read model."""
    return Mock()


@pytest.fixture
def mock_user_cache():
    """Create a mock user cache."""
    return Mock()


@pytest.fixture
def mock_messaging_service():
    """Create a mock messaging service."""
    return Mock()


@pytest.fixture
def user_service(
    mock_user_repository,
    mock_user_read_model,
    mock_user_cache,
    mock_messaging_service,
):
    """Create a user application service with mocks."""
    return UserApplicationService(
        user_repository=mock_user_repository,
        user_read_model=mock_user_read_model,
        user_cache=mock_user_cache,
        messaging_service=mock_messaging_service,
    )


def test_create_user_success(user_service, mock_user_repository):
    """Test creating a user successfully."""
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.add = Mock()

    command = CreateUserCommand(email="user@example.com", name="John Doe")
    user_dto = user_service.create_user(command)

    assert user_dto.email == "user@example.com"
    assert user_dto.name == "John Doe"
    mock_user_repository.add.assert_called_once()


def test_create_user_email_exists(user_service, mock_user_repository):
    """Test creating a user with existing email raises error."""
    from src.domain.users.entities import User
    from src.domain.users.value_objects import Email, UserId

    existing_user = User.create(
        UserId.generate(), Email("user@example.com"), "Existing User"
    )
    mock_user_repository.get_by_email.return_value = existing_user

    command = CreateUserCommand(email="user@example.com", name="John Doe")

    with pytest.raises(UserEmailAlreadyExistsError):
        user_service.create_user(command)

