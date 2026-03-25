#!/usr/bin/env python3
"""
CyberTeam V4 - Spawn 模块
Agent Spawn 系统 (tmux + registry)
"""

from .registry import (
    SpawnRegistryManager,
    SpawnRegistry,
    AgentInfo,
    is_agent_alive,
    check_all_alive,
    DEFAULT_REGISTRY_DIR
)
from .tmux_backend import (
    TmuxBackend,
    TmuxBackendError,
    spawn_tmux_agent
)

__all__ = [
    # Registry
    "SpawnRegistryManager",
    "SpawnRegistry",
    "AgentInfo",
    "is_agent_alive",
    "check_all_alive",
    "DEFAULT_REGISTRY_DIR",
    # Tmux Backend
    "TmuxBackend",
    "TmuxBackendError",
    "spawn_tmux_agent"
]
