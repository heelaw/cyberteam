"""MCP - Model Context Protocol 集成模块

完全本地化实现，无外部依赖。
"""

from cyberteam.mcp.client import MCPClient
from cyberteam.mcp.server import MCPServerManager
from cyberteam.mcp.registry import ToolRegistry

__all__ = ["MCPClient", "MCPServerManager", "ToolRegistry"]
__version__ = "1.0.0"