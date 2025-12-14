"""User API schemas (Pydantic models)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    """Request schema for creating a user."""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
            }
        }


class UpdateUserRequest(BaseModel):
    """Request schema for updating a user."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="User full name"
    )
    email: Optional[EmailStr] = Field(None, description="User email address")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.com",
            }
        }


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }


