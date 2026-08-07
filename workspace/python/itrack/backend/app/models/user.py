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
    email: EmailStr
    password: str = Field(..., max_length=200)


class UserInDB(UserBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    password_hash: str
    entity_id: Optional[PyObjectId] = None
    entity_role: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    entity_id: Optional[str] = None
    entity_role: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
