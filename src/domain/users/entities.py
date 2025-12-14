"""User aggregate root entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.users.exceptions import InvalidUserDataError
from src.domain.users.value_objects import Email, UserId


@dataclass
class User:
    """User aggregate root.

    This is the aggregate root for the user domain. All operations
    on user data should go through this entity.

    Example:
        >>> user_id = UserId.generate()
        >>> email = Email("user@example.com")
        >>> user = User.create(user_id, email, "John Doe")
        >>> user.update_name("Jane Doe")
        >>> user.deactivate()
    """

    id: UserId
    email: Email
    name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _domain_events: List[dict] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        email: Email,
        name: str,
    ) -> "User":
        """Factory method to create a new user.

        Args:
            user_id: Unique user identifier
            email: User email address
            name: User full name

        Returns:
            New User instance

        Raises:
            InvalidUserDataError: If name is empty or invalid
        """
        if not name or not name.strip():
            raise InvalidUserDataError("User name cannot be empty")

        user = cls(
            id=user_id,
            email=email,
            name=name.strip(),
            is_active=True,
        )
        user._add_domain_event("user_registered", {"user_id": str(user.id)})
        return user

    def update_name(self, new_name: str) -> None:
        """Update user name.

        Args:
            new_name: New name for the user

        Raises:
            InvalidUserDataError: If name is empty or invalid
        """
        if not new_name or not new_name.strip():
            raise InvalidUserDataError("User name cannot be empty")

        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()
        self._add_domain_event("user_name_updated", {"user_id": str(self.id)})

    def update_email(self, new_email: Email) -> None:
        """Update user email.

        Args:
            new_email: New email address
        """
        self.email = new_email
        self.updated_at = datetime.utcnow()
        self._add_domain_event("user_email_updated", {"user_id": str(self.id)})

    def activate(self) -> None:
        """Activate the user."""
        if self.is_active:
            return

        self.is_active = True
        self.updated_at = datetime.utcnow()
        self._add_domain_event("user_activated", {"user_id": str(self.id)})

    def deactivate(self) -> None:
        """Deactivate the user."""
        if not self.is_active:
            return

        self.is_active = False
        self.updated_at = datetime.utcnow()
        self._add_domain_event("user_deactivated", {"user_id": str(self.id)})

    def _add_domain_event(self, event_type: str, data: dict) -> None:
        """Add a domain event.

        Args:
            event_type: Type of the event
            data: Event data
        """
        self._domain_events.append(
            {
                "event_type": event_type,
                "data": data,
                "occurred_at": datetime.utcnow().isoformat(),
            }
        )

    def get_domain_events(self) -> List[dict]:
        """Get and clear domain events.

        Returns:
            List of domain events
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)


