"""
Swarm编排引擎 - CyberTeam v4

提供多Agent协同编排能力，包括：
- SwarmCoordinator: 蜂群协调器
- TaskDAG: 任务依赖图管理
- WorktreeManager: Git Worktree生命周期管理
- MessageBus: 消息总线
"""

from .coordinator import SwarmCoordinator
from .task_dag import TaskDAG
from .worktree_manager import WorktreeManager
from .message_bus import MessageBus

__all__ = [
    "SwarmCoordinator",
    "TaskDAG",
    "WorktreeManager",
    "MessageBus",
]