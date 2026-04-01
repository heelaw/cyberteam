"""CyberTeam V4 - Enterprise AI Agent Swarm Intelligence System.

Layer 0: 核心引擎层（CEO、PM、部门调度等）
Layer 1: 底层能力层（融合 ClawTeam 的 Git Worktree、TMUX、消息传输等）
"""

__version__ = "4.0.0"

# 导入 Layer 0 核心引擎
try:
    from engine import CEO, PM, Department
except ImportError:
    pass

# 导入 Layer 1 底层能力
try:
    from CYBERTEAM.team import TeamManager
    from CYBERTEAM.board import BoardCollector
    from CYBERTEAM.mcp import MCPClient, ToolRegistry
except ImportError:
    pass

__all__ = [
    "__version__",
    "CEO",
    "PM", 
    "Department",
    "TeamManager",
    "BoardCollector",
    "MCPClient",
    "ToolRegistry",
]
