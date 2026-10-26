import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from task_manager.database import engine, Base, get_session
from task_manager.services import TaskService
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

app = FastAPI(
    title="Task Management System API",
    version="1.0.0",
    description="REST API для системи керування завданнями (Лабораторна №8, Варіант 14)",
    lifespan=lifespan,
)

def get_service(session: Session = Depends(get_session)) -> TaskService:
    return TaskService(session)


@app.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"])
async def get_tasks(
    status: str | None = Query(None, description="Фільтрація за статусом"),
    priority: str | None = Query(None, description="Фільтрація за пріоритетом"),
    user_id: int | None = Query(None, description="Фільтрація за користувачем"),
    service: TaskService = Depends(get_service),
):
    return service.list_tasks(status=status, priority=priority, user_id=user_id)


@app.get("/tasks/overdue", response_model=list[TaskResponse], tags=["Tasks"])
async def get_overdue_tasks(service: TaskService = Depends(get_service)):
    return service.get_overdue_tasks()


@app.get("/tasks/statistics", response_model=TaskStatistics, tags=["Tasks"])
async def get_tasks_statistics(service: TaskService = Depends(get_service)):
    return service.get_statistics()


@app.get("/tasks/{id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task_by_id(id: int, service: TaskService = Depends(get_service)):
    task = service.get_task(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    return service.create_task(data)


@app.patch("/tasks/{id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(id: int, data: TaskUpdate, service: TaskService = Depends(get_service)):
    task = service.update_task(id, data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(id: int, service: TaskService = Depends(get_service)):
    deleted = service.delete_task(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


@app.get("/users/{id}/tasks", response_model=list[TaskResponse], tags=["Users"])
async def get_user_tasks(id: int, service: TaskService = Depends(get_service)):
    return service.get_user_tasks(id)


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(data: UserCreate, service: TaskService = Depends(get_service)):
    return service.create_user(data)


@app.post("/tasks/batch-users-summary", tags=["Async Aggregation"])
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
            detail="Batch operation timed out",
        )
