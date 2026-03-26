from __future__ import annotations
"""Spawn backends for launching team agents."""


from cyberteam.spawn.base import SpawnBackend


def get_backend(name: str = "tmux") -> SpawnBackend:
    """Factory function to get a spawn backend by name."""
    if name == "subprocess":
        from cyberteam.spawn.subprocess_backend import SubprocessBackend
        return SubprocessBackend()
    elif name == "tmux":
        from cyberteam.spawn.tmux_backend import TmuxBackend
        return TmuxBackend()
    else:
        raise ValueError(f"Unknown spawn backend: {name}. Available: subprocess, tmux")


# Spawn registry functions and classes
from cyberteam.spawn.registry import (
    register_agent,
    get_registry,
    is_agent_alive,
    list_dead_agents,
    stop_agent,
    check_all_alive,
    SpawnRegistryManager,
)


__all__ = [
    # Base
    "SpawnBackend",
    "get_backend",
    # Registry functions
    "register_agent",
    "get_registry",
    "is_agent_alive",
    "list_dead_agents",
    "stop_agent",
    "check_all_alive",
    # Registry classes
    "SpawnRegistryManager",
]
