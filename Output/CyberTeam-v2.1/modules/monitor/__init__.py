"""
CyberTeam Execution Monitor
============================

基于 PentAGI Execution Monitoring 设计

模块:
- config: 监控配置
- detector: 循环检测器
- intervention: Mentor/Adviser Agent
- limits: 工具调用限制
- utils: 工具函数
- monitor: 主监控器

快速开始:
```python
from monitor import ExecutionMonitor

# 创建监控器
monitor = ExecutionMonitor()

# 启动监控
monitor.start(agent_id="agent-1")

# 检查工具调用
result = monitor.check(agent_id="agent-1", tool_name="read", arguments={})
if not result.allowed:
    print(f"调用被阻止: {result.warnings}")
else:
    # 执行工具
    ...

# 记录调用结果
monitor.record(agent_id="agent-1", tool_name="read", arguments={}, result=data)

# 获取状态
status = monitor.get_status(agent_id="agent-1")
print(status)

# 停止监控
monitor.stop(agent_id="agent-1")
```
"""

from .config import MonitorConfig, DEFAULT_CONFIG, get_config
from .monitor import ExecutionMonitor, MonitorResult, create_monitor
from .detector import LoopDetector, LoopDetectionResult
from .intervention import MentorAgent, InterventionResult, InterventionAction
from .limits import ToolLimits, LimitStatus, LimitCheckResult
from .utils import (
    ToolCall, Alert, AlertLevel, IssueType,
    calculate_sequence_similarity, find_repeated_pattern,
    analyze_tool_frequency, get_time_window_calls
)

__version__ = "2.1.0"

__all__ = [
    # Config
    'MonitorConfig',
    'DEFAULT_CONFIG',
    'get_config',

    # Monitor
    'ExecutionMonitor',
    'MonitorResult',
    'create_monitor',

    # Detector
    'LoopDetector',
    'LoopDetectionResult',

    # Intervention
    'MentorAgent',
    'InterventionResult',
    'InterventionAction',

    # Limits
    'ToolLimits',
    'LimitStatus',
    'LimitCheckResult',

    # Utils
    'ToolCall',
    'Alert',
    'AlertLevel',
    'IssueType',
    'calculate_sequence_similarity',
    'find_repeated_pattern',
    'analyze_tool_frequency',
    'get_time_window_calls'
]
