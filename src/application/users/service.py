"""User application service."""

import logging
from typing import List, Optional
from uuid import UUID

from src.application.users.commands import (
    ActivateUserCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from src.application.users.dto import CreateUserDTO, UpdateUserDTO, UserDTO
from src.application.users.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    SearchUsersQuery,
)
from src.domain.users.entities import User
from src.domain.users.exceptions import (
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from src.domain.users.value_objects import Email, UserId
from src.ports.external.messaging_service import MessagingService
from src.ports.users.user_cache import UserCache
from src.ports.users.user_read_model import UserReadModel
from src.ports.users.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserApplicationService:
    """Application service for user use cases.

    This service orchestrates user-related operations, coordinating
    between domain entities, repositories, and external services.

    Example:
        >>> service = UserApplicationService(
        ...     user_repository=...,
        ...     user_read_model=...,
        ...     user_cache=...,
        ...     messaging_service=...
        ... )
        >>> user_dto = service.create_user(CreateUserCommand(...))
    """

    def __init__(
        self,
        user_repository: UserRepository,
        user_read_model: UserReadModel,
        user_cache: UserCache,
        messaging_service: MessagingService,
        cache_ttl: int = 3600,
    ) -> None:
        """Initialize user application service.

        Args:
            user_repository: User repository (write model)
            user_read_model: User read model (read model)
            user_cache: User cache
            messaging_service: Messaging service for events
            cache_ttl: Cache TTL in seconds
        """
        self._user_repository = user_repository
        self._user_read_model = user_read_model
        self._user_cache = user_cache
        self._messaging_service = messaging_service
        self._cache_ttl = cache_ttl

    def create_user(self, command: CreateUserCommand) -> UserDTO:
        """Create a new user.

        Args:
            command: Create user command

        Returns:
            Created user DTO

        Raises:
            UserEmailAlreadyExistsError: If email already exists
        """
        email = Email(command.email)

        # Check if user already exists
        existing_user = self._user_repository.get_by_email(email)
        if existing_user:
            raise UserEmailAlreadyExistsError(f"Email {email} already exists")

        # Create domain entity
        user_id = UserId.generate()
        user = User.create(user_id, email, command.name)

        # Save to write model
        self._user_repository.add(user)

        # Publish domain events
        events = user.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Create read model (async would be better, but sync for now)
        user_dto = self._to_dto(user)
        try:
            self._user_read_model.create(self._to_read_model_dict(user_dto))
        except Exception as e:
            logger.error(f"Failed to create read model: {e}")

        # Cache user
        self._user_cache.set(
            user_id, self._to_cache_dict(user_dto), self._cache_ttl
        )

        logger.info(f"User created: {user_id}")
        return user_dto

    def get_user(self, query: GetUserByIdQuery) -> Optional[UserDTO]:
        """Get user by ID.

        Args:
            query: Get user query

        Returns:
            User DTO if found, None otherwise
        """
        user_id = UserId(query.user_id)

        # Try cache first
        cached = self._user_cache.get(user_id)
        if cached:
            return self._from_cache_dict(cached)

        # Try read model
        read_data = self._user_read_model.get_by_id(user_id)
        if read_data:
            user_dto = self._from_read_model_dict(read_data)
            # Cache it
            self._user_cache.set(
                user_id, self._to_cache_dict(user_dto), self._cache_ttl
            )
            return user_dto

        # Fallback to write model
        user = self._user_repository.get_by_id(user_id)
        if user:
            user_dto = self._to_dto(user)
            # Cache it
            self._user_cache.set(
                user_id, self._to_cache_dict(user_dto), self._cache_ttl
            )
            return user_dto

        return None

    def get_user_by_email(self, query: GetUserByEmailQuery) -> Optional[UserDTO]:
        """Get user by email.

        Args:
            query: Get user by email query

        Returns:
            User DTO if found, None otherwise
        """
        email = Email(query.email)
        user = self._user_repository.get_by_email(email)
        if user:
            return self._to_dto(user)
        return None

    def update_user(self, command: UpdateUserCommand) -> UserDTO:
        """Update a user.

        Args:
            command: Update user command

        Returns:
            Updated user DTO

        Raises:
            UserNotFoundError: If user is not found
        """
        user_id = UserId(command.user_id)
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Update domain entity
        if command.name:
            user.update_name(command.name)
        if command.email:
            new_email = Email(command.email)
            # Check if email already exists (if different)
            if user.email != new_email:
                existing = self._user_repository.get_by_email(new_email)
                if existing:
                    raise UserEmailAlreadyExistsError(
                        f"Email {new_email} already exists"
                    )
            user.update_email(new_email)

        # Save to write model
        self._user_repository.update(user)

        # Publish domain events
        events = user.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        # Update read model
        user_dto = self._to_dto(user)
        try:
            self._user_read_model.update(
                user_id, self._to_read_model_dict(user_dto)
            )
        except Exception as e:
            logger.error(f"Failed to update read model: {e}")

        # Update cache
        self._user_cache.set(
            user_id, self._to_cache_dict(user_dto), self._cache_ttl
        )

        logger.info(f"User updated: {user_id}")
        return user_dto

    def delete_user(self, command: DeleteUserCommand) -> None:
        """Delete a user.

        Args:
            command: Delete user command

        Raises:
            UserNotFoundError: If user is not found
        """
        user_id = UserId(command.user_id)
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Delete from write model
        self._user_repository.delete(user_id)

        # Delete from read model
        try:
            self._user_read_model.delete(user_id)
        except Exception as e:
            logger.error(f"Failed to delete read model: {e}")

        # Delete from cache
        self._user_cache.delete(user_id)

        logger.info(f"User deleted: {user_id}")

    def activate_user(self, command: ActivateUserCommand) -> UserDTO:
        """Activate a user.

        Args:
            command: Activate user command

        Returns:
            Updated user DTO

        Raises:
            UserNotFoundError: If user is not found
        """
        user_id = UserId(command.user_id)
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user.activate()
        self._user_repository.update(user)

        # Publish domain events
        events = user.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        user_dto = self._to_dto(user)
        self._user_cache.set(
            user_id, self._to_cache_dict(user_dto), self._cache_ttl
        )

        return user_dto

    def deactivate_user(self, command: DeactivateUserCommand) -> UserDTO:
        """Deactivate a user.

        Args:
            command: Deactivate user command

        Returns:
            Updated user DTO

        Raises:
            UserNotFoundError: If user is not found
        """
        user_id = UserId(command.user_id)
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user.deactivate()
        self._user_repository.update(user)

        # Publish domain events
        events = user.get_domain_events()
        for event in events:
            self._messaging_service.publish_event(
                event["event_type"], event["data"]
            )

        user_dto = self._to_dto(user)
        self._user_cache.set(
            user_id, self._to_cache_dict(user_dto), self._cache_ttl
        )

        return user_dto

    def search_users(self, query: SearchUsersQuery) -> List[UserDTO]:
        """Search users.

        Args:
            query: Search users query

        Returns:
            List of user DTOs
        """
        # Use read model for search
        if query.email:
            read_data_list = self._user_read_model.search_by_email(query.email)
            return [
                self._from_read_model_dict(data) for data in read_data_list
            ]

        # For more complex queries, would need to extend read model
        return []

    def _to_dto(self, user: User) -> UserDTO:
        """Convert User entity to DTO."""
        return UserDTO(
            id=user.id.value,
            email=str(user.email),
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _to_read_model_dict(self, dto: UserDTO) -> dict:
        """Convert DTO to read model dictionary."""
        return {
            "id": str(dto.id),
            "email": dto.email,
            "name": dto.name,
            "is_active": dto.is_active,
            "created_at": dto.created_at.isoformat(),
            "updated_at": dto.updated_at.isoformat(),
        }

    def _from_read_model_dict(self, data: dict) -> UserDTO:
        """Convert read model dictionary to DTO."""
        from datetime import datetime

        return UserDTO(
            id=UUID(data["id"]),
            email=data["email"],
            name=data["name"],
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def _to_cache_dict(self, dto: UserDTO) -> dict:
        """Convert DTO to cache dictionary."""
        return {
            "id": str(dto.id),
            "email": dto.email,
            "name": dto.name,
            "is_active": dto.is_active,
            "created_at": dto.created_at.isoformat(),
            "updated_at": dto.updated_at.isoformat(),
        }

    def _from_cache_dict(self, data: dict) -> UserDTO:
        """Convert cache dictionary to DTO."""
        from datetime import datetime

        return UserDTO(
            id=UUID(data["id"]),
            email=data["email"],
            name=data["name"],
            is_active=data["is_active"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

