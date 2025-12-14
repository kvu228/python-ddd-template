"""Messaging service interface for event publishing."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class MessagingService(ABC):
    """Messaging service interface for publishing domain events."""

    @abstractmethod
    def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish a domain event.

        Args:
            event_type: Type of the event (e.g., 'user_registered')
            event_data: Event data dictionary
        """
        pass


