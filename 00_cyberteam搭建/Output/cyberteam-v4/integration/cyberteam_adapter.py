#!/usr/bin/env python3
"""
CyberTeam Adapter - 引擎适配层

封装 cyberteam 底层模块，提供简洁接口给 engine 层使用。
同时作为 ClawTeam 升级的缓冲层。

核心功能：
1. Team Management - 团队创建/删除/状态
2. Agent Spawning - Agent 生命周期管理
3. Task Management - 任务分配/追踪
4. Messaging - Agent 间消息传递
5. Workspace - Git Worktree 管理
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# 导入 cyberteam 底层模块（使用适配器模式隔离）
# ============================================================================

try:
    from cyberteam.team import TeamManager, TaskStore, MailboxManager, TaskStatus, TaskItem, TeamMessage, MessageType
    from cyberteam.spawn import get_backend
    from cyberteam.workspace import WorkspaceManager, WorkspaceInfo
    from cyberteam.transport import get_transport
    from cyberteam.config import load_config
    CYBERTEAM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"cyberteam 底层模块导入失败: {e}")
    CYBERTEAM_AVAILABLE = False


# ============================================================================
# 数据模型
# ============================================================================

class AgentStatus(Enum):
    """Agent 状态"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class AgentInfo:
    """Agent 信息"""
    name: str
    role: str
    team_name: str
    status: AgentStatus = AgentStatus.PENDING
    task_id: Optional[str] = None
    workspace_path: Optional[str] = None
    tmux_target: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_report: Optional[str] = None


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: str  # "success", "failure", "partial"
    output: Any = None
    summary: str = ""


@dataclass
class SwarmConfig:
    """Swarm 配置"""
    team_name: str
    goal: str
    max_agents: int = 5
    backend: str = "tmux"  # "tmux" | "subprocess"
    auto_cleanup: bool = True


# ============================================================================
# CyberTeamAdapter 主类
# ============================================================================

