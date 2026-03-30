"""Spawn backends for launching team agents."""

from __future__ import annotations

from cyberteam.spawn.base import SpawnBackend
from cyberteam.spawn.registry import get_registry, is_agent_alive, register_agent


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


class SpawnRegistryManager:
    """Registry manager for spawned agents."""

    def __init__(self, team_name: str):
        self.team_name = team_name

    def get_registry(self) -> dict:
        """Get the full registry for this team."""
        return get_registry(self.team_name)

    def is_agent_alive(self, agent_name: str) -> Optional[bool]:
        """Check if an agent is alive."""
        return is_agent_alive(self.team_name, agent_name)

    def register(self, agent_name: str, backend: str, tmux_target: str = "", pid: int = 0, command: list = None) -> None:
        """Register an agent."""
        register_agent(self.team_name, agent_name, backend, tmux_target, pid, command)

    def get_alive_agents(self) -> list[str]:
        """Get list of alive agent names."""
        registry = self.get_registry()
        alive = []
        for name in registry:
            if is_agent_alive(self.team_name, name):
                alive.append(name)
        return alive

    def get_dead_agents(self) -> list[str]:
        """Get list of dead agent names."""
        registry = self.get_registry()
        dead = []
        for name in registry:
            alive = is_agent_alive(self.team_name, name)
            if alive is False:
                dead.append(name)
        return dead


def check_all_alive(team_name: str) -> dict[str, Optional[bool]]:
    """Check all agents' alive status for a team.

    Returns:
        dict mapping agent_name to alive status (True/False/None)
    """
    registry = get_registry(team_name)
    return {name: is_agent_alive(team_name, name) for name in registry}


__all__ = ["SpawnBackend", "get_backend", "SpawnRegistryManager", "check_all_alive"]
