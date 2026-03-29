"""
CyberTeam V4 - 思维注入中台

核心思想：
- 思维专家不是独立的 Agent，而是决策工具
- 每个 Agent 在决策时可以注入合适的思维模型
- 根据任务特征，动态组合 1-3 个思维模型
"""

from .loader import ThinkingLoader
from .injector import ThinkingInjector
from .router import ThinkingRouter
from .models import (
    ThinkingModel,
    ThinkingResult,
    ModelCombination,
    TaskContext
)
from .injector import InjectionContext, InjectionResult

__all__ = [
    "ThinkingLoader",
    "ThinkingInjector",
    "ThinkingRouter",
    "ThinkingModel",
    "ThinkingResult",
    "ModelCombination",
    "TaskContext",
    "InjectionContext",
    "InjectionResult",
]
