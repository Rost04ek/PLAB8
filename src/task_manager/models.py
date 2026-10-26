from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from task_manager.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)

    tasks = relationship("TaskModel", back_populates="assignee", cascade="all, delete-orphan")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(30), default="todo", nullable=False)       # todo, in_progress, done
    priority = Column(String(30), default="medium", nullable=False)   # low, medium, high
    due_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    assignee = relationship("User", back_populates="tasks")
