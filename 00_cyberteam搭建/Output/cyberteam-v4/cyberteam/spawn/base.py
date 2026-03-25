from __future__ import annotations
from typing import Dict, List, Optional

"""Abstract base class for agent spawn backends."""


from abc import ABC, abstractmethod


class SpawnBackend(ABC):
    """Base class for different ways to spawn team agents."""

    @abstractmethod
    def spawn(
        self,
        command: List[str],
        agent_name: str,
        agent_id: str,
        agent_type: str,
        team_name: str,
        prompt: Optional[str] = None,
        env: Dict[str, str] | None = None,
        cwd: Optional[str] = None,
        skip_permissions: bool = False,
    ) -> str:
        """Spawn a new agent process. Returns a status message."""

    @abstractmethod
    def list_running(self) -> list[Dict[str, str]]:
        """List currently running agents."""
