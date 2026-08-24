from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.models.base import PyObjectId


EntityType = Literal["Home", "Office", "Custom"]
MemberRole = Literal["admin", "member"]


class EntityMember(BaseModel):
    user_id: str
    role: MemberRole
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    entity_type: EntityType
    custom_type_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class EntityCreate(EntityBase):
    pass


class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    entity_type: Optional[EntityType] = None
    custom_type_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    entity_type: EntityType
    custom_type_name: Optional[str] = None
    description: Optional[str] = None
    members: List[EntityMember]
    created_by: str
    created_at: datetime
    member_count: int


class EntityMemberResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: MemberRole
    joined_at: datetime


class EntityInviteRequest(BaseModel):
    user_email: str
    role: MemberRole = "member"


class EntitySummary(BaseModel):
    entity_id: str
    entity_name: str
    total_balance: float
    total_income: float
    total_expense: float
    total_assets: float = 0.0
    total_liabilities: float = 0.0
    net_worth: float = 0.0
    shared_balance: float
    shared_income: float
    shared_expense: float
    shared_assets: float = 0.0
    shared_liabilities: float = 0.0
    transaction_count: int
    shared_transaction_count: int
    categories_breakdown: dict[str, float]
    member_breakdown: dict[str, dict]
