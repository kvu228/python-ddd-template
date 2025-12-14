"""User repository PostgreSQL implementation."""

from typing import Optional

from sqlalchemy.orm import Session

from src.domain.users.entities import User
from src.domain.users.value_objects import Email, UserId
from src.infrastructure.db_postgres.user_models import UserModel
from src.ports.users.user_repository import UserRepository


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL implementation of UserRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy database session
        """
        self._session = session

    def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        model = (
            self._session.query(UserModel)
            .filter(UserModel.id == user_id.value)
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        model = (
            self._session.query(UserModel)
            .filter(UserModel.email == str(email))
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def add(self, user: User) -> None:
        """Add a new user."""
        model = self._to_model(user)
        self._session.add(model)
        self._session.flush()

    def update(self, user: User) -> None:
        """Update an existing user."""
        model = (
            self._session.query(UserModel)
            .filter(UserModel.id == user.id.value)
            .first()
        )
        if model:
            model.email = str(user.email)
            model.name = user.name
            model.is_active = str(user.is_active).lower()
            model.updated_at = user.updated_at
            self._session.flush()

    def delete(self, user_id: UserId) -> None:
        """Delete a user."""
        model = (
            self._session.query(UserModel)
            .filter(UserModel.id == user_id.value)
            .first()
        )
        if model:
            self._session.delete(model)
            self._session.flush()

    def _to_entity(self, model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        from src.domain.users.entities import User

        return User(
            id=UserId(model.id),
            email=Email(model.email),
            name=model.name,
            is_active=model.is_active.lower() == "true",
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, user: User) -> UserModel:
        """Convert domain entity to ORM model."""
        return UserModel(
            id=user.id.value,
            email=str(user.email),
            name=user.name,
            is_active=str(user.is_active).lower(),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


