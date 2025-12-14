"""User API routes."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.users.commands import (
    CreateUserCommand,
    DeleteUserCommand,
    GetUserByIdQuery,
    GetUserByEmailQuery,
    SearchUsersQuery,
    UpdateUserCommand,
)
from src.domain.users.exceptions import (
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from src.application.users.service import UserApplicationService
from src.interfaces.api.dependencies import get_user_service
from src.interfaces.api.users.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    request: CreateUserRequest,
    service: UserApplicationService = Depends(get_user_service),
) -> UserResponse:
    """Register a new user.

    Args:
        request: User registration data
        service: User application service

    Returns:
        Created user data

    Raises:
        HTTPException: If email already exists
    """
    try:
        command = CreateUserCommand(email=request.email, name=request.name)
        user_dto = service.create_user(command)
        return UserResponse(**user_dto.__dict__)
    except UserEmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
async def get_user(
    user_id: UUID,
    service: UserApplicationService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID.

    Args:
        user_id: User identifier
        service: User application service

    Returns:
        User data

    Raises:
        HTTPException: If user is not found
    """
    query = GetUserByIdQuery(user_id=user_id)
    user_dto = service.get_user(query)
    if not user_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse(**user_dto.__dict__)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    service: UserApplicationService = Depends(get_user_service),
) -> UserResponse:
    """Update user information.

    Args:
        user_id: User identifier
        request: Update user data
        service: User application service

    Returns:
        Updated user data

    Raises:
        HTTPException: If user is not found or email already exists
    """
    try:
        command = UpdateUserCommand(
            user_id=user_id, name=request.name, email=request.email
        )
        user_dto = service.update_user(command)
        return UserResponse(**user_dto.__dict__)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except UserEmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete_user(
    user_id: UUID,
    service: UserApplicationService = Depends(get_user_service),
) -> None:
    """Delete a user.

    Args:
        user_id: User identifier
        service: User application service

    Raises:
        HTTPException: If user is not found
    """
    try:
        command = DeleteUserCommand(user_id=user_id)
        service.delete_user(command)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.get(
    "/search",
    response_model=List[UserResponse],
    summary="Search users",
)
async def search_users(
    email: str = Query(None, description="Email to search (partial match)"),
    service: UserApplicationService = Depends(get_user_service),
) -> List[UserResponse]:
    """Search users by email.

    Args:
        email: Email to search (partial match)
        service: User application service

    Returns:
        List of matching users
    """
    query = SearchUsersQuery(email=email)
    user_dtos = service.search_users(query)
    return [UserResponse(**dto.__dict__) for dto in user_dtos]

