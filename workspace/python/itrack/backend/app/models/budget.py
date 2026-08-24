from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.base import PyObjectId


BudgetPeriod = Literal["daily", "weekly", "monthly", "yearly"]
BudgetType = Literal["category", "total"]


class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    period: BudgetPeriod
    budget_type: BudgetType
    category: Optional[str] = Field(None, max_length=50)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    alert_threshold: float = Field(default=80.0, ge=0, le=100)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v):
        return round(v, 2)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[BudgetPeriod] = None
    budget_type: Optional[BudgetType] = None
    category: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class BudgetInDB(BudgetBase):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    entity_id: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    amount: float
    period: BudgetPeriod
    budget_type: BudgetType
    category: Optional[str] = None
    currency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    alert_threshold: float
    user_id: str
    entity_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BudgetProgress(BaseModel):
    budget_id: str
    budget_name: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_spent: float
    is_exceeded: bool
    is_alert: bool
    period: BudgetPeriod
    category: Optional[str] = None
    currency: str = "USD"
    days_remaining: Optional[int] = None
