"""SQLAlchemy database models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Integer, Float, DateTime, Boolean,
    ForeignKey, Index, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Conversation(Base):
    """Conversation model for chat sessions."""
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_conversations_user_created", "user_id", "created_at"),
    )


class Message(Base):
    """Message model for individual chat messages."""
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user/assistant/system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    thinking_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )


class AgentExecution(Base):
    """Agent execution tracking model."""
    __tablename__ = "agent_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=True
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    thinking_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    __table_args__ = (
        Index("ix_agent_executions_agent_status", "agent_name", "status"),
    )


class BudgetTracking(Base):
    """Budget tracking model for cost management."""
    __tablename__ = "budget_tracking"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    budget_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily/monthly/project
    budget_amount: Mapped[float] = mapped_column(Float, nullable=False)
    spent_amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="CNY")
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_budget_tracking_user_period", "user_id", "period_start", "period_end"),
    )


class Project(Base):
    """Project model for organizing work."""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_projects_user_status", "user_id", "status"),
    )


class CustomAgent(Base):
    """Custom agent model for user-created agents."""
    __tablename__ = "custom_agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    llm: Mapped[str] = mapped_column(String(50), default="claude")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tools: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    departments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_custom_agents_user_active", "user_id", "is_active"),
    )


class Team(Base):
    """Team model for agent collaboration groups."""
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    members: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_teams_user_status", "user_id", "status"),
    )


class Template(Base):
    """Template model for task workflow templates."""
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    steps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    estimated_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_templates_user_department", "user_id", "department"),
    )
