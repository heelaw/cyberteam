"""CyberTeam V4 数据库模型。"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 基础类。"""
    pass


class TaskState(str, Enum):
    """任务状态枚举。"""
    PENDING = "pending"
    THINKING = "thinking"
    DEBATING = "debating"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base):
    """任务表。"""
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)

    # 任务信息
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    user_input: Mapped[str] = mapped_column(Text)

    # 状态与优先级
    state: Mapped[TaskState] = mapped_column(SQLEnum(TaskState), default=TaskState.PENDING)
    priority: Mapped[str] = mapped_column(String(20), default="中")

    # 执行信息
    assignee_org: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    creator: Mapped[str] = mapped_column(String(100), default="system")

    # 元数据
    tags: Mapped[str] = mapped_column(JSON, default=list)
    meta: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)

    # 评分结果
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    professionalism: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    practicality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    logic: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    innovation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    safety: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典。"""
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "title": self.title,
            "description": self.description,
            "user_input": self.user_input,
            "state": self.state.value,
            "priority": self.priority,
            "assignee_org": self.assignee_org,
            "creator": self.creator,
            "tags": self.tags if isinstance(self.tags, list) else [],
            "meta": self.meta or {},
            "score": self.score,
            "completeness": self.completeness,
            "professionalism": self.professionalism,
            "practicality": self.practicality,
            "logic": self.logic,
            "innovation": self.innovation,
            "safety": self.safety,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class ExpertOutput(Base):
    """专家输出表。"""
    __tablename__ = "expert_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    expert_id: Mapped[str] = mapped_column(String(50))
    expert_name: Mapped[str] = mapped_column(String(100))

    # 输出内容
    framework: Mapped[str] = mapped_column(String(100))
    analysis: Mapped[str] = mapped_column(Text)
    suggestions: Mapped[str] = mapped_column(Text)
    risks: Mapped[str] = mapped_column(Text, default="")

    # 评分
    completeness: Mapped[float] = mapped_column(Float, default=0)
    professionalism: Mapped[float] = mapped_column(Float, default=0)
    practicality: Mapped[float] = mapped_column(Float, default=0)
    logic: Mapped[float] = mapped_column(Float, default=0)
    innovation: Mapped[float] = mapped_column(Float, default=0)
    safety: Mapped[float] = mapped_column(Float, default=0)

    # 元数据
    round: Mapped[int] = mapped_column(Integer, default=1)
    keywords: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DebateRound(Base):
    """辩论轮次表。"""
    __tablename__ = "debate_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    round_number: Mapped[int] = mapped_column(Integer)
    round_type: Mapped[str] = mapped_column(String(50))  # initial, cross_examine, defend, converge, final
    convergence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_converged: Mapped[bool] = mapped_column(default=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DepartmentOutput(Base):
    """部门执行输出表。"""
    __tablename__ = "department_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True)
    department: Mapped[str] = mapped_column(String(50))

    # 输出内容
    output: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class FinalReport(Base):
    """最终报告表。"""
    __tablename__ = "final_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), index=True, unique=True)

    # 报告内容
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 整体评分
    final_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── TODO 应用模型 ──

class TodoItemState(str, Enum):
    """TODO 项状态枚举。"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TodoItemPriority(str, Enum):
    """TODO 项优先级枚举。"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoItem(Base):
    """TODO 项表。"""
    __tablename__ = "todo_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 内容
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 状态与优先级
    state: Mapped[TodoItemState] = mapped_column(SQLEnum(TodoItemState), default=TodoItemState.TODO)
    priority: Mapped[TodoItemPriority] = mapped_column(SQLEnum(TodoItemPriority), default=TodoItemPriority.MEDIUM)

    # 分类
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[str] = mapped_column(JSON, default=list)

    # 时间戳
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "state": self.state.value,
            "priority": self.priority.value,
            "category": self.category,
            "tags": self.tags if isinstance(self.tags, list) else [],
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }