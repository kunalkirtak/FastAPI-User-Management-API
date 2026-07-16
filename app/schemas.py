"""
Pydantic schemas.

These define the shape of data coming in (requests) and going out
(responses) for the `/users` endpoints, independently of the SQLAlchemy
model. Keeping them separate from `models.py` means the API's public
contract can evolve without being tied 1:1 to the database schema (and it
guarantees fields like `hashed_password` are never accidentally returned).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.validators import (
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    validate_password_strength,
    validate_username,
)


# ------------------------------------------------------------------------------------
# Base / shared schema
# ------------------------------------------------------------------------------------
class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        json_schema_extra={"example": "johndoe"},
    )
    email: EmailStr = Field(..., json_schema_extra={"example": "johndoe@example.com"})
    full_name: Optional[str] = Field(
        None, max_length=100, json_schema_extra={"example": "John Doe"}
    )

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        return validate_username(v)


# ------------------------------------------------------------------------------------
# Create
# ------------------------------------------------------------------------------------
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=128,
        json_schema_extra={"example": "S3curePass!"},
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        return validate_password_strength(v)


# ------------------------------------------------------------------------------------
# Update (all fields optional -- only supplied fields are changed)
# ------------------------------------------------------------------------------------
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=PASSWORD_MIN_LENGTH, max_length=128)
    is_active: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_username(v)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_password_strength(v)


# ------------------------------------------------------------------------------------
# Response
# ------------------------------------------------------------------------------------
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Allows creating this schema directly from a SQLAlchemy model instance,
    # e.g. `UserResponse.model_validate(db_user)`.
    model_config = ConfigDict(from_attributes=True)
