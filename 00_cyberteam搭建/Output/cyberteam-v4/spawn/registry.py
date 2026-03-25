#!/usr/bin/env python3
"""
CyberTeam V4 - Agent Spawn 注册表
管理 Agent 进程注册和存活检查
"""

import json
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

# 默认注册表路径
DEFAULT_REGISTRY_DIR = Path.home() / ".cyberteam" / "spawn"
DEFAULT_REGISTRY_FILE = "spawn_registry.json"


@dataclass
class AgentInfo:
    """Agent 信息"""
    agent_id: str
    agent_name: str
    team_name: str
    backend: str  # "tmux" | "subprocess"
    pid: Optional[int] = None
    tmux_target: Optional[str] = None
    command: Optional[str] = None
    status: str = "running"  # running | dead | unknown
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_heartbeat: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "team_name": self.team_name,
            "backend": self.backend,
            "pid": self.pid,
            "tmux_target": self.tmux_target,
            "command": self.command,
            "status": self.status,
            "created_at": self.created_at,
            "last_heartbeat": self.last_heartbeat
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentInfo":
        return cls(**data)


@dataclass
class SpawnRegistry:
    """Spawn 注册表"""
    team_name: str
    agents: List[AgentInfo] = field(default_factory=list)

    def add(self, agent: AgentInfo) -> None:
        """添加 Agent"""
        for existing in self.agents:
            if existing.agent_name == agent.agent_name:
                # 更新
                existing.status = agent.status
                existing.pid = agent.pid
                existing.tmux_target = agent.tmux_target
                existing.last_heartbeat = agent.last_heartbeat
                return
        self.agents.append(agent)

    def get(self, agent_name: str) -> Optional[AgentInfo]:
        for agent in self.agents:
            if agent.agent_name == agent_name:
                return agent
        return None

    def remove(self, agent_name: str) -> bool:
        for i, agent in enumerate(self.agents):
            if agent.agent_name == agent_name:
                self.agents.pop(i)
                return True
        return False

    def list_all(self) -> List[AgentInfo]:
        return self.agents

    def list_alive(self) -> List[AgentInfo]:
        return [a for a in self.agents if a.status == "running"]

    def to_dict(self) -> dict:
        return {
            "team_name": self.team_name,
            "agents": [a.to_dict() for a in self.agents]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpawnRegistry":
        agents = [AgentInfo.from_dict(a) for a in data.get("agents", [])]
        return cls(team_name=data["team_name"], agents=agents)


class SpawnRegistryManager:
    """Spawn 注册表管理器"""

    def __init__(self, team_name: str, registry_dir: Optional[Path] = None):
        self.team_name = team_name
        self.registry_dir = registry_dir or DEFAULT_REGISTRY_DIR / team_name
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.registry_dir / "spawn_registry.json"

        # 加载注册表
        self.registry = self._load()

    def _load(self) -> SpawnRegistry:
        """加载注册表"""
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                return SpawnRegistry.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return SpawnRegistry(team_name=self.team_name)

    def _save(self) -> None:
        """保存注册表"""
        self.registry_path.write_text(
            json.dumps(self.registry.to_dict(), indent=2, ensure_ascii=False)
        )

    def register(
        self,
        agent_name: str,
        backend: str,
        pid: Optional[int] = None,
        tmux_target: Optional[str] = None,
        command: Optional[str] = None
    ) -> AgentInfo:
        """注册 Agent"""
        agent_id = str(uuid.uuid4())[:8]

        agent = AgentInfo(
            agent_id=agent_id,
            agent_name=agent_name,
            team_name=self.team_name,
            backend=backend,
            pid=pid,
            tmux_target=tmux_target,
            command=command,
            status="running"
        )

        self.registry.add(agent)
        self._save()

        return agent

    def unregister(self, agent_name: str) -> bool:
        """注销 Agent"""
        result = self.registry.remove(agent_name)
        if result:
            self._save()
        return result

    def get(self, agent_name: str) -> Optional[AgentInfo]:
        """获取 Agent 信息"""
        return self.registry.get(agent_name)

    def list_all(self) -> List[AgentInfo]:
        """列出所有 Agent"""
        return self.registry.list_all()

    def list_alive(self) -> List[AgentInfo]:
        """列出存活的 Agent"""
        return self.registry.list_alive()

    def update_status(self, agent_name: str, status: str) -> bool:
        """更新 Agent 状态"""
        agent = self.registry.get(agent_name)
        if agent:
            agent.status = status
            agent.last_heartbeat = datetime.utcnow().isoformat()
            self._save()
            return True
        return False


# ============ 存活检查函数 ============

def is_agent_alive(team_name: str, agent_name: str) -> Optional[bool]:
    """
    检查 Agent 是否存活

    Returns:
        True  = 存活
        False = 已死亡
        None  = 未知
    """
    registry_dir = DEFAULT_REGISTRY_DIR / team_name
    registry_path = registry_dir / "spawn_registry.json"

    if not registry_path.exists():
        return None

    try:
        data = json.loads(registry_path.read_text())
        agents = data.get("agents", [])

        for agent in agents:
            if agent["agent_name"] == agent_name:
                backend = agent.get("backend")

                if backend == "tmux":
                    return _check_tmux_alive(agent.get("tmux_target"))
                elif backend == "subprocess":
                    return _check_pid_alive(agent.get("pid"))
                else:
                    return None

        return None
    except (json.JSONDecodeError, KeyError):
        return None


def _check_tmux_alive(tmux_target: str) -> Optional[bool]:
    """检查 tmux pane 是否存活"""
    if not tmux_target:
        return None

    try:
        result = subprocess.run(
            ["tmux", "list-panes", "-t", tmux_target, "-F", "#{pane_dead}"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False

        return "1" not in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _check_pid_alive(pid: int) -> bool:
    """检查 PID 是否存活"""
    if not pid:
        return False

    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid="],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_all_alive(team_name: str) -> Dict[str, Optional[bool]]:
    """检查所有 Agent 存活状态"""
    registry_dir = DEFAULT_REGISTRY_DIR / team_name
    registry_path = registry_dir / "spawn_registry.json"

    if not registry_path.exists():
        return {}

    try:
        data = json.loads(registry_path.read_text())
        agents = data.get("agents", [])

        result = {}
        for agent in agents:
            name = agent["agent_name"]
            backend = agent.get("backend")

            if backend == "tmux":
                result[name] = _check_tmux_alive(agent.get("tmux_target"))
            elif backend == "subprocess":
                result[name] = _check_pid_alive(agent.get("pid"))
            else:
                result[name] = None

        return result
    except (json.JSONDecodeError, KeyError):
        return {}


if __name__ == "__main__":
    # 测试
    print("Spawn Registry 测试")
    print("=" * 50)

    # 测试检查
    alive_status = check_all_alive("test-team")
    print(f"\n存活状态: {alive_status}")
