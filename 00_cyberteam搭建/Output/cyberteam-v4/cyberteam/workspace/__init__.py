"""Git worktree workspace isolation for ClawTeam agents."""

from __future__ import annotations

from pathlib import Path

from cyberteam.workspace.manager import WorkspaceManager
from typing import Union


def get_workspace_manager(repo_path: Optional[str] = None) -> Union[WorkspaceManager, None]:
    """Return a WorkspaceManager if inside a git repo, else None."""
    path = Path(repo_path) if repo_path else None
    return WorkspaceManager.try_create(path)
