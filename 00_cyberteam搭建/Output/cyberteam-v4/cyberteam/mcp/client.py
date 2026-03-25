"""MCP 客户端 - 完全本地化，无外部依赖"""

import json
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path
import asyncio


class MCPClient:
    """MCP 客户端 - 完全本地化，无外部依赖

    支持本地 MCP 服务器通信，提供工具调用和列表功能。
    """

    def __init__(self, project_path: Optional[Path] = None):
        """初始化 MCP 客户端

        Args:
            project_path: 项目根路径，默认为上一级目录
        """
        self.project_path = project_path or Path(__file__).parent.parent.parent
        self._tools_cache: Dict[str, Any] = {}
        self._server_process: Optional[subprocess.Popen] = None
        self._connected_servers: List[str] = []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        # 检查缓存
        if tool_name in self._tools_cache:
            tool_info = self._tools_cache[tool_name]
            handler = tool_info.get("handler")
            if handler:
                return handler(arguments)

        # 本地工具直接调用
        from cyberteam.mcp import registry
        tool_handler = registry.ToolRegistry.get_handler(tool_name)
        if tool_handler:
            return tool_handler(arguments)

        raise ValueError(f"Tool '{tool_name}' not found")

    async def call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """异步调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.call_tool, tool_name, arguments)

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具

        Returns:
            工具列表，每个工具包含 name, description, input_schema
        """
        from cyberteam.mcp import registry
        return registry.ToolRegistry.list_all_tools()

    def list_local_tools(self) -> List[Dict[str, Any]]:
        """列出本地注册的工具

        Returns:
            本地工具列表
        """
        return [
            tool for tool in self.list_tools()
            if tool.get("source") == "local"
        ]

    def register_tool(self, name: str, handler: callable, description: str = "",
                     input_schema: Optional[Dict[str, Any]] = None) -> None:
        """注册工具到本地缓存

        Args:
            name: 工具名称
            handler: 工具处理函数
            description: 工具描述
            input_schema: 输入模式
        """
        self._tools_cache[name] = {
            "handler": handler,
            "description": description,
            "input_schema": input_schema or {}
        }

    def cache_tools(self, tools: List[Dict[str, Any]]) -> None:
        """缓存工具列表

        Args:
            tools: 工具列表
        """
        for tool in tools:
            name = tool.get("name")
            if name:
                self._tools_cache[name] = tool

    def clear_cache(self) -> None:
        """清空工具缓存"""
        self._tools_cache.clear()

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息

        Args:
            tool_name: 工具名称

        Returns:
            工具信息字典
        """
        return self._tools_cache.get(tool_name)

    def __repr__(self) -> str:
        return f"MCPClient(project_path={self.project_path}, tools_count={len(self._tools_cache)})"


# 导出类
__all__ = ["MCPClient"]