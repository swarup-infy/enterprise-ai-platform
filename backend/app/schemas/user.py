"""
User schemas.

Pydantic models for User API requests and responses.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==============================================================================
# Base
# ==============================================================================

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


# ==============================================================================
# Create
# ==============================================================================

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


# ==============================================================================
# Update
# ==============================================================================

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


# ==============================================================================
# Response
# ==============================================================================

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None


# ==============================================================================
# Login
# ==============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==============================================================================
# Token
# ==============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==============================================================================
# JWT Payload
# ==============================================================================

class TokenPayload(BaseModel):
    sub: str
    exp: int


__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "Token",
    "TokenPayload",
]