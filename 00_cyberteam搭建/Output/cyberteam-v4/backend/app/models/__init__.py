"""CyberTeam V4 数据库模型。"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Date, Float, Integer, Boolean, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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

# ── 扩展模型：Skills, Teams, Projects ──

class Skill(Base):
    """技能表。"""
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), default="growth", index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    trigger_conditions: Mapped[str] = mapped_column(Text, default="")
    usage_guide: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[str] = mapped_column(JSON, default=list)
    success_metrics: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    references: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "triggerConditions": self.trigger_conditions,
            "usageGuide": self.usage_guide,
            "difficulty": self.difficulty,
            "version": self.version,
            "author": self.author,
            "tags": self.tags if isinstance(self.tags, list) else [],
            "success_metrics": self.success_metrics,
            "references": self.references,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Team(Base):
    """团队表。"""
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    agent_ids: Mapped[str] = mapped_column(JSON, default=list)
    coordination_mode: Mapped[str] = mapped_column(String(50), default="sequential")
    reporting_cycle: Mapped[str] = mapped_column(String(50), default="daily")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agentIds": self.agent_ids if isinstance(self.agent_ids, list) else [],
            "coordinationMode": self.coordination_mode,
            "reportingCycle": self.reporting_cycle,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Project(Base):
    """项目表。"""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goal: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(JSON, default=list)
    extra_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # 避免与SQLAlchemy保留字metadata冲突
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    task_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典。"""
        return {
            "project_id": self.id,
            "name": self.name,
            "description": self.description,
            "goal": self.goal,
            "tags": self.tags if isinstance(self.tags, list) else [],
            "metadata": self.extra_data or {},
            "status": self.status,
            "task_count": self.task_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ── 会话与消息模型 ──


class Conversation(Base):
    """会话表。"""
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    meta: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "status": self.status,
            "project_id": self.project_id,
            "metadata": self.meta or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(Base):
    """消息表。"""
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    sender_type: Mapped[str] = mapped_column(String(32))  # user/agent/system
    sender_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sender_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(32), default="markdown")
    meta: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "department": self.department,
            "content": self.content,
            "content_type": self.content_type,
            "metadata": self.meta or {},
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ── Agent 执行日志 ──


class AgentExecution(Base):
    """Agent 执行日志表。"""
    __tablename__ = "agent_executions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    agent_name: Mapped[str] = mapped_column(String(64), index=True)
    department: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32))  # running/completed/failed
    model_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    input_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "department": self.department,
            "status": self.status,
            "model_id": self.model_id,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ── 预算追踪 ──


class BudgetTracking(Base):
    """预算追踪表。"""
    __tablename__ = "budget_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(32))  # organization/project/agent
    entity_id: Mapped[str] = mapped_column(String(64))
    period: Mapped[datetime] = mapped_column(Date)  # 日期维度
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0)
    budget_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "period": self.period.isoformat() if self.period else None,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "budget_limit": self.budget_limit,
        }


# ── 审批记录 ──


class Approval(Base):
    """审批记录表。"""
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    action_type: Mapped[str] = mapped_column(String(64))
    action_detail: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending/approved/rejected
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    review_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "action_type": self.action_type,
            "action_detail": self.action_detail,
            "status": self.status,
            "reviewer_id": self.reviewer_id,
            "review_comment": self.review_comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


# ── 跨部门协作模型 ──


class HandoffStatus(str, Enum):
    """Handoff状态枚举。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CollaborationTaskState(str, Enum):
    """协作任务状态枚举。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HandoffRecord(Base):
    """Handoff记录表 - 部门间任务移交凭证。"""
    __tablename__ = "handoff_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    handoff_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(64), index=True)
    from_department: Mapped[str] = mapped_column(String(50))  # 移交部门
    to_department: Mapped[str] = mapped_column(String(50))    # 接收部门
    status: Mapped[HandoffStatus] = mapped_column(SQLEnum(HandoffStatus), default=HandoffStatus.PENDING)

    # 上下文传递（JSON格式存储）
    context: Mapped[dict] = mapped_column(JSON, default=dict)

    # 协作结果（JSON格式存储）
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 元数据
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "handoff_id": self.handoff_id,
            "task_id": self.task_id,
            "from_department": self.from_department,
            "to_department": self.to_department,
            "status": self.status.value if isinstance(self.status, HandoffStatus) else self.status,
            "context": self.context or {},
            "result": self.result or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
        }


