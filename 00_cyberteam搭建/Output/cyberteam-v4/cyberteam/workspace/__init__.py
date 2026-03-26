from __future__ import annotations
from typing import Optional

"""Git worktree workspace isolation for CyberTeam agents."""


from pathlib import Path

from cyberteam.workspace.manager import WorkspaceManager
from cyberteam.workspace.models import WorkspaceInfo, WorkspaceRegistry


def get_workspace_manager(repo_path: Optional[str] = None) -> WorkspaceManager | None:
    """Return a WorkspaceManager if inside a git repo, else None."""
    path = Path(repo_path) if repo_path else None
    return WorkspaceManager.try_create(path)


__all__ = [
    "WorkspaceManager",
    "WorkspaceInfo",
    "WorkspaceRegistry",
    "get_workspace_manager",
]
