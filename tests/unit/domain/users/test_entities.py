"""Unit tests for User entity."""

import pytest

from src.domain.users.entities import User
from src.domain.users.exceptions import InvalidUserDataError
from src.domain.users.value_objects import Email, UserId


def test_create_user():
    """Test creating a user."""
    user_id = UserId.generate()
    email = Email("user@example.com")
    user = User.create(user_id, email, "John Doe")

    assert user.id == user_id
    assert user.email == email
    assert user.name == "John Doe"
    assert user.is_active is True
    assert len(user.get_domain_events()) > 0


def test_create_user_with_empty_name():
    """Test creating a user with empty name raises error."""
    user_id = UserId.generate()
    email = Email("user@example.com")

    with pytest.raises(InvalidUserDataError):
        User.create(user_id, email, "")


def test_update_user_name():
    """Test updating user name."""
    user_id = UserId.generate()
    email = Email("user@example.com")
    user = User.create(user_id, email, "John Doe")

    user.update_name("Jane Doe")
    assert user.name == "Jane Doe"
    assert len(user.get_domain_events()) > 0


def test_update_user_email():
    """Test updating user email."""
    user_id = UserId.generate()
    email = Email("user@example.com")
    user = User.create(user_id, email, "John Doe")

    new_email = Email("newuser@example.com")
    user.update_email(new_email)
    assert user.email == new_email


def test_activate_user():
    """Test activating a user."""
    user_id = UserId.generate()
    email = Email("user@example.com")
    user = User.create(user_id, email, "John Doe")

    user.deactivate()
    assert user.is_active is False

    user.activate()
    assert user.is_active is True


def test_deactivate_user():
    """Test deactivating a user."""
    user_id = UserId.generate()
    email = Email("user@example.com")
    user = User.create(user_id, email, "John Doe")

    user.deactivate()
    assert user.is_active is False


def test_user_equality():
    """Test user equality based on ID."""
    user_id = UserId.generate()
    email = Email("user@example.com")
    user1 = User.create(user_id, email, "John Doe")
    user2 = User.create(user_id, email, "Jane Doe")

    assert user1 == user2
    assert hash(user1) == hash(user2)


