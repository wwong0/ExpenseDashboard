from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

class CreateExpenseSchema(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None
    active_status: Optional[bool] = True
    date: datetime.date = datetime.date.today()
    tag_ids: Optional[List[int]] = []

class UpdateExpenseSchema(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    active_status: Optional[bool] = None
    date: Optional[datetime.date] = None
    tag_ids: Optional[List[int]] = None

class TagResponseSchema(BaseModel):
    id: int
    name: str

class CategoryResponseSchema(BaseModel):
    id: int
    name: str

class ExpenseResponseSchema(BaseModel):
    id: int
    amount: float
    description: str
    date: datetime.date
    active_status: bool
    category: CategoryResponseSchema
    tags: List[TagResponseSchema]

    model_config = ConfigDict(from_attributes=True)

class AuthSchema(BaseModel):
    username: str
    password: str
