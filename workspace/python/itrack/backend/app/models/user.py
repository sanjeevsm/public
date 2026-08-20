from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from app.models.base import PyObjectId


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    # Accept either username or email for login
    identifier: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., max_length=200)


class UserInDB(UserBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    password_hash: str
    entity_id: Optional[PyObjectId] = None
    entity_role: Optional[str] = None
    is_superadmin: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    entity_role: Optional[str] = None
    is_superadmin: bool | None = False
    created_at: datetime


class UserUpdate(BaseModel):
    """Fields the current user can change on their own profile."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    current_password: Optional[str] = Field(None, max_length=200)
    new_password: Optional[str] = Field(None, min_length=8, max_length=100)


class AdminUserUpdate(BaseModel):
    """Fields an entity admin can change on a member's profile (no password)."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
