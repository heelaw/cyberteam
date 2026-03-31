"""
WorktreeManager - Git Worktree生命周期管理

管理Agent的Git Worktree创建、切换和清理
"""

import subprocess
import os
from typing import Dict, Optional, List
from datetime import datetime


class WorktreeManager:
    """Git Worktree管理器"""

    def __init__(self, base_path: str = None):
        """
        初始化WorktreeManager

        Args:
            base_path: Worktree根目录，默认为当前目录的 .worktrees/
        """
        self._base_path = base_path or os.path.join(os.getcwd(), ".worktrees")
        self._worktrees: dict[str, dict] = {}
        os.makedirs(self._base_path, exist_ok=True)

    def create_worktree(self, agent_id: str, branch: str, base_branch: str = "main") -> str:
        """
        为Agent创建Worktree

        Args:
            agent_id: Agent标识
            branch: 要创建的分支名
            base_branch: 基于哪个分支

        Returns:
            worktree_path: Worktree目录路径
        """
        if agent_id in self._worktrees:
            raise ValueError(f"Worktree for agent {agent_id} already exists")

        worktree_path = os.path.join(self._base_path, f"{agent_id}")

        try:
            # 创建worktree命令
            cmd = [
                "git", "worktree", "add",
                "-b", branch,
                worktree_path,
                base_branch
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # 记录worktree信息
            self._worktrees[agent_id] = {
                "path": worktree_path,
                "branch": branch,
                "base_branch": base_branch,
                "created_at": datetime.now().isoformat(),
                "status": "active",
            }

            return worktree_path

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create worktree: {e.stderr.decode()}")

    def cleanup_worktree(self, agent_id: str) -> bool:
        """
        清理Agent的Worktree

        Args:
            agent_id: Agent标识

        Returns:
            是否成功清理
        """
        if agent_id not in self._worktrees:
            return False

        worktree_info = self._worktrees[agent_id]
        worktree_path = worktree_info["path"]

        try:
            # 删除worktree
            subprocess.run(
                ["git", "worktree", "remove", worktree_path, "--force"],
                check=True,
                capture_output=True
            )

            # 移除分支（如果存在）
            subprocess.run(
                ["git", "branch", "-D", worktree_info["branch"]],
                check=False,  # 忽略错误（分支可能已合并）
                capture_output=True
            )

            self._worktrees[agent_id]["status"] = "removed"
            del self._worktrees[agent_id]
            return True

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to cleanup worktree: {e.stderr.decode()}")

    def get_worktree_path(self, agent_id: str) -> Optional[str]:
        """获取Agent的Worktree路径"""
        if agent_id in self._worktrees:
            return self._worktrees[agent_id]["path"]
        return None

    def list_worktrees(self) -> list[dict]:
        """列出所有Worktree"""
        return [
            {
                "agent_id": agent_id,
                **info
            }
            for agent_id, info in self._worktrees.items()
        ]

    def get_active_worktree(self, agent_id: str) -> Optional[str]:
        """获取当前工作目录（如果在该agent的worktree中）"""
        cwd = os.getcwd()
        if agent_id in self._worktrees:
            wt_path = self._worktrees[agent_id]["path"]
            if cwd.startswith(wt_path):
                return wt_path
        return None