"""
Task API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
)
from app.models.task import Task
from app.repositories.task import task_repo

router = APIRouter()


@router.get("/tasks", response_model=TaskListResponse)
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List tasks with filtering."""
    query = db.query(Task)
    
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "data": tasks,
        "meta": {"skip": skip, "limit": limit, "total": total}
    }


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
):
    """Create a new task."""
    task = task_repo.create(db, obj_in=task_in)
    return {"data": task}


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific task."""
    task = task_repo.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"data": task}


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
):
    """Update a task."""
    task = task_repo.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_repo.update(db, db_obj=task, obj_in=task_in)
    return {"data": task}


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """Delete a task."""
    task = task_repo.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_repo.remove(db, id=task_id)
    return None


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """Mark task as completed."""
    task = task_repo.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_repo.update(db, db_obj=task, obj_in={"completed": True})
    return {"data": task}
