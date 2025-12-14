"""User-related Celery tasks."""

import logging
from typing import Optional
from uuid import UUID

from src.infrastructure.db_postgres.base import SessionLocal
from src.infrastructure.db_postgres.user_repository_impl import (
    PostgreSQLUserRepository,
)
from src.infrastructure.external.email_service_impl import SMTPEmailService
from src.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.users.tasks.send_welcome_email")
def send_welcome_email(user_id: str, email: str) -> bool:
    """Send welcome email to newly registered user.

    Args:
        user_id: User ID
        email: User email address

    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        email_service = SMTPEmailService()
        subject = "Welcome to Shop Service!"
        body = f"Welcome! Your account has been created successfully."
        html_body = f"""
        <html>
            <body>
                <h1>Welcome to Shop Service!</h1>
                <p>Your account has been created successfully.</p>
                <p>User ID: {user_id}</p>
            </body>
        </html>
        """
        return email_service.send(to_email=email, subject=subject, body=body, html_body=html_body)
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")
        return False


@celery_app.task(name="workers.users.tasks.send_order_confirmation")
def send_order_confirmation(order_id: str) -> bool:
    """Send order confirmation email.

    Args:
        order_id: Order ID

    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        # Get order and user info from database
        db = SessionLocal()
        try:
            from src.domain.orders.value_objects import OrderId
            from src.infrastructure.db_postgres.order_repository_impl import (
                PostgreSQLOrderRepository,
            )

            order_repo = PostgreSQLOrderRepository(db)
            order = order_repo.get_by_id(OrderId(UUID(order_id)))
            if not order:
                logger.error(f"Order {order_id} not found")
                return False

            # Get user email
            from src.domain.users.value_objects import UserId
            from src.infrastructure.db_postgres.user_repository_impl import (
                PostgreSQLUserRepository,
            )

            user_repo = PostgreSQLUserRepository(db)
            user = user_repo.get_by_id(order.user_id)
            if not user:
                logger.error(f"User {order.user_id} not found")
                return False

            email_service = SMTPEmailService()
            subject = f"Order Confirmation - Order #{order_id[:8]}"
            body = f"Your order has been confirmed. Order ID: {order_id}"
            html_body = f"""
            <html>
                <body>
                    <h1>Order Confirmation</h1>
                    <p>Your order has been confirmed.</p>
                    <p>Order ID: {order_id}</p>
                    <p>Total: {order.calculate_total()}</p>
                </body>
            </html>
            """
            return email_service.send(
                to_email=str(user.email),
                subject=subject,
                body=body,
                html_body=html_body,
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to send order confirmation for {order_id}: {e}")
        return False


