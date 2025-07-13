from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
import datetime

# --- Input Schemas ---
# These schemas are used to validate incoming request data.

class CreateExpenseSchema(BaseModel):
    """Schema for validating data when creating a new expense."""
    name : str
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None
    active_status: bool = True
    date: datetime.date = Field(default_factory=datetime.date.today)
    tag_ids: set[int] = Field(default_factory=set)

class UpdateExpenseSchema(BaseModel):
    """
    Schema for validating data when updating an expense.
    All fields are optional, allowing for partial updates.
    """
    name : Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    active_status: Optional[bool] = None
    date: Optional[datetime.date] = None
    tag_ids: Optional[set[int]] = None


class AuthSchema(BaseModel):
    """Schema for validating user registration and login data."""
    username: str
    password: str


# --- Response Schemas ---
# These schemas are used to serialize data for outgoing responses.

class TagResponseSchema(BaseModel):
    """Schema for serializing Tag model data."""
    id: int
    name: str


class CategoryResponseSchema(BaseModel):
    """Schema for serializing Category model data."""
    id: int
    name: str


class ExpenseResponseSchema(BaseModel):
    """Schema for serializing Expense model data, including nested objects."""
    id: int
    name: str
    amount: float
    description: Optional[str]
    date: datetime.date
    active_status: bool
    category: Optional[CategoryResponseSchema]
    tags: List[TagResponseSchema]

    # This configuration allows Pydantic to create the schema from a SQLAlchemy model instance
    model_config = ConfigDict(from_attributes=True)