class CollaborationTask(Base):
    """协作任务表 - 跨部门任务的完整生命周期。"""
    __tablename__ = "collaboration_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    original_task: Mapped[str] = mapped_column(Text)  # 原始任务描述
    status: Mapped[CollaborationTaskState] = mapped_column(SQLEnum(CollaborationTaskState), default=CollaborationTaskState.PENDING)

    # 路由结果
    primary_department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    collaborating_departments: Mapped[list] = mapped_column(JSON, default=list)  # 协作部门列表
    match_scores: Mapped[dict] = mapped_column(JSON, default=dict)  # {dept_id: score}

    # 结果汇总（JSON格式存储）
    results: Mapped[dict] = mapped_column(JSON, default=dict)  # {dept_id: result}
    final_output: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 最终输出

    # 执行统计
    total_handoffs: Mapped[int] = mapped_column(Integer, default=0)
    completed_handoffs: Mapped[int] = mapped_column(Integer, default=0)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 元数据
    creator: Mapped[str] = mapped_column(String(100), default="system")
    tags: Mapped[list] = mapped_column(JSON, default=list)

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "original_task": self.original_task,
            "status": self.status.value if isinstance(self.status, CollaborationTaskState) else self.status,
            "primary_department": self.primary_department,
            "collaborating_departments": self.collaborating_departments if isinstance(self.collaborating_departments, list) else [],
            "match_scores": self.match_scores or {},
            "results": self.results or {},
            "final_output": self.final_output or {},
            "total_handoffs": self.total_handoffs,
            "completed_handoffs": self.completed_handoffs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "creator": self.creator,
            "tags": self.tags if isinstance(self.tags, list) else [],
        }


# ── 审核模型 ──


class ReviewStatus(str, Enum):
    """审核状态枚举。"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION = "revision"


class Department(Base):
    """部门表 - 三省六部架构。"""
    __tablename__ = "departments"
    __table_args__ = (
        Index("ix_department_company_id", "company_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    company_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("companies.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="departments")
    company_departments: Mapped[list["CompanyDepartment"]] = relationship("CompanyDepartment", back_populates="department")


class Agent(Base):
    """Agent表。"""
    __tablename__ = "agents"
    __table_args__ = (
        Index("ix_agent_company_id", "company_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(32), nullable=False, default="executor")
    status: Mapped[str] = mapped_column(String(32), default="active")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    company_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("companies.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="agents")
    company_agents: Mapped[list["CompanyAgent"]] = relationship("CompanyAgent", back_populates="agent")


class Company(Base):
    """公司表。"""
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="company")
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="company")
    company_departments: Mapped[list["CompanyDepartment"]] = relationship("CompanyDepartment", back_populates="company")
    company_agents: Mapped[list["CompanyAgent"]] = relationship("CompanyAgent", back_populates="company")

    def to_dict(self):
        """转换为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "config": self.config or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CompanyDepartment(Base):
    """公司部门表。"""
    __tablename__ = "company_departments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), nullable=False, index=True)
    department_id: Mapped[str] = mapped_column(String(64), ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="company_departments")
    department: Mapped["Department"] = relationship("Department", back_populates="company_departments")


class CompanyAgent(Base):
    """公司Agent关联表。"""
    __tablename__ = "company_agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(64), ForeignKey("agents.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="company_agents")
    agent: Mapped["Agent"] = relationship("Agent", back_populates="company_agents")


class CompanySkill(Base):
    """公司Skill关联表。"""
    __tablename__ = "company_skills"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), nullable=False, index=True)
    skill_id: Mapped[str] = mapped_column(String(64), ForeignKey("skills.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    """订阅表。"""
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(64), ForeignKey("companies.id"), nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(32), default="free")
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SealRejection(Base):
    """审核记录表 - 内容审核（含自动合规检查）。"""
    __tablename__ = "seal_rejections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    reviewer_agent: Mapped[str] = mapped_column(String(50), default="auto")
    check_keywords: Mapped[list] = mapped_column(JSON, default=list)
    min_length: Mapped[int] = mapped_column(Integer, default=0)
    max_length: Mapped[int] = mapped_column(Integer, default=0)
    auto_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    violations: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[ReviewStatus] = mapped_column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "content": self.content,
            "reviewer_agent": self.reviewer_agent,
            "check_keywords": self.check_keywords,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "auto_passed": self.auto_passed,
            "violations": self.violations,
            "status": self.status.value if isinstance(self.status, ReviewStatus) else self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
