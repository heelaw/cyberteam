"""CyberTeam V4 - Enterprise AI Agent Swarm Intelligence System."""

__version__ = "4.0.0"

# Layer 1 - CYBERTEAM (ClawTeam integration)
from cyberteam.team.models import TaskPriority, TaskStatus
from cyberteam.team.manager import TeamManager
from cyberteam.team.tasks import TaskStore
from cyberteam.board.collector import BoardCollector

# Layer 0 - Core MCP exports
from .mcp import MCPClient, MCPServerManager, ToolRegistry

__all__ = [
    # Version
    "__version__",
    # CYBERTEAM (Layer 1)
    "TaskPriority",
    "TaskStatus",
    "TaskStore",
    "TeamManager",
    "BoardCollector",
    # MCP (Layer 0)
    "MCPClient",
    "MCPServerManager",
    "ToolRegistry",
]
