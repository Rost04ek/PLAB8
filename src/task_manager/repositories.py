from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from task_manager.models import TaskModel, User

class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(
        self,
        status: str | None = None,
        priority: str | None = None,
        user_id: int | None = None,
    ) -> list[TaskModel]:
        stmt = select(TaskModel)
        if status:
            stmt = stmt.where(TaskModel.status == status)
        if priority:
            stmt = stmt.where(TaskModel.priority == priority)
        if user_id:
            stmt = stmt.where(TaskModel.user_id == user_id)
        return list(self.session.scalars(stmt))

    def get_by_id(self, task_id: int) -> TaskModel | None:
        return self.session.get(TaskModel, task_id)

    def create(self, task: TaskModel) -> TaskModel:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def update(self, task: TaskModel, updates: dict) -> TaskModel:
        for field, value in updates.items():
            setattr(task, field, value)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task: TaskModel) -> None:
        self.session.delete(task)
        self.session.commit()

    def get_by_user(self, user_id: int) -> list[TaskModel]:
        stmt = select(TaskModel).where(TaskModel.user_id == user_id)
        return list(self.session.scalars(stmt))

    def get_overdue(self) -> list[TaskModel]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = select(TaskModel).where(
            TaskModel.due_date < now,
            TaskModel.status != "done"
        )
        return list(self.session.scalars(stmt))

    def get_statistics(self) -> dict:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        total = self.session.scalar(select(func.count(TaskModel.id))) or 0
        completed = self.session.scalar(
            select(func.count(TaskModel.id)).where(TaskModel.status == "done")
        ) or 0
        overdue = self.session.scalar(
            select(func.count(TaskModel.id)).where(
                TaskModel.due_date < now,
                TaskModel.status != "done"
            )
        ) or 0
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "overdue": overdue,
        }

class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
