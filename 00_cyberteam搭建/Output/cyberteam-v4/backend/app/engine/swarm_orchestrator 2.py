"""Swarm 编排器 - 统一入口。

此模块从项目根目录的 swarm_orchestrator.py 导入核心实现。
"""

# 从项目根目录导入核心 SwarmOrchestrator
try:
    from swarm_orchestrator import SwarmOrchestrator, SwarmStatus, SubAgent, ExecutionResult
    CORE_SWARM_AVAILABLE = True
except ImportError:
    CORE_SWARM_AVAILABLE = False
    # 如果导入失败，定义占位符
    class SwarmOrchestrator:
        """Swarm 编排器占位符（导入失败）"""
        pass

    class SwarmStatus:
        """Swarm 状态占位符"""
        pass

    class SubAgent:
        """子 Agent 占位符"""
        pass

    class ExecutionResult:
        """执行结果占位符"""
        pass

import logging

log = logging.getLogger("cyberteam.swarm_orchestrator")

# 导出核心类和函数
__all__ = [
    "SwarmOrchestrator",
    "SwarmStatus",
    "SubAgent",
    "ExecutionResult",
]

if CORE_SWARM_AVAILABLE:
    log.info("Using root-level swarm_orchestrator.py as authoritative source")
else:
    log.warning("Root-level swarm_orchestrator.py not available, using placeholder classes")
