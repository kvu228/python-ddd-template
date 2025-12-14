"""User commands (CQRS pattern)."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.application.users.dto import CreateUserDTO, UpdateUserDTO


@dataclass
class CreateUserCommand:
    """Command to create a new user."""

    email: str
    name: str


@dataclass
class UpdateUserCommand:
    """Command to update a user."""

    user_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None


@dataclass
class DeleteUserCommand:
    """Command to delete a user."""

    user_id: UUID


@dataclass
class ActivateUserCommand:
    """Command to activate a user."""

    user_id: UUID


@dataclass
class DeactivateUserCommand:
    """Command to deactivate a user."""

    user_id: UUID


