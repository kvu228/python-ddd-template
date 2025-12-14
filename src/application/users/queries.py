"""User queries (CQRS pattern)."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class GetUserByIdQuery:
    """Query to get user by ID."""

    user_id: UUID


@dataclass
class GetUserByEmailQuery:
    """Query to get user by email."""

    email: str


@dataclass
class SearchUsersQuery:
    """Query to search users."""

    email: Optional[str] = None
    is_active: Optional[bool] = None
    limit: int = 100
    offset: int = 0


