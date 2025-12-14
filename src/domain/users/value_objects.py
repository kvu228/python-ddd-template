"""User value objects."""

import re
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class UserId:
    """User ID value object."""

    value: UUID

    def __post_init__(self) -> None:
        """Validate user ID."""
        if not isinstance(self.value, UUID):
            raise ValueError("UserId must be a UUID")

    @classmethod
    def generate(cls) -> "UserId":
        """Generate a new UserId."""
        return cls(uuid4())

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate email format."""
        if not self.value:
            raise ValueError("Email cannot be empty")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def __str__(self) -> str:
        """String representation."""
        return self.value