class CyberTeamAdapter:
    """
    CyberTeam 适配器 - Engine 层与底层 cyberteam 的桥梁

    使用适配器模式，隔离 engine 层与底层实现细节。
    如果 ClawTeam 升级，只需更新此类，engine 层保持不变。
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """初始化适配器

        Args:
            data_dir: 数据目录，默认使用 ~/.cyberteam/
        """
        self.data_dir = data_dir
        self._teams: dict[str, dict] = {}
        self._agents: dict[str, dict] = {}  # agent_name -> AgentInfo
        self._tasks: dict[str, dict] = {}

        if CYBERTEAM_AVAILABLE:
            self._init_backend()
        else:
            logger.warning("CyberTeam 底层不可用，使用模拟模式")

    def _init_backend(self) -> None:
        """初始化底层后端"""
        if not CYBERTEAM_AVAILABLE:
            return

        self.config = load_config()
        self.backend_name = self.config.default_backend or "tmux"
        self.backend = get_backend(self.backend_name)

        # 如果指定了 data_dir，设置环境变量
        if self.data_dir:
            import os
            os.environ["CYBERTEAM_DATA_DIR"] = str(self.data_dir)

    # =========================================================================
    # 团队管理
    # =========================================================================

    def create_team(self, team_name: str, description: str = "") -> dict:
        """
        创建团队

        Args:
            team_name: 团队名称
            description: 团队描述

        Returns:
            团队信息字典
        """
        if CYBERTEAM_AVAILABLE:
            from cyberteam.team.models import get_data_dir

            team_config = {
                "name": team_name,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "members": [],
            }

            # 写入团队配置
            team_dir = get_data_dir() / "teams" / team_name
            team_dir.mkdir(parents=True, exist_ok=True)
            config_file = team_dir / "config.json"
            config_file.write_text(json.dumps(team_config, indent=2, ensure_ascii=False))

            self._teams[team_name] = team_config
            logger.info(f"团队创建成功: {team_name}")
            return team_config
        else:
            # 模拟模式
            team_config = {
                "name": team_name,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
            }
            self._teams[team_name] = team_config
            return team_config

    def delete_team(self, team_name: str) -> bool:
        """删除团队"""
        if team_name in self._teams:
            del self._teams[team_name]

        # 清理相关 agents
        agents_to_delete = [a for a in self._agents.values() if a["team_name"] == team_name]
        for agent in agents_to_delete:
            self.stop_agent(agent["name"])

        logger.info(f"团队已删除: {team_name}")
        return True

    def list_teams(self) -> list[str]:
        """列出所有团队"""
        if CYBERTEAM_AVAILABLE:
            from cyberteam.team.models import get_data_dir
            teams_dir = get_data_dir() / "teams"
            if teams_dir.exists():
                return [d.name for d in teams_dir.iterdir() if d.is_dir()]
        return list(self._teams.keys())

    def get_team_info(self, team_name: str) -> Optional[dict]:
        """获取团队信息"""
        return self._teams.get(team_name)

    # =========================================================================
    # Agent 管理
    # =========================================================================

    def spawn_agent(
        self,
        team_name: str,
        agent_name: str,
        role: str,
        task: Optional[str] = None,
        backend: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> AgentInfo:
        """
        Spawn Agent

        Args:
            team_name: 团队名称
            agent_name: Agent 名称
            role: Agent 角色
            task: 初始任务
            backend: 后端类型 ("tmux" | "subprocess")
            profile: Agent Profile 名称

        Returns:
            AgentInfo 对象
        """
        backend = backend or self.backend_name

        # 确保团队存在
        if team_name not in self._teams:
            self.create_team(team_name)

        agent_info = AgentInfo(
            name=agent_name,
            role=role,
            team_name=team_name,
            status=AgentStatus.INITIALIZING,
        )

        if CYBERTEAM_AVAILABLE:
            try:
                # 使用 WorkspaceManager 创建独立工作区
                workspace_manager = WorkspaceManager.try_create()
                if workspace_manager:
                    ws_info = workspace_manager.create_workspace(
                        team_name=team_name,
                        agent_name=agent_name,
                        agent_id=uuid.uuid4().hex[:12],
                    )
                    agent_info.workspace_path = ws_info.worktree_path

                # 使用 spawn backend 启动 Agent
                spawn_backend = get_backend(backend)
                command = self._build_spawn_command(agent_name, role, task, profile)

                tmux_target = spawn_backend.spawn(
                    team_name=team_name,
                    agent_name=agent_name,
                    command=command,
                    task=task,
                )
                agent_info.tmux_target = tmux_target

                # 注册 Agent
                from cyberteam.spawn.registry import register_agent
                register_agent(
                    team_name=team_name,
                    agent_name=agent_name,
                    backend=backend,
                    tmux_target=tmux_target,
                )

                agent_info.status = AgentStatus.RUNNING
                logger.info(f"Agent spawn 成功: {agent_name} in {team_name}")

            except Exception as e:
                logger.error(f"Agent spawn 失败: {agent_name}, error: {e}")
                agent_info.status = AgentStatus.FAILED

        self._agents[agent_name] = {
            "name": agent_info.name,
            "role": agent_info.role,
            "team_name": agent_info.team_name,
            "status": agent_info.status.value,
            "workspace_path": agent_info.workspace_path,
            "tmux_target": agent_info.tmux_target,
        }

        return agent_info

    def _build_spawn_command(
        self,
        agent_name: str,
        role: str,
        task: Optional[str],
        profile: Optional[str],
    ) -> list[str]:
        """构建 spawn 命令"""
        # 基本命令
        cmd = ["python3", "-m", "cyberteam", "spawn", backend or "tmux"]

        if profile:
            cmd.extend(["--profile", profile])

        cmd.extend(["--team", self._teams[agent_name]["name"] if agent_name in self._agents else ""])
        cmd.extend(["--agent-name", agent_name])

        if task:
            cmd.extend(["--task", task])

        return cmd

    def stop_agent(self, agent_name: str, timeout: float = 3.0) -> bool:
        """停止 Agent"""
        if CYBERTEAM_AVAILABLE:
            try:
                from cyberteam.spawn.registry import stop_agent

                # 查找 agent 所属团队
                agent_info = self._agents.get(agent_name)
                if not agent_info:
                    return False

                team_name = agent_info["team_name"]
                return stop_agent(team_name, agent_name, timeout)
            except Exception as e:
                logger.error(f"停止 Agent 失败: {agent_name}, error: {e}")

        if agent_name in self._agents:
            self._agents[agent_name]["status"] = AgentStatus.STOPPED.value
            return True
        return False

    def is_agent_alive(self, agent_name: str) -> bool:
        """检查 Agent 是否存活"""
        if CYBERTEAM_AVAILABLE:
            try:
                from cyberteam.spawn.registry import is_agent_alive

                agent_info = self._agents.get(agent_name)
                if not agent_info:
                    return False

                team_name = agent_info["team_name"]
                return is_agent_alive(team_name, agent_name) is True
            except Exception:
                return False

        agent_info = self._agents.get(agent_name)
        return agent_info and agent_info["status"] == AgentStatus.RUNNING.value

    def list_agents(self, team_name: Optional[str] = None) -> list[AgentInfo]:
        """列出 Agents"""
        agents = []
        for name, info in self._agents.items():
            if team_name is None or info["team_name"] == team_name:
                agents.append(AgentInfo(**info))
        return agents

    # =========================================================================
    # 任务管理
    # =========================================================================

    def create_task(
        self,
        team_name: str,
        subject: str,
        description: str = "",
        owner: str = "",
        blocked_by: Optional[list[str]] = None,
    ) -> TaskItem:
        """创建任务"""
        if CYBERTEAM_AVAILABLE:
            task_store = TaskStore(team_name)
            task = task_store.create_task(
                subject=subject,
                description=description,
                owner=owner,
                blocked_by=blocked_by or [],
            )
            self._tasks[task.id] = {
                "id": task.id,
                "subject": task.subject,
                "status": task.status.value,
            }
            return task

        # 模拟模式
        task_id = uuid.uuid4().hex[:8]
        task_data = {
            "id": task_id,
            "subject": subject,
            "description": description,
            "owner": owner,
            "status": "pending",
            "blocked_by": blocked_by or [],
        }
        self._tasks[task_id] = task_data
        return TaskItem(**task_data)

    def assign_task(self, team_name: str, agent_name: str, task_id: str) -> bool:
        """分配任务给 Agent"""
        if CYBERTEAM_AVAILABLE:
            task_store = TaskStore(team_name)
            return task_store.assign_task(task_id, agent_name)

        if task_id in self._tasks:
            self._tasks[task_id]["owner"] = agent_name
            self._tasks[task_id]["status"] = "in_progress"
            return True
        return False

    def complete_task(self, team_name: str, task_id: str, result: str) -> bool:
        """完成任务"""
        if CYBERTEAM_AVAILABLE:
            task_store = TaskStore(team_name)
            return task_store.complete_task(task_id, result)

        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["result"] = result
            return True
        return False

    def get_task_status(self, team_name: str, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        if CYBERTEAM_AVAILABLE:
            task_store = TaskStore(team_name)
            task = task_store.get_task(task_id)
            if task:
                return {
                    "id": task.id,
                    "subject": task.subject,
                    "status": task.status.value,
                    "owner": task.owner,
                }

        task = self._tasks.get(task_id)
        return task

    # =========================================================================
    # 消息传递
    # =========================================================================

    def send_message(
        self,
        team_name: str,
        from_agent: str,
        to_agent: str,
        content: str,
        message_type: str = "message",
    ) -> bool:
        """发送消息"""
        if CYBERTEAM_AVAILABLE:
            mailbox = MailboxManager(team_name)
            return mailbox.send(from_agent, to_agent, content, message_type)

        # 模拟模式 - 简单存储
        msg_key = f"{to_agent}:{uuid.uuid4().hex[:8]}"
        self._tasks[msg_key] = {
            "from": from_agent,
            "to": to_agent,
            "content": content,
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return True

    def get_messages(self, team_name: str, agent_name: str, limit: int = 10) -> list[dict]:
        """获取消息"""
        if CYBERTEAM_AVAILABLE:
            mailbox = MailboxManager(team_name)
            return mailbox.get_messages(agent_name, limit)

        return []

    # =========================================================================
    # Swarm 编排
    # =========================================================================

    def create_swarm(self, config: SwarmConfig) -> dict:
        """创建 Swarm"""
        # 创建 Swarm 团队
        self.create_team(config.team_name, description=f"Swarm for: {config.goal}")

        swarm_info = {
            "team_name": config.team_name,
            "goal": config.goal,
            "max_agents": config.max_agents,
            "agents": [],
            "created_at": datetime.utcnow().isoformat(),
        }

        return swarm_info

    def get_swarm_status(self, team_name: str) -> dict:
        """获取 Swarm 状态"""
        agents = self.list_agents(team_name)
        alive_count = sum(1 for a in agents if self.is_agent_alive(a.name))

        return {
            "team_name": team_name,
            "total_agents": len(agents),
            "alive_agents": alive_count,
            "status": "running" if alive_count > 0 else "idle",
        }

    # =========================================================================
    # 工具方法
    # =========================================================================

    def health_check(self) -> dict:
        """健康检查"""
        return {
            "cyberteam_available": CYBERTEAM_AVAILABLE,
            "backend": self.backend_name if CYBERTEAM_AVAILABLE else "mock",
            "data_dir": str(self.data_dir) if self.data_dir else "~/.cyberteam/",
            "teams_count": len(self._teams),
            "agents_count": len(self._agents),
            "tasks_count": len(self._tasks),
        }


# ============================================================================
# 便捷函数
# ============================================================================

def create_adapter(data_dir: Optional[Path] = None) -> CyberTeamAdapter:
    """创建适配器实例的便捷函数"""
    return CyberTeamAdapter(data_dir)


def get_swarm_adapter() -> CyberTeamAdapter:
    """获取 Swarm 专用的适配器"""
    return CyberTeamAdapter()
