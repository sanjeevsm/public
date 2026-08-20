from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.models.base import PyObjectId


CategoryType = Literal["income", "expense", "asset", "liability", "both"]


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: CategoryType
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = Field(None, max_length=200)
    is_default: bool = False


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[CategoryType] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = Field(None, max_length=200)


class CategoryInDB(CategoryBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: Optional[PyObjectId] = None
    entity_id: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: CategoryType
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    is_default: bool
    user_id: Optional[str] = None
    entity_id: Optional[str] = None
    created_at: datetime
