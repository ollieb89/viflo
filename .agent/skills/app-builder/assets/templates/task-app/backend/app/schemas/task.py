"""
Task schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    """Base task schema."""
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    user_id: int


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskInDB(TaskBase):
    """Schema representing task in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskResponse(BaseModel):
    """API response wrapper."""
    data: TaskInDB


class TaskListResponse(BaseModel):
    """API response wrapper for list."""
    data: list[TaskInDB]
    meta: dict


class UserBase(BaseModel):
    """Base user schema."""
    email: str
    name: str


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserInDB(UserBase):
    """Schema representing user in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    """API response wrapper."""
    data: UserInDB
