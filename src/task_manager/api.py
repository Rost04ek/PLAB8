import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from task_manager.database import engine, Base, get_session
from task_manager.models import TaskModel, User
from task_manager.repositories import TaskRepository
from task_manager.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatistics,
    UserCreate,
    UserResponse,
)
from task_manager.external_api import fetch_multiple_users_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Task Management System API", version="1.0.0", lifespan=lifespan)


@app.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(
    status: str | None = Query(None, description="todo, in_progress, done"),
    priority: str | None = Query(None, description="low, medium, high"),
    user_id: int | None = Query(None),
    session: Session = Depends(get_session),
):
    repo = TaskRepository(session)
    return repo.get_all(status=status, priority=priority, user_id=user_id)


@app.get("/tasks/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    return repo.get_overdue()


@app.get("/tasks/statistics", response_model=TaskStatistics)
async def get_tasks_statistics(session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    return repo.get_statistics()


@app.get("/tasks/{id}", response_model=TaskResponse)
async def get_task_by_id(id: int, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    new_task = TaskModel(**data.model_dump())
    return repo.create(new_task)


@app.patch("/tasks/{id}", response_model=TaskResponse)
async def update_task(id: int, data: TaskUpdate, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    updates = data.model_dump(exclude_unset=True)
    return repo.update(task, updates)


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    repo.delete(task)


@app.get("/users/{id}/tasks", response_model=list[TaskResponse])
async def get_user_tasks(id: int, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    return repo.get_by_user(id)


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, session: Session = Depends(get_session)):
    user = User(name=data.name, email=data.email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/tasks/batch-users-summary")
async def batch_fetch_users_tasks(user_ids: list[int]):
    try:
        results = await asyncio.wait_for(
            fetch_multiple_users_tasks(
                base_url="http://127.0.0.1:8000",
                user_ids=user_ids,
                max_concurrency=3,
                timeout=5.0,
            ),
            timeout=8.0,
        )
        return results
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Batch request processing timed out",
        )
