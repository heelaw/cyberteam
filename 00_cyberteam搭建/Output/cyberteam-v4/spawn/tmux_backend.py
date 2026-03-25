#!/usr/bin/env python3
"""
CyberTeam V4 - Tmux Backend
实现基于 tmux 的 Agent Spawn
"""

import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional, List, Dict

from .registry import SpawnRegistryManager, AgentInfo


class TmuxBackendError(Exception):
    """Tmux Backend 操作异常"""
    pass


class TmuxBackend:
    """Tmux 会话管理"""

    def __init__(self, team_name: str):
        self.team_name = team_name
        self.session_name = f"cyberteam-{team_name}"
        self.registry = SpawnRegistryManager(team_name)

        # 初始化 tmux session
        self._ensure_session()

    def _ensure_session(self) -> None:
        """确保 tmux session 存在"""
        result = subprocess.run(
            ["tmux", "has-session", "-t", self.session_name],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # 创建新 session
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", self.session_name, "-n", "leader"],
                check=True
            )

    @staticmethod
    def session_name(team_name: str) -> str:
        """获取 session 名称"""
        return f"cyberteam-{team_name}"

    def spawn(
        self,
        agent_name: str,
        command: str,
        prompt: Optional[str] = None,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        skip_permissions: bool = False
    ) -> AgentInfo:
        """
        Spawn Agent 到 tmux window

        Args:
            agent_name: Agent 名称
            command: 启动命令
            prompt: 协作提示词
            cwd: 工作目录
            env: 环境变量
            skip_permissions: 是否跳过权限检查

        Returns:
            AgentInfo
        """
        window_name = agent_name
        full_command = self._prepare_command(
            command,
            prompt=prompt,
            cwd=cwd,
            skip_permissions=skip_permissions
        )

        # 构建 tmux 命令
        target = f"{self.session_name}:{window_name}"

        # 创建新窗口
        try:
            subprocess.run(
                ["tmux", "new-window", "-t", self.session_name, "-n", window_name, full_command],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise TmuxBackendError(f"Failed to create tmux window: {e}")

        # 获取 pane PID
        pane_pid = self._get_pane_pid(target)

        # 注册 Agent
        agent = self.registry.register(
            agent_name=agent_name,
            backend="tmux",
            pid=pane_pid,
            tmux_target=target,
            command=command
        )

        return agent

    def _prepare_command(
        self,
        command: str,
        prompt: Optional[str] = None,
        cwd: Optional[Path] = None,
        skip_permissions: bool = False
    ) -> str:
        """准备命令"""
        parts = []

        # 添加协作提示词
        if prompt:
            parts.append(f'echo "{prompt}" && ')

        # 处理命令
        cmd = command
        if skip_permissions:
            # 添加 --dangerously-skip-permissions
            if "claude" in cmd and "--dangerously-skip-permissions" not in cmd:
                cmd = cmd.replace("claude", "claude --dangerously-skip-permissions", 1)

        parts.append(cmd)

        return " && ".join(parts)

    def _get_pane_pid(self, target: str) -> Optional[int]:
        """获取 pane PID"""
        try:
            result = subprocess.run(
                ["tmux", "display-message", "-t", target, "-p", "#{pane_pid}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError):
            pass
        return None

    def send_keys(self, agent_name: str, keys: str) -> None:
        """向 Agent 发送按键"""
        target = f"{self.session_name}:{agent_name}"
        subprocess.run(
            ["tmux", "send-keys", "-t", target, keys, "Enter"],
            check=True
        )

    def capture_pane(self, agent_name: str) -> str:
        """捕获 pane 内容"""
        target = f"{self.session_name}:{agent_name}"
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p"],
            capture_output=True,
            text=True
        )
        return result.stdout

    def resize_pane(self, agent_name: str, width: int, height: int) -> None:
        """调整 pane 大小"""
        target = f"{self.session_name}:{agent_name}"
        subprocess.run(
            ["tmux", "resize-pane", "-t", target, f"-x{width}", f"-y{height}"],
            check=True
        )

    def kill_window(self, agent_name: str) -> None:
        """杀死窗口"""
        target = f"{self.session_name}:{agent_name}"
        subprocess.run(
            ["tmux", "kill-window", "-t", target],
            check=False
        )
        self.registry.unregister(agent_name)

    def list_windows(self) -> List[str]:
        """列出所有窗口"""
        result = subprocess.run(
            ["tmux", "list-windows", "-t", self.session_name, "-F", "#{window_name}"],
            capture_output=True,
            text=True
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def tile_panes(self) -> str:
        """平铺所有窗口"""
        # 获取所有窗口
        windows = self.list_windows()

        if len(windows) <= 1:
            return "Only one window, no need to tile"

        # 尝试合并窗口到第一个窗口
        for window in windows[1:]:
            source = f"{self.session_name}:{window}"
            target = f"{self.session_name}:{windows[0]}"
            try:
                subprocess.run(
                    ["tmux", "join-pane", "-s", source, "-t", target, "-h"],
                    check=False
                )
            except Exception:
                pass

        # 设置平铺布局
        subprocess.run(
            ["tmux", "select-layout", "-t", self.session_name, "tiled"],
            check=False
        )

        return f"Tiled {len(windows)} windows"

    def attach_all(self) -> None:
        """平铺并附加到 session"""
        self.tile_panes()
        subprocess.run(
            ["tmux", "attach-session", "-t", self.session_name],
            check=False
        )

    def detach(self) -> None:
        """分离 session"""
        subprocess.run(
            ["tmux", "detach", "-s", self.session_name],
            check=False
        )

    def kill_session(self) -> None:
        """杀死整个 session"""
        # 注销所有 Agent
        for agent in self.registry.list_all():
            self.registry.unregister(agent.agent_name)

        # 杀死 session
        subprocess.run(
            ["tmux", "kill-session", "-t", self.session_name],
            check=False
        )


def spawn_tmux_agent(
    team_name: str,
    agent_name: str,
    command: str,
    prompt: Optional[str] = None
) -> AgentInfo:
    """便捷函数：Spawn tmux Agent"""
    backend = TmuxBackend(team_name)
    return backend.spawn(agent_name, command, prompt=prompt)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        team_name = sys.argv[1]
        agent_name = sys.argv[2]
    else:
        team_name = "test-team"
        agent_name = "test-agent"

    print(f"\n{'='*50}")
    print(f"Tmux Backend 测试 - Team: {team_name}")
    print(f"{'='*50}")

    backend = TmuxBackend(team_name)

    print(f"\n【Session】: {backend.session_name}")
    print(f"\n【窗口列表】: {backend.list_windows()}")

    print(f"\n【可用命令】")
    print(f"  - tmux attach-session -t {backend.session_name}")
    print(f"  - tmux list-windows -t {backend.session_name}")
