from sqlalchemy.orm import Session
from task_manager.models import TaskModel, User
from task_manager.repositories import TaskRepository, UserRepository
from task_manager.schemas import TaskCreate, TaskUpdate, UserCreate

class TaskService:
    def __init__(self, session: Session) -> None:
        self.task_repo = TaskRepository(session)
        self.user_repo = UserRepository(session)

    def list_tasks(
        self,
        status: str | None = None,
        priority: str | None = None,
        user_id: int | None = None,
    ) -> list[TaskModel]:
        return self.task_repo.get_all(status=status, priority=priority, user_id=user_id)

    def get_task(self, task_id: int) -> TaskModel | None:
        return self.task_repo.get_by_id(task_id)

    def create_task(self, data: TaskCreate) -> TaskModel:
        task = TaskModel(**data.model_dump())
        return self.task_repo.create(task)

    def update_task(self, task_id: int, data: TaskUpdate) -> TaskModel | None:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return None
        updates = data.model_dump(exclude_unset=True)
        return self.task_repo.update(task, updates)

    def delete_task(self, task_id: int) -> bool:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return False
        self.task_repo.delete(task)
        return True

    def get_user_tasks(self, user_id: int) -> list[TaskModel]:
        return self.task_repo.get_by_user(user_id)

    def get_overdue_tasks(self) -> list[TaskModel]:
        return self.task_repo.get_overdue()

    def get_statistics(self) -> dict:
        return self.task_repo.get_statistics()

    def create_user(self, data: UserCreate) -> User:
        user = User(name=data.name, email=data.email)
        return self.user_repo.create(user)
