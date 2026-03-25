#!/usr/bin/env python3
"""
CyberTeam V4 - Team 模块
团队协作核心 (tasks + mailbox)
"""

from .models import (
    TaskStatus,
    TaskItem,
    MessageType,
    TeamMessage,
    TeamSnapshot
)
from .tasks import (
    TaskStore,
    TaskLockError,
    TaskNotFoundError,
    DEFAULT_TASK_DIR
)
from .mailbox import (
    MailboxManager,
    Inbox,
    DEFAULT_MAILBOX_DIR
)

__all__ = [
    # Models
    "TaskStatus",
    "TaskItem",
    "MessageType",
    "TeamMessage",
    "TeamSnapshot",
    # Tasks
    "TaskStore",
    "TaskLockError",
    "TaskNotFoundError",
    "DEFAULT_TASK_DIR",
    # Mailbox
    "MailboxManager",
    "Inbox",
    "DEFAULT_MAILBOX_DIR"
]
