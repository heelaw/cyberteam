#!/usr/bin/env python3
"""
CyberTeam V4 - Team 数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(Enum):
    """消息类型"""
    MESSAGE = "message"
    JOIN_REQUEST = "join_request"
    JOIN_APPROVED = "join_approved"
    PLAN_APPROVAL_REQUEST = "plan_approval_request"
    PLAN_APPROVED = "plan_approved"
    PLAN_REJECTED = "plan_rejected"
    SHUTDOWN_REQUEST = "shutdown_request"
    SHUTDOWN_APPROVED = "shutdown_approved"
    IDLE = "idle"
    BROADCAST = "broadcast"


@dataclass
class TaskItem:
    """任务项"""
    task_id: str
    subject: str
    description: str = ""
    owner: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    blocked_by: List[str] = field(default_factory=list)  # task_ids
    depends_on: List[str] = field(default_factory=list)  # task_ids (alias for blocked_by)
    locked_by: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "description": self.description,
            "owner": self.owner,
            "status": self.status.value,
            "blocked_by": self.blocked_by,
            "depends_on": self.depends_on,
            "locked_by": self.locked_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskItem":
        status = data.get("status", "pending")
        if isinstance(status, str):
            status = TaskStatus(status)
        return cls(
            task_id=data["task_id"],
            subject=data["subject"],
            description=data.get("description", ""),
            owner=data.get("owner"),
            status=status,
            blocked_by=data.get("blocked_by", []),
            depends_on=data.get("depends_on", []),
            locked_by=data.get("locked_by"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            completed_at=data.get("completed_at"),
            result=data.get("result"),
            error=data.get("error")
        )

    @property
    def is_blocked(self) -> bool:
        return len(self.blocked_by) > 0 and self.status == TaskStatus.BLOCKED


@dataclass
class TeamMessage:
    """团队消息"""
    msg_id: str
    msg_type: MessageType
    from_agent: str
    to: str  # "leader" or agent_name or "*" (broadcast)
    content: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    consumed: bool = False

    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "from_agent": self.from_agent,
            "to": self.to,
            "content": self.content,
            "created_at": self.created_at,
            "consumed": self.consumed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TeamMessage":
        msg_type = data.get("msg_type", "message")
        if isinstance(msg_type, str):
            msg_type = MessageType(msg_type)
        return cls(
            msg_id=data["msg_id"],
            msg_type=msg_type,
            from_agent=data["from_agent"],
            to=data["to"],
            content=data["content"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            consumed=data.get("consumed", False)
        )


@dataclass
class TeamSnapshot:
    """团队快照"""
    team_name: str
    goal: str
    members: List[str]
    tasks: List[Dict]
    messages: List[Dict]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "team_name": self.team_name,
            "goal": self.goal,
            "members": self.members,
            "tasks": self.tasks,
            "messages": self.messages,
            "created_at": self.created_at
        }
