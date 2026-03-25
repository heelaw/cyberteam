#!/usr/bin/env python3
"""
CyberTeam V4 - Workspace 数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class WorkspaceStatus(Enum):
    """工作区状态"""
    ACTIVE = "active"
    IDLE = "idle"
    COMMITED = "committed"
    MERGED = "merged"
    REMOVED = "removed"


@dataclass
class WorkspaceInfo:
    """工作区信息"""
    agent_name: str
    agent_id: str
    team_name: str
    branch_name: str
    worktree_path: str
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_commit_at: Optional[str] = None
    commit_message: Optional[str] = None
    commit_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "team_name": self.team_name,
            "branch_name": self.branch_name,
            "worktree_path": self.worktree_path,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_commit_at": self.last_commit_at,
            "commit_message": self.commit_message,
            "commit_hash": self.commit_hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceInfo":
        status = data.get("status", "active")
        if isinstance(status, str):
            status = WorkspaceStatus(status)
        return cls(
            agent_name=data["agent_name"],
            agent_id=data["agent_id"],
            team_name=data["team_name"],
            branch_name=data["branch_name"],
            worktree_path=data["worktree_path"],
            status=status,
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            last_commit_at=data.get("last_commit_at"),
            commit_message=data.get("commit_message"),
            commit_hash=data.get("commit_hash")
        )


@dataclass
class WorkspaceRegistry:
    """工作区注册表"""
    team_name: str
    workspaces: List[WorkspaceInfo] = field(default_factory=list)
    repo_root: str = ""

    def add(self, ws: WorkspaceInfo) -> None:
        """添加工作区"""
        # 检查是否已存在
        for existing in self.workspaces:
            if existing.agent_name == ws.agent_name:
                existing.status = WorkspaceStatus.ACTIVE
                existing.branch_name = ws.branch_name
                existing.worktree_path = ws.worktree_path
                return
        self.workspaces.append(ws)

    def get(self, agent_name: str) -> Optional[WorkspaceInfo]:
        """获取工作区"""
        for ws in self.workspaces:
            if ws.agent_name == agent_name:
                return ws
        return None

    def remove(self, agent_name: str) -> bool:
        """移除工作区"""
        for i, ws in enumerate(self.workspaces):
            if ws.agent_name == agent_name:
                ws.status = WorkspaceStatus.REMOVED
                return True
        return False

    def list_active(self) -> List[WorkspaceInfo]:
        """列出活跃工作区"""
        return [ws for ws in self.workspaces if ws.status == WorkspaceStatus.ACTIVE]

    def to_dict(self) -> dict:
        return {
            "team_name": self.team_name,
            "repo_root": self.repo_root,
            "workspaces": [ws.to_dict() for ws in self.workspaces]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkspaceRegistry":
        ws_list = [WorkspaceInfo.from_dict(ws) for ws in data.get("workspaces", [])]
        return cls(
            team_name=data["team_name"],
            repo_root=data.get("repo_root", ""),
            workspaces=ws_list
        )
