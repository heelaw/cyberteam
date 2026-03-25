"""
CyberTeam V4 Engine - 核心引擎

包含：
- CEO 路由引擎
- 项目管理
- 部门调度
- 策略设计
- 辩论引擎
- 思维注入
"""

from .ceo import CEORouter, Complexity, Intent, RoutingTarget, RoutingResult
from .pm import PMCoordinator
from .department import DepartmentExecutor
from .strategy import StrategyEngine
from .debate import DebateEngine
from .thinking import ThinkingInjector, ThinkingRouter, ThinkingLoader

__all__ = [
    "CEORouter",
    "Complexity",
    "Intent",
    "RoutingTarget",
    "RoutingResult",
    "PMCoordinator",
    "DepartmentExecutor",
    "StrategyEngine",
    "DebateEngine",
    "ThinkingInjector",
    "ThinkingRouter",
    "ThinkingLoader",
]
