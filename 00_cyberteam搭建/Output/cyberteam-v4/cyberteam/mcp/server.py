"""MCP 服务器管理器 - 本地化实现"""

import json
import subprocess
import asyncio
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


class MCPServerManager:
    """MCP 服务器管理器

    管理和本地 MCP 服务器的连接，支持启动、停止、重启操作。
    """

    def __init__(self, config_path: Optional[Path] = None):
        """初始化服务器管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._servers: Dict[str, MCPServerConfig] = {}
        self._processes: Dict[str, subprocess.Popen] = {}
        self._server_tasks: Dict[str, asyncio.subprocess.Process] = {}
        self._initialized = False

    def load_config(self, config_path: Optional[Path] = None) -> None:
        """加载服务器配置

        Args:
            config_path: 配置文件路径，默认使用初始化时的路径
        """
        path = config_path or self.config_path
        if not path:
            return

        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                servers = config.get("mcp_servers", [])
                for srv in servers:
                    name = srv.get("name")
                    if name:
                        self._servers[name] = MCPServerConfig(
                            name=name,
                            command=srv.get("command", ""),
                            args=srv.get("args", []),
                            env=srv.get("env", {}),
                            enabled=srv.get("enabled", True)
                        )
        self._initialized = True

    def add_server(self, config: MCPServerConfig) -> None:
        """添加服务器配置

        Args:
            config: 服务器配置
        """
        self._servers[config.name] = config

    def remove_server(self, name: str) -> bool:
        """移除服务器配置

        Args:
            name: 服务器名称

        Returns:
            是否成功移除
        """
        if name in self._servers:
            del self._servers[name]
            return True
        return False

    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """获取服务器配置

        Args:
            name: 服务器名称

        Returns:
            服务器配置
        """
        return self._servers.get(name)

    def list_servers(self) -> List[Dict[str, Any]]:
        """列出所有服务器

        Returns:
            服务器列表
        """
        return [
            {
                "name": name,
                "command": cfg.command,
                "args": cfg.args,
                "enabled": cfg.enabled,
                "running": name in self._processes
            }
            for name, cfg in self._servers.items()
        ]

    def start_server(self, name: str) -> bool:
        """启动服务器

        Args:
            name: 服务器名称

        Returns:
            是否成功启动
        """
        if name not in self._servers:
            logger.error(f"Server '{name}' not found")
            return False

        cfg = self._servers[name]
        if not cfg.enabled:
            logger.warning(f"Server '{name}' is disabled")
            return False

        if name in self._processes:
            logger.info(f"Server '{name}' is already running")
            return True

        try:
            env = {**subprocess.os.environ, **cfg.env}
            process = subprocess.Popen(
                [cfg.command] + cfg.args,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self._processes[name] = process
            logger.info(f"Server '{name}' started with PID {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start server '{name}': {e}")
            return False

    def stop_server(self, name: str) -> bool:
        """停止服务器

        Args:
            name: 服务器名称

        Returns:
            是否成功停止
        """
        if name not in self._processes:
            return False

        try:
            process = self._processes[name]
            process.terminate()
            process.wait(timeout=5)
            del self._processes[name]
            logger.info(f"Server '{name}' stopped")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            del self._processes[name]
            logger.info(f"Server '{name}' killed")
            return True
        except Exception as e:
            logger.error(f"Failed to stop server '{name}': {e}")
            return False

    def restart_server(self, name: str) -> bool:
        """重启服务器

        Args:
            name: 服务器名称

        Returns:
            是否成功重启
        """
        self.stop_server(name)
        return self.start_server(name)

    def start_all(self) -> Dict[str, bool]:
        """启动所有服务器

        Returns:
            启动结果字典
        """
        results = {}
        for name in self._servers:
            results[name] = self.start_server(name)
        return results

    def stop_all(self) -> None:
        """停止所有服务器"""
        for name in list(self._processes.keys()):
            self.stop_server(name)

    def is_running(self, name: str) -> bool:
        """检查服务器是否运行

        Args:
            name: 服务器名称

        Returns:
            是否运行
        """
        if name not in self._processes:
            return False
        process = self._processes[name]
        return process.poll() is None

    async def start_server_async(self, name: str) -> bool:
        """异步启动服务器

        Args:
            name: 服务器名称

        Returns:
            是否成功启动
        """
        if name not in self._servers:
            return False

        cfg = self._servers[name]
        if not cfg.enabled:
            return False

        try:
            process = await asyncio.create_subprocess_exec(
                cfg.command,
                *cfg.args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self._server_tasks[name] = process
            return True
        except Exception as e:
            logger.error(f"Failed to start server '{name}' async: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取服务器状态

        Returns:
            状态字典
        """
        return {
            "total": len(self._servers),
            "running": len(self._processes),
            "servers": self.list_servers()
        }

    def __repr__(self) -> str:
        return f"MCPServerManager(servers={len(self._servers)}, running={len(self._processes)})"


__all__ = ["MCPServerManager", "MCPServerConfig"]