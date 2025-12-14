"""Email service interface."""

from abc import ABC, abstractmethod
from typing import Optional


class EmailService(ABC):
    """Email service interface for sending emails."""

    @abstractmethod
    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body

        Returns:
            True if email was sent successfully, False otherwise
        """
        pass


