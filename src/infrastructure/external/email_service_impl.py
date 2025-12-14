"""Email service implementation."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.config.settings import settings
from src.ports.external.email_service import EmailService

logger = logging.getLogger(__name__)


class SMTPEmailService(EmailService):
    """SMTP implementation of EmailService."""

    def __init__(self) -> None:
        """Initialize email service."""
        self._smtp_host = settings.SMTP_HOST
        self._smtp_port = settings.SMTP_PORT
        self._smtp_user = settings.SMTP_USER
        self._smtp_password = settings.SMTP_PASSWORD
        self._smtp_use_tls = settings.SMTP_USE_TLS
        self._from_email = settings.EMAIL_FROM

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email.

        If SMTP is not configured, logs the email instead.
        """
        if not self._smtp_host:
            logger.info(
                f"Email not sent (SMTP not configured): "
                f"To: {to_email}, Subject: {subject}"
            )
            return True  # Return True for development

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self._from_email or self._smtp_user or "noreply@shop.com"
            msg["To"] = to_email

            # Add plain text part
            part1 = MIMEText(body, "plain")
            msg.attach(part1)

            # Add HTML part if provided
            if html_body:
                part2 = MIMEText(html_body, "html")
                msg.attach(part2)

            # Send email
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                if self._smtp_use_tls:
                    server.starttls()
                if self._smtp_user and self._smtp_password:
                    server.login(self._smtp_user, self._smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


