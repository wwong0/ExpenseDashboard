from pydantic import BaseModel, ConfigDict, Field, conint
from typing import List, Optional, Set
from decimal import Decimal
import datetime

# --- Input Schemas ---
# These schemas are used to validate incoming request data.

class AuthSchema(BaseModel):
    """Schema for validating user registration and login data."""
    username: str
    password: str

class CreateExpenseSchema(BaseModel):
    """Schema for validating data when creating a new expense."""
    name : str
    amount: Decimal
    description: Optional[str] = None
    category_id: Optional[int] = None
    active_status: bool = True
    merchant: Optional[str] = None
    date: datetime.date = Field(default_factory=datetime.date.today)
    tag_ids: set[int] = Field(default_factory=set)


class UpdateExpenseSchema(BaseModel):
    """
    Schema for validating data when updating an expense.
    All fields are optional, allowing for partial updates.
    """
    name : Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    active_status: Optional[bool] = None
    date: Optional[datetime.date] = None
    tag_ids: Optional[set[int]] = None

class TagLookupSchema(BaseModel):
    tag_ids: Set[int]

class CreateIncomeSchema(BaseModel):
    """Schema for validating data when creating a new income."""
    source: str
    amount: Decimal
    date: datetime.date = Field(default_factory=datetime.date.today)
    description: Optional[str] = None

class UpdateIncomeSchema(BaseModel):
    """Schema for validating data when updating an income."""
    source: Optional[str] = None
    amount: Optional[Decimal] = None
    date: Optional[datetime.date] = None
    description: Optional[str] = Field(default=None)

class CreateBudgetSchema(BaseModel):
    """Schema for validating data when creating a new budget."""
    amount: Decimal
    year: conint(ge=1900, le=2200)
    month: conint(ge=1, le=12)
    category_id: Optional[int] = None

class UpdateBudgetSchema(BaseModel):
    """Schema for validating data when updating a budget."""
    amount: Optional[Decimal] = None
    year: Optional[conint(ge=1900, le=2200)] = None
    month: Optional[conint(ge=1, le=12)] = None
    category_id: Optional[int] = None

# --- Response Schemas ---
# These schemas are used to serialize data for outgoing responses.

class TagResponseSchema(BaseModel):
    """Schema for serializing Tag model data."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryResponseSchema(BaseModel):
    """Schema for serializing Category model data."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExpenseResponseSchema(BaseModel):
    """Schema for serializing Expense model data, including nested objects."""
    id: int
    name: str
    amount: Decimal
    description: Optional[str]
    date: datetime.date
    active_status: bool
    merchant: Optional[str]
    category: Optional[CategoryResponseSchema]
    tags: List[TagResponseSchema]

    model_config = ConfigDict(from_attributes=True)

class IncomeResponseSchema(BaseModel):
    """Schema for serializing Income model data."""
    id: int
    source: str
    amount: Decimal
    date: datetime.date
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class BudgetResponseSchema(BaseModel):
    """Schema for serializing Budget model data."""
    id: int
    amount: Decimal
    year: int
    month: int
    category: Optional[CategoryResponseSchema] # A budget can exist without a category

    model_config = ConfigDict(from_attributes=True)