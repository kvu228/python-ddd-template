"""User ORM models for PostgreSQL."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from src.infrastructure.db_postgres.base import Base


class UserModel(Base):
    """User ORM model for PostgreSQL."""

    __tablename__ = "users"

    id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(String(10), default="true", nullable=False)  # Stored as string for compatibility
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<UserModel(id={self.id}, email={self.email})>"

