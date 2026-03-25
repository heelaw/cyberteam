#!/usr/bin/env python3
"""
CyberTeam V4 - Workspace 管理器
管理 Git Worktree 的创建、提交、合并、清理
"""

import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict

from .git import (
    GitWorktreeError,
    create_worktree,
    remove_worktree,
    delete_branch,
    commit_all,
    merge_branch,
    get_worktree_info,
    get_current_branch,
    list_worktrees as git_list_worktrees
)
from .models import WorkspaceInfo, WorkspaceRegistry, WorkspaceStatus


# 默认工作区根目录
DEFAULT_WORKSPACE_ROOT = Path.home() / ".cyberteam" / "workspaces"


class WorkspaceManager:
    """工作区管理器"""

    def __init__(
        self,
        team_name: str,
        repo_root: Optional[Path] = None,
        workspace_root: Optional[Path] = None
    ):
        self.team_name = team_name
        self.repo_root = repo_root or Path.cwd()
        self.workspace_root = workspace_root or DEFAULT_WORKSPACE_ROOT / team_name
        self.registry_path = self.workspace_root / "workspace-registry.json"

        # 确保目录存在
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        # 加载注册表
        self.registry = self._load_registry()

    def _load_registry(self) -> WorkspaceRegistry:
        """加载注册表"""
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                return WorkspaceRegistry.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass

        return WorkspaceRegistry(team_name=self.team_name, repo_root=str(self.repo_root))

    def _save_registry(self) -> None:
        """保存注册表"""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(self.registry.to_dict(), indent=2, ensure_ascii=False))

    def create_workspace(
        self,
        agent_name: str,
        agent_id: Optional[str] = None,
        base_branch: str = "HEAD"
    ) -> WorkspaceInfo:
        """
        创建独立工作区 (Git Worktree)

        Args:
            agent_name: Agent 名称
            agent_id: Agent ID
            base_branch: 基准分支

        Returns:
            WorkspaceInfo
        """
        agent_id = agent_id or str(uuid.uuid4())[:8]
        branch = f"cyberteam/{self.team_name}/{agent_name}"
        wt_path = self.workspace_root / agent_name

        # 创建 worktree
        create_worktree(
            repo_root=self.repo_root,
            worktree_path=wt_path,
            branch=branch,
            base_ref=base_branch
        )

        # 创建工作区信息
        info = WorkspaceInfo(
            agent_name=agent_name,
            agent_id=agent_id,
            team_name=self.team_name,
            branch_name=branch,
            worktree_path=str(wt_path),
            status=WorkspaceStatus.ACTIVE
        )

        # 注册
        self.registry.add(info)
        self._save_registry()

        return info

    def commit_workspace(
        self,
        agent_name: str,
        message: Optional[str] = None
    ) -> str:
        """
        提交工作区更改

        Args:
            agent_name: Agent 名称
            message: 提交信息

        Returns:
            commit hash
        """
        ws = self.registry.get(agent_name)
        if not ws:
            raise ValueError(f"Workspace not found for agent: {agent_name}")

        wt_path = Path(ws.worktree_path)
        if not wt_path.exists():
            raise ValueError(f"Worktree path does not exist: {wt_path}")

        # 默认提交信息
        if not message:
            message = f"Checkpoint by {agent_name} ({ws.team_name})"

        # 提交
        commit_hash = commit_all(wt_path, message)

        # 更新注册表
        ws.last_commit_at = ws.created_at  # 简化，实际应该用当前时间
        ws.commit_message = message
        ws.commit_hash = commit_hash
        ws.status = WorkspaceStatus.COMMITED
        self._save_registry()

        return commit_hash

    def merge_workspace(
        self,
        agent_name: str,
        target_branch: str = "main"
    ) -> None:
        """
        合并工作区到主分支

        Args:
            agent_name: Agent 名称
            target_branch: 目标分支
        """
        ws = self.registry.get(agent_name)
        if not ws:
            raise ValueError(f"Workspace not found for agent: {agent_name}")

        # 合并
        merge_branch(
            repo_root=self.repo_root,
            branch=ws.branch_name,
            target=target_branch
        )

        # 更新状态
        ws.status = WorkspaceStatus.MERGED
        self._save_registry()

    def remove_workspace(
        self,
        agent_name: str,
        delete_branch: bool = True
    ) -> None:
        """
        移除工作区

        Args:
            agent_name: Agent 名称
            delete_branch: 是否删除分支
        """
        ws = self.registry.get(agent_name)
        if not ws:
            raise ValueError(f"Workspace not found for agent: {agent_name}")

        wt_path = Path(ws.worktree_path)

        # 删除 worktree
        if wt_path.exists():
            remove_worktree(repo_root=self.repo_root, worktree_path=wt_path, force=True)

        # 删除分支
        if delete_branch:
            delete_branch(repo_root=self.repo_root, branch=ws.branch_name)

        # 更新注册表
        self.registry.remove(agent_name)
        self._save_registry()

    def get_workspace(self, agent_name: str) -> Optional[WorkspaceInfo]:
        """获取工作区信息"""
        return self.registry.get(agent_name)

    def list_workspaces(self, active_only: bool = False) -> List[WorkspaceInfo]:
        """列出所有工作区"""
        if active_only:
            return self.registry.list_active()
        return self.registry.workspaces

    def get_status(self) -> Dict:
        """获取工作区状态概览"""
        workspaces = self.registry.list_active()
        return {
            "team_name": self.team_name,
            "repo_root": str(self.repo_root),
            "workspace_root": str(self.workspace_root),
            "active_count": len(workspaces),
            "total_count": len(self.registry.workspaces),
            "workspaces": [ws.to_dict() for ws in workspaces]
        }

    def cleanup_all(self) -> List[str]:
        """清理所有已合并的工作区"""
        removed = []
        for ws in self.registry.workspaces:
            if ws.status == WorkspaceStatus.MERGED:
                try:
                    self.remove_workspace(ws.agent_name)
                    removed.append(ws.agent_name)
                except Exception as e:
                    print(f"Failed to remove {ws.agent_name}: {e}")
        return removed


def main():
    """CLI 测试"""
    import sys

    if len(sys.argv) > 1:
        team_name = sys.argv[1]
    else:
        team_name = "test-team"

    print(f"\n{'='*50}")
    print(f"Workspace 管理器测试 - Team: {team_name}")
    print(f"{'='*50}")

    manager = WorkspaceManager(team_name)

    print(f"\n【状态概览】")
    status = manager.get_status()
    for k, v in status.items():
        if k != "workspaces":
            print(f"  {k}: {v}")

    print(f"\n【活跃工作区】")
    for ws in manager.list_workspaces(active_only=True):
        print(f"  - {ws.agent_name}: {ws.worktree_path}")


if __name__ == "__main__":
    main()
