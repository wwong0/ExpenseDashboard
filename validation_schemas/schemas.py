# C:/Users/William/PycharmProjects/ExpenseDashboard/validation_schemas/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime


# --- Input Schemas ---
# These schemas are used to validate incoming request data.

class CreateExpenseSchema(BaseModel):
    """Schema for validating data when creating a new expense."""
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None
    active_status: bool = True
    date: datetime.date = datetime.date.today()
    tag_ids: List[int] = []


class UpdateExpenseSchema(BaseModel):
    """
    Schema for validating data when updating an expense.
    All fields are optional, allowing for partial updates.
    """
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    active_status: Optional[bool] = None
    date: Optional[datetime.date] = None
    tag_ids: Optional[List[int]] = None


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
    amount: float
    description: Optional[str]
    date: datetime.date
    active_status: bool
    category: Optional[CategoryResponseSchema]
    tags: List[TagResponseSchema]

    # This configuration allows Pydantic to create the schema from a SQLAlchemy model instance
    model_config = ConfigDict(from_attributes=True)