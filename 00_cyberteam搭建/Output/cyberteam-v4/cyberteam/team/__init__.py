"""Team coordination layer for multi-agent collaboration."""

from cyberteam.team.lifecycle import LifecycleManager
from cyberteam.team.mailbox import MailboxManager
from cyberteam.team.manager import TeamManager
from cyberteam.team.plan import PlanManager
from cyberteam.team.tasks import TaskStore
from cyberteam.team.watcher import InboxWatcher

__all__ = [
    "TeamManager",
    "MailboxManager",
    "TaskStore",
    "PlanManager",
    "LifecycleManager",
    "InboxWatcher",
]
