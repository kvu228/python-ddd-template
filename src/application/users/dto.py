"""User DTOs (Data Transfer Objects)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CreateUserDTO:
    """DTO for creating a user.

    Example:
        >>> dto = CreateUserDTO(
        ...     email="user@example.com",
        ...     name="John Doe"
        ... )
    """

    email: str
    name: str


@dataclass
class UpdateUserDTO:
    """DTO for updating a user."""

    name: Optional[str] = None
    email: Optional[str] = None


@dataclass
class UserDTO:
    """DTO for user data.

    Example:
        >>> user_dto = UserDTO(
        ...     id=UUID("..."),
        ...     email="user@example.com",
        ...     name="John Doe",
        ...     is_active=True,
        ...     created_at=datetime.utcnow()
        ... )
    """

    id: UUID
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


