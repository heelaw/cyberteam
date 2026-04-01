"""Team coordination layer for multi-agent collaboration."""

from cyberteam.team.lifecycle import LifecycleManager
from cyberteam.team.mailbox import MailboxManager
from cyberteam.team.manager import TeamManager
from cyberteam.team.plan import PlanManager
from cyberteam.team.tasks import TaskStore
from cyberteam.team.watcher import InboxWatcher
from cyberteam.team.models import (
    TeamMessage,
    TeamMember,
    TeamConfig,
    TaskItem,
    TaskStatus,
    TaskPriority,
    MessageType,
    MemberStatus,
)

__all__ = [
    "TeamManager",
    "MailboxManager",
    "TaskStore",
    "PlanManager",
    "LifecycleManager",
    "InboxWatcher",
    "TeamMessage",
    "TeamMember",
    "TeamConfig",
    "TaskItem",
    "TaskStatus",
    "TaskPriority",
    "MessageType",
    "MemberStatus",
]
