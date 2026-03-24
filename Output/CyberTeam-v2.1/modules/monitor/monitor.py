"""
CyberTeam Execution Monitor
===========================
基于 PentAGI Execution Monitoring 设计

整合:
- Loop Detection: 循环检测
- Mentor/Adviser Agent: 智能干预
- Tool Call Limits: 工具调用限制

使用方式:
```python
from monitor import ExecutionMonitor

monitor = ExecutionMonitor()
monitor.start(agent_id="agent-1")

# 在每次工具调用前检查
result = monitor.check(agent_id="agent-1", tool_name="read", arguments={})
if not result.allowed:
    print(f"调用被阻止: {result.reason}")
    return

# 记录工具调用
monitor.record(agent_id="agent-1", tool_name="read", arguments={"file": "test.py"})

# 获取监控状态
status = monitor.get_status(agent_id="agent-1")
print(status)
```
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from .config import MonitorConfig, DEFAULT_CONFIG
from .detector import LoopDetector, LoopDetectionResult
from .intervention import MentorAgent, InterventionResult, InterventionAction
from .limits import ToolLimits, LimitCheckResult
from .utils import ToolCall, Alert, AlertLevel, IssueType


@dataclass
class MonitorResult:
    """监控结果"""
    allowed: bool
    should_continue: bool
    alerts: List[Alert] = field(default_factory=list)
    intervention: Optional[InterventionResult] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionMonitor:
    """
    执行监控器

    整合循环检测、智能干预和调用限制
    """

    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or DEFAULT_CONFIG

        # 初始化组件
        self.loop_detector = LoopDetector(self.config.loop_detection)
        self.mentor_agent = MentorAgent(self.config.intervention)
        self.tool_limits = ToolLimits(self.config.limits)

        # 日志
        self.logger = logging.getLogger(__name__)

        # 回调函数
        self.on_alert: Optional[Callable[[Alert], None]] = None
        self.on_intervention: Optional[Callable[[str, InterventionResult], None]] = None
        self.on_limit_reached: Optional[Callable[[str, LimitCheckResult], None]] = None

        # 状态
        self.active_agents: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {
            'total_checks': 0,
            'total_blocks': 0,
            'total_interventions': 0,
            'loops_detected': 0,
            'limits_reached': 0
        }

    def start(self, agent_id: str) -> None:
        """启动监控"""
        self.active_agents[agent_id] = time.time()
        self.logger.info(f"开始监控 Agent: {agent_id}")

    def stop(self, agent_id: str) -> None:
        """停止监控"""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        self.loop_detector.reset(agent_id)
        self.logger.info(f"停止监控 Agent: {agent_id}")

    def check(self, agent_id: str, tool_name: str,
              arguments: Dict[str, Any]) -> MonitorResult:
        """
        检查是否允许工具调用

        这是主入口方法，在每次工具调用前调用
        """
        self.metrics['total_checks'] += 1
        alerts = []

        # 1. 检查调用限制
        limit_result = self.tool_limits.check(agent_id, tool_name)

        if not limit_result.allowed:
            self.metrics['total_blocks'] += 1
            self.metrics['limits_reached'] += 1

            alert = self.tool_limits.get_alert(agent_id, tool_name, limit_result)
            if alert:
                alerts.append(alert)

            # 触发回调
            if self.on_limit_reached:
                self.on_limit_reached(agent_id, limit_result)

            # 达到硬性限制，触发干预
            if limit_result.should_stop:
                intervention = self.mentor_agent.advise(
                    agent_id,
                    alerts,
                    {'reason': 'hard_limit_reached'}
                )
                return MonitorResult(
                    allowed=False,
                    should_continue=intervention.should_continue,
                    alerts=alerts,
                    intervention=intervention
                )

            # 软限制，返回警告但允许执行
            return MonitorResult(
                allowed=True,
                should_continue=True,
                alerts=alerts,
                warnings=[limit_result.reason]
            )

        # 2. 检测循环
        loop_result = self.loop_detector.detect(agent_id)

        if loop_result and loop_result.is_loop:
            self.metrics['loops_detected'] += 1

            alert = self.loop_detector.get_alert(agent_id, loop_result)
            alerts.append(alert)

            # 触发回调
            if self.on_alert:
                self.on_alert(alert)

            # 触发干预
            if self.config.intervention.auto_intervention:
                intervention = self.mentor_agent.advise(agent_id, alerts)

                if self.on_intervention:
                    self.on_intervention(agent_id, intervention)

                return MonitorResult(
                    allowed=True,
                    should_continue=intervention.should_continue,
                    alerts=alerts,
                    intervention=intervention,
                    warnings=[intervention.message]
                )

        return MonitorResult(allowed=True, should_continue=True, alerts=alerts)

    def record(self, agent_id: str, tool_name: str,
               arguments: Dict[str, Any],
               result: Optional[Any] = None,
               error: Optional[str] = None,
               duration: float = 0.0) -> None:
        """记录工具调用"""
        tool_call = ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            error=error,
            duration=duration,
            agent_id=agent_id
        )

        # 记录到循环检测器
        self.loop_detector.record_call(agent_id, tool_call)

        # 记录到限制器
        self.tool_limits.record(agent_id, tool_name)

    def diagnose(self, agent_id: str) -> Dict[str, Any]:
        """诊断 Agent 状态"""
        alerts = []

        # 获取循环检测结果
        loop_result = self.loop_detector.detect(agent_id)
        if loop_result and loop_result.is_loop:
            alert = self.loop_detector.get_alert(agent_id, loop_result)
            alerts.append(alert)

        # 获取限制状态
        stats = self.tool_limits.get_stats(agent_id)
        if stats.get('agent', {}).get('percentage', 0) >= 0.8:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                issue_type=IssueType.TOOL_LIMIT_REACHED,
                message=f"Agent 接近限制: {stats['agent']['percentage']:.1%}",
                agent_id=agent_id
            ))

        return self.mentor_agent.diagnose(agent_id, alerts)

    def get_status(self, agent_id: str) -> Dict[str, Any]:
        """获取 Agent 监控状态"""
        return {
            'agent_id': agent_id,
            'is_active': agent_id in self.active_agents,
            'uptime': time.time() - self.active_agents.get(agent_id, 0),
            'loop_detector': self.loop_detector.get_stats(agent_id),
            'tool_limits': self.tool_limits.get_stats(agent_id),
            'intervention': self.mentor_agent.get_intervention_stats(agent_id),
            'alerts': self.diagnose(agent_id)
        }

    def get_metrics(self) -> Dict[str, Any]:
        """获取全局指标"""
        return {
            **self.metrics,
            'active_agents': len(self.active_agents),
            'loop_detector': {
                'total_calls_tracked': sum(
                    len(calls) for calls in self.loop_detector.call_history.values()
                )
            }
        }

    def reset(self, agent_id: Optional[str] = None) -> None:
        """重置状态"""
        if agent_id:
            self.loop_detector.reset(agent_id)
            self.tool_limits.reset(agent_id)
            self.stop(agent_id)
        else:
            # 重置所有
            self.loop_detector.call_history.clear()
            self.tool_limits.reset()
            self.active_agents.clear()
            self.metrics = {
                'total_checks': 0,
                'total_blocks': 0,
                'total_interventions': 0,
                'loops_detected': 0,
                'limits_reached': 0
            }

    def register_callbacks(self,
                          on_alert: Optional[Callable[[Alert], None]] = None,
                          on_intervention: Optional[Callable[[str, InterventionResult], None]] = None,
                          on_limit_reached: Optional[Callable[[str, LimitCheckResult], None]] = None) -> None:
        """注册回调函数"""
        self.on_alert = on_alert
        self.on_intervention = on_intervention
        self.on_limit_reached = on_limit_reached


# 便捷函数
def create_monitor(**config_kwargs) -> ExecutionMonitor:
    """创建监控器"""
    config = MonitorConfig(
        loop_detection=config_kwargs.get('loop_detection'),
        intervention=config_kwargs.get('intervention'),
        limits=config_kwargs.get('limits'),
        log_level=config_kwargs.get('log_level', 'INFO'),
        metrics_enabled=config_kwargs.get('metrics_enabled', True),
        alert_webhook=config_kwargs.get('alert_webhook'),
        persist_state=config_kwargs.get('persist_state', True),
        state_file=config_kwargs.get('state_file', '.cyberteam/monitor_state.json')
    )
    return ExecutionMonitor(config)
