from datetime import datetime, timezone
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.base import PyObjectId


TransactionType = Literal["income", "expense", "asset", "liability"]
TransactionMode = Literal["shared", "private"]


class TransactionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=50)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mode: TransactionMode = "private"
    currency: str = Field(default="USD", min_length=3, max_length=3)  # Currency code (USD, EUR, GBP, etc.)
    # Recurrence
    is_recurring: bool = False
    recurrence: Optional[Literal["monthly"]] = None
    recurrence_start: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v):
        return round(v, 2)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    date: Optional[datetime] = None
    mode: Optional[TransactionMode] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str
    amount: float
    type: TransactionType
    category: str
    date: datetime
    mode: TransactionMode
    currency: str
    created_at: datetime
    user_id: str
    username: Optional[str] = None
    entity_id: Optional[str] = None


class TransactionSummary(BaseModel):
    total_balance: float
    total_income: float
    total_expense: float
    total_assets: float
    total_liabilities: float
    net_worth: float  # (income - expense) + (assets - liabilities)
    income_count: int
    expense_count: int
    asset_count: int
    liability_count: int
    categories_breakdown: dict[str, float]
    currency: str  # Currency for this summary


class TransactionImportRow(BaseModel):
    description: str
    amount: float
    type: TransactionType
    category: str
    date: str
    currency: str = "USD"

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return round(v, 2)
