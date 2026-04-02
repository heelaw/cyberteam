"""数据库模型 - 抄 Magic。

核心表：
- users: 用户表
- conversations: 会话表
- messages: 消息表
- agent_executions: Agent 执行日志
- budget_tracking: 预算追踪

设计原则：
- 软删除（is_deleted 字段）
- 时间戳自动管理
- JSON 字段存储元数据
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
    Float,
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """用户表。"""

    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="user")  # admin/user/guest/department_admin
    org_id = Column(String(64), default="default", index=True)
    departments = Column(JSON, default=list)  # 所属部门列表
    extra_data = Column(JSON, default=dict)  # 扩展元数据
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    conversations = relationship("Conversation", back_populates="user", lazy="selectin")
    executions = relationship("AgentExecution", back_populates="user", lazy="selectin")


class Conversation(Base):
    """会话表。"""

    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(String(64), nullable=True, index=True)  # 主 Agent ID
    title = Column(String(255), nullable=True)
    status = Column(String(32), default="active")  # active/completed/archived
    extra_data = Column(JSON, default=dict)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", lazy="selectin", order_by="Message.created_at")

    __table_args__ = (
        Index("idx_conversation_user_created", "user_id", "created_at"),
    )


class Message(Base):
    """消息表。"""

    __tablename__ = "messages"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    sender_type = Column(String(32), nullable=False)  # user/agent/system
    sender_id = Column(String(64), nullable=True)  # Agent ID 或 user ID
    content = Column(Text, nullable=False)
    extra_data = Column(JSON, default=dict)  # 存储 token 消耗、模型等信息
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_message_conversation_created", "conversation_id", "created_at"),
    )


class AgentExecution(Base):
    """Agent 执行日志表。"""

    __tablename__ = "agent_executions"

    id = Column(String(64), primary_key=True)
    task_id = Column(String(64), nullable=True, index=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    agent_name = Column(String(64), nullable=False, index=True)
    agent_version = Column(String(32), nullable=True)
    status = Column(String(32), default="running")  # running/completed/failed
    input_text = Column(Text, nullable=True)
    output_text = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    extra_data = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", back_populates="executions")

    __table_args__ = (
        Index("idx_execution_user_agent", "user_id", "agent_name"),
        Index("idx_execution_started", "started_at"),
    )


class BudgetTracking(Base):
    """预算追踪表。"""

    __tablename__ = "budget_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(32), nullable=False)  # user/org/agent
    entity_id = Column(String(64), nullable=False)
    period = Column(String(7), nullable=False)  # YYYY-MM 格式
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    budget_limit = Column(Float, nullable=True)
    alert_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_budget_entity_period", "entity_type", "entity_id", "period", unique=True),
    )


class Project(Base):
    """项目表（CyberTeam 特色）。"""

    __tablename__ = "projects"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # ========== 新增：本地文件夹路径 ==========
    local_path = Column(String(512), nullable=True)
    # =========================================
    goal = Column(Text, default="")  # 项目目标
    tags = Column(JSON, default=list)  # 标签
    status = Column(String(32), default="planning")  # planning/executing/completed/archived
    extra_data = Column(JSON, default=dict)  # 存储业务上下文、方案等
    is_deleted = Column(Boolean, default=False)
    task_count = Column(Integer, default=0)  # 任务计数
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_project_user_status", "user_id", "status"),
    )


class Department(Base):
    """部门表（三省六部架构）。"""

    __tablename__ = "departments"

    id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=False)
    code = Column(String(32), unique=True, nullable=False, index=True)  # CEO/COO/STRATEGY/PRODUCT...
    parent_id = Column(String(64), nullable=True)  # 上级部门
    level = Column(Integer, default=1)  # 层级：1=决策层，2=协调层，3=执行层
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Expert(Base):
    """专家表（100+思维专家）。"""

    __tablename__ = "experts"

    id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=False)
    code = Column(String(64), unique=True, nullable=False, index=True)  # first_principles/lateral_thinking...
    category = Column(String(32), nullable=False)  # thinking/strategy/analysis/creative...
    description = Column(Text, nullable=True)
    prompt_template = Column(Text, nullable=True)  # 专家的 Prompt 模板
    extra_data = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Team(Base):
    """团队表（支持公司隔离）。"""

    __tablename__ = "teams"

    id = Column(String(64), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    company_id = Column(String(64), nullable=True, index=True)  # 公司ID（系统团队可为空）
    agent_ids = Column(JSON, default=list)  # 成员Agent ID列表
    coordination_mode = Column(String(32), default="sequential")  # sequential/parallel/hierarchical
    reporting_cycle = Column(String(32), default="daily")  # daily/weekly/monthly
    status = Column(String(32), default="active")  # active/inactive/archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_team_company", "company_id"),
    )

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "company_id": self.company_id,
            "agent_ids": self.agent_ids or [],
            "coordination_mode": self.coordination_mode,
            "reporting_cycle": self.reporting_cycle,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(Base):
    """任务表（支持多Agent协作）。"""

    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), default="pending")  # pending/running/completed/failed
    priority = Column(Integer, default=3)  # 1=最高，5=最低
    assignee_org = Column(String(64), nullable=True, index=True)  # 分配给的团队/部门ID
    meta = Column(JSON, default=dict)  # 元数据（包含 executive_agent_ids 等）
    result = Column(Text, nullable=True)  # 执行结果
    error = Column(Text, nullable=True)  # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_task_assignee_org", "assignee_org"),
        Index("idx_task_status", "status"),
    )

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee_org": self.assignee_org,
            "meta": self.meta or {},
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class DepartmentAgent(Base):
    """部门-Agent关联表（支持公司隔离）。"""

    __tablename__ = "department_agents"

    id = Column(String(64), primary_key=True)
    department_id = Column(String(64), nullable=False, index=True)
    company_id = Column(String(64), nullable=True, index=True)  # 公司ID
    agent_id = Column(String(64), nullable=False)
    agent_type = Column(String(32), default="executor")  # executor/leader/coordinator
    role_name = Column(String(64), nullable=True)  # 在部门中的角色名
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_dept_agent_dept", "department_id"),
        Index("idx_dept_agent_company", "company_id"),
    )
