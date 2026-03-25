#!/usr/bin/env python3
"""
CyberTeam V4 - Workspace 模块
Git Worktree 隔离管理
"""

from .git import (
    GitWorktreeError,
    create_worktree,
    remove_worktree,
    commit_all,
    merge_branch,
    get_current_branch,
    list_worktrees,
    get_worktree_info
)
from .models import WorkspaceInfo, WorkspaceRegistry, WorkspaceStatus
from .manager import WorkspaceManager, DEFAULT_WORKSPACE_ROOT

__all__ = [
    # Git 操作
    "GitWorktreeError",
    "create_worktree",
    "remove_worktree",
    "commit_all",
    "merge_branch",
    "get_current_branch",
    "list_worktrees",
    "get_worktree_info",
    # 模型
    "WorkspaceInfo",
    "WorkspaceRegistry",
    "WorkspaceStatus",
    # 管理器
    "WorkspaceManager",
    "DEFAULT_WORKSPACE_ROOT"
]
