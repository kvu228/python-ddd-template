"""User domain services."""

from typing import Protocol

from src.domain.users.entities import User
from src.domain.users.value_objects import Email


class UserEmailUniquenessChecker(Protocol):
    """Protocol for checking email uniqueness."""

    def is_email_unique(self, email: Email) -> bool:
        """Check if email is unique.

        Args:
            email: Email to check

        Returns:
            True if email is unique, False otherwise
        """
        ...


class UserDomainService:
    """Domain service for user-related business logic."""

    def __init__(self, email_checker: UserEmailUniquenessChecker) -> None:
        """Initialize domain service.

        Args:
            email_checker: Service to check email uniqueness
        """
        self._email_checker = email_checker

    def validate_email_uniqueness(self, email: Email) -> None:
        """Validate that email is unique.

        Args:
            email: Email to validate

        Raises:
            ValueError: If email is not unique
        """
        if not self._email_checker.is_email_unique(email):
            raise ValueError(f"Email {email} already exists")


