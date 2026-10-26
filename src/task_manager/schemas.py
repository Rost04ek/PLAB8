from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, EmailStr

PriorityType = Literal["low", "medium", "high"]
StatusType = Literal["todo", "in_progress", "done"]

class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    model_config = {"from_attributes": True}


class TaskBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    status: StatusType = "todo"
    priority: PriorityType = "medium"
    due_date: datetime
    user_id: int | None = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    status: StatusType | None = None
    priority: PriorityType | None = None
    due_date: datetime | None = None
    user_id: int | None = None

class TaskResponse(TaskBase):
    id: int

    model_config = {"from_attributes": True}


class TaskStatistics(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
