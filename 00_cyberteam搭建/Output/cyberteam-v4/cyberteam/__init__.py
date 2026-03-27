"""CyberTeam - Framework-agnostic multi-agent coordination CLI."""

import sys
from pathlib import Path

__version__ = "0.1.2"

# macOS 大小写不敏感，cyberteam/ 和 CYBERTEAM/ 是同一目录
# 将 cyberteam 目录自身加入 sys.path 以便能找到 mcp 子包
_cyberteam_dir = Path(__file__).parent
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))
if str(_cyberteam_dir) not in sys.path:
    sys.path.insert(0, str(_cyberteam_dir))

# MCP 模块导出
# 注意：由于 macOS 大小写不敏感，cyberteam.mcp 就是 CYBERTEAM.mcp
from mcp import MCPClient, MCPServerManager, ToolRegistry
