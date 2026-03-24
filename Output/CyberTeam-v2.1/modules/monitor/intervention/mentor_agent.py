"""
Mentor/Adviser Agent - 干预器
=============================
基于 PentAGI Execution Monitoring 设计

功能:
- 诊断问题: 分析循环和问题的根本原因
- 提供建议: 给出具体的解决方案建议
- 自动干预: 根据配置自动执行干预操作
- 升级处理: 必要时升级给人工处理
"""

import logging
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from ..config import InterventionConfig
from ..utils import ToolCall, Alert, AlertLevel, IssueType


class InterventionAction(Enum):
    """干预动作"""
    NONE = "none"
    WARN = "warn"
    RETRY = "retry"
    CONTEXT_REFRESH = "context_refresh"
    ALTERNATIVE = "alternative"
    ESCALATE = "escalate"
    STOP = "stop"


@dataclass
class MentorSuggestion:
    """建议"""
    action: InterventionAction
    message: str
    confidence: float = 1.0
    alternative_tools: List[str] = field(default_factory=list)
    context_refresh_prompt: str = ""
    retry_strategy: str = ""


@dataclass
class InterventionResult:
    """干预结果"""
    action: InterventionAction
    suggestions: List[MentorSuggestion]
    should_continue: bool
    message: str


class MentorAgent:
    """
    Mentor/Adviser Agent

    根据检测到的问题提供智能建议和干预
    """

    def __init__(self, config: Optional[InterventionConfig] = None):
        self.config = config or InterventionConfig()
        self.logger = logging.getLogger(__name__)

        # 干预历史
        self.intervention_history: Dict[str, List[Dict]] = {}

        # 回调函数
        self.callbacks: Dict[str, Callable] = {}

    def diagnose(self, agent_id: str, alerts: List[Alert]) -> Dict[str, Any]:
        """
        诊断问题

        返回诊断结果字典
        """
        if not alerts:
            return {'status': 'healthy', 'issues': []}

        issues = []
        for alert in alerts:
            issue = {
                'type': alert.issue_type.value,
                'level': alert.level.value,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'metadata': alert.metadata
            }
            issues.append(issue)

        # 诊断总结
        severity_counts = {}
        for alert in alerts:
            severity_counts[alert.level.value] = severity_counts.get(alert.level.value, 0) + 1

        return {
            'status': 'unhealthy' if alerts else 'healthy',
            'issues': issues,
            'severity_summary': severity_counts,
            'recommendation': self._generate_recommendation(issues)
        }

    def _generate_recommendation(self, issues: List[Dict]) -> str:
        """生成推荐建议"""
        if not issues:
            return "继续执行"

        issue_types = [i['type'] for i in issues]

        if IssueType.LOOP_DETECTED.value in issue_types:
            return "检测到循环，建议刷新上下文或更换方法"
        elif IssueType.TOOL_LIMIT_REACHED.value in issue_types:
            return "工具调用达到限制，建议等待或升级"
        elif IssueType.AGENT_STUCK.value in issue_types:
            return "Agent 卡住，建议重新初始化"
        else:
            return "需要人工检查"

    def advise(self, agent_id: str, alerts: List[Alert],
               agent_context: Optional[Dict] = None) -> InterventionResult:
        """
        提供建议

        基于诊断结果给出具体的干预建议
        """
        suggestions = []

        for alert in alerts:
            suggestion = self._generate_suggestion(alert, agent_context or {})
            suggestions.append(suggestion)

        # 根据模式选择最终动作
        action = self._decide_action(suggestions)

        # 记录干预
        self._record_intervention(agent_id, alerts, action)

        message = self._format_message(action, suggestions)

        return InterventionResult(
            action=action,
            suggestions=suggestions,
            should_continue=action not in [InterventionAction.STOP, InterventionAction.ESCALATE],
            message=message
        )

    def _generate_suggestion(self, alert: Alert, context: Dict) -> MentorSuggestion:
        """生成单个建议"""
        if alert.issue_type == IssueType.LOOP_DETECTED:
            return self._handle_loop_detected(alert, context)
        elif alert.issue_type == IssueType.TOOL_LIMIT_REACHED:
            return self._handle_limit_reached(alert, context)
        elif alert.issue_type == IssueType.AGENT_STUCK:
            return self._handle_agent_stuck(alert, context)
        else:
            return MentorSuggestion(
                action=InterventionAction.WARN,
                message=f"检测到未知问题: {alert.message}"
            )

    def _handle_loop_detected(self, alert: Alert, context: Dict) -> MentorSuggestion:
        """处理循环检测"""
        loop_type = alert.metadata.get('loop_type', 'unknown')
        loop_count = alert.metadata.get('loop_count', 0)

        if loop_count >= self.config.max_retries:
            return MentorSuggestion(
                action=InterventionAction.ESCALATE,
                message=f"循环已重复 {loop_count} 次，建议升级处理",
                confidence=0.9
            )

        # 根据循环类型给出建议
        if loop_type == "exact":
            return MentorSuggestion(
                action=InterventionAction.CONTEXT_REFRESH,
                message="检测到精确循环，建议刷新上下文",
                context_refresh_prompt="你似乎陷入了重复的模式，请重新思考问题，尝试不同的方法。",
                confidence=0.8
            )
        elif loop_type == "fuzzy":
            return MentorSuggestion(
                action=InterventionAction.ALTERNATIVE,
                message="检测到模糊循环模式，建议更换方法",
                alternative_tools=self._get_alternative_tools(alert),
                confidence=0.7
            )
        elif loop_type == "frequency":
            return MentorSuggestion(
                action=InterventionAction.ALTERNATIVE,
                message=f"工具 {alert.metadata.get('pattern', [])} 使用过于频繁，建议使用替代方案",
                alternative_tools=self._get_alternative_tools(alert),
                confidence=0.8
            )
        else:
            return MentorSuggestion(
                action=InterventionAction.WARN,
                message="检测到循环，建议重试",
                retry_strategy="使用新的参数重新尝试"
            )

    def _handle_limit_reached(self, alert: Alert, context: Dict) -> MentorSuggestion:
        """处理限制达到"""
        return MentorSuggestion(
            action=InterventionAction.STOP,
            message="工具调用达到硬性限制，必须停止",
            confidence=1.0
        )

    def _handle_agent_stuck(self, alert: Alert, context: Dict) -> MentorSuggestion:
        """处理 Agent 卡住"""
        return MentorSuggestion(
            action=InterventionAction.CONTEXT_REFRESH,
            message="Agent 似乎卡住了，建议重新初始化",
            context_refresh_prompt="请重新审视任务目标，采用新的策略。",
            confidence=0.6
        )

    def _get_alternative_tools(self, alert: Alert) -> List[str]:
        """获取替代工具建议"""
        # 基于当前使用的工具，返回可能的替代工具
        tool_mapping = {
            'read': ['glob', 'grep', 'search'],
            'glob': ['read', 'grep'],
            'grep': ['read', 'glob'],
            'bash': ['write', 'edit'],
            'write': ['bash', 'edit'],
            'edit': ['write', 'bash']
        }

        pattern = alert.metadata.get('pattern', [])
        if pattern and pattern[0] in tool_mapping:
            return tool_mapping[pattern[0]]

        return []

    def _decide_action(self, suggestions: List[MentorSuggestion]) -> InterventionAction:
        """决定最终动作"""
        if self.config.mentor_mode == "passive":
            return InterventionAction.NONE
        elif self.config.mentor_mode == "aggressive":
            #  aggressive 模式更容易采取行动
            for s in suggestions:
                if s.action in [InterventionAction.STOP, InterventionAction.ESCALATE]:
                    return s.action
            return suggestions[0].action if suggestions else InterventionAction.WARN
        else:  # adviser
            # 默认 adviser 模式
            for s in suggestions:
                if s.confidence >= 0.8:
                    return s.action
            return suggestions[0].action if suggestions else InterventionAction.NONE

    def _format_message(self, action: InterventionAction,
                       suggestions: List[MentorSuggestion]) -> str:
        """格式化消息"""
        if not suggestions:
            return "执行正常"

        main_suggestion = suggestions[0]

        messages = {
            InterventionAction.NONE: "继续执行",
            InterventionAction.WARN: f"警告: {main_suggestion.message}",
            InterventionAction.RETRY: f"重试: {main_suggestion.retry_strategy or main_suggestion.message}",
            InterventionAction.CONTEXT_REFRESH: f"上下文刷新: {main_suggestion.message}",
            InterventionAction.ALTERNATIVE: f"更换方法: {main_suggestion.message}",
            InterventionAction.ESCALATE: f"升级: {main_suggestion.message}",
            InterventionAction.STOP: f"停止: {main_suggestion.message}"
        }

        return messages.get(action, main_suggestion.message)

    def _record_intervention(self, agent_id: str, alerts: List[Alert],
                            action: InterventionAction) -> None:
        """记录干预历史"""
        if agent_id not in self.intervention_history:
            self.intervention_history[agent_id] = []

        self.intervention_history[agent_id].append({
            'timestamp': time.time(),
            'alerts': [a.to_dict() for a in alerts],
            'action': action.value
        })

        # 限制历史长度
        if len(self.intervention_history[agent_id]) > 100:
            self.intervention_history[agent_id] = self.intervention_history[agent_id][-100:]

    def register_callback(self, action: InterventionAction,
                         callback: Callable[[str, Alert], Any]) -> None:
        """注册回调函数"""
        self.callbacks[action.value] = callback

    def execute_callback(self, action: InterventionAction,
                        agent_id: str, alert: Alert) -> Any:
        """执行回调"""
        callback = self.callbacks.get(action.value)
        if callback:
            return callback(agent_id, alert)
        return None

    def get_intervention_stats(self, agent_id: str) -> Dict:
        """获取干预统计"""
        history = self.intervention_history.get(agent_id, [])
        action_counts = {}

        for entry in history:
            action = entry['action']
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            'total_interventions': len(history),
            'action_counts': action_counts,
            'last_intervention': history[-1] if history else None
        }
