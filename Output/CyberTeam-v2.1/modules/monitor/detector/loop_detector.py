"""
Loop Detection - 循环检测器
===========================
基于 PentAGI Execution Monitoring 设计

功能:
- 序列匹配: 检测重复的工具调用序列
- 频率分析: 检测单个工具的过度使用
- 状态检测: 检测 Agent 状态停滞
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from ..config import LoopDetectionConfig
from ..utils import (
    ToolCall, Alert, AlertLevel, IssueType,
    calculate_sequence_similarity, find_repeated_pattern,
    analyze_tool_frequency, get_time_window_calls
)


@dataclass
class LoopDetectionResult:
    """循环检测结果"""
    is_loop: bool
    loop_type: str  # exact | fuzzy | frequency | stagnation
    confidence: float  # 0.0 - 1.0
    pattern: Optional[List[str]] = None
    repeated_count: int = 0
    message: str = ""


class LoopDetector:
    """
    循环检测器

    检测三种类型的循环:
    1. Exact Loop: 完全相同的工具调用序列重复
    2. Fuzzy Loop: 相似但不完全相同的调用模式
    3. Frequency Loop: 单个工具过度调用
    """

    def __init__(self, config: Optional[LoopDetectionConfig] = None):
        self.config = config or LoopDetectionConfig()
        self.logger = logging.getLogger(__name__)

        # 每个 Agent 的调用历史
        self.call_history: Dict[str, List[ToolCall]] = defaultdict(list)

        # 检测缓存
        self.last_check_time: Dict[str, float] = {}
        self.loop_count: Dict[str, int] = defaultdict(int)

    def record_call(self, agent_id: str, tool_call: ToolCall) -> None:
        """记录工具调用"""
        tool_call.agent_id = agent_id
        self.call_history[agent_id].append(tool_call)

        # 限制历史长度
        if len(self.call_history[agent_id]) > self.config.max_sequence_length:
            self.call_history[agent_id] = self.call_history[agent_id][-self.config.max_sequence_length:]

    def detect(self, agent_id: str) -> Optional[LoopDetectionResult]:
        """
        检测循环

        返回:
            LoopDetectionResult: 检测结果，无循环返回 None
        """
        calls = self.call_history.get(agent_id, [])

        if len(calls) < self.config.min_repeat_count:
            return None

        # 检查是否需要检测
        current_time = time.time()
        if agent_id in self.last_check_time:
            if current_time - self.last_check_time[agent_id] < self.config.check_interval:
                return None
        self.last_check_time[agent_id] = current_time

        # 1. 检测精确循环
        if self.config.exact_match_enabled:
            result = self._detect_exact_loop(calls)
            if result:
                self.loop_count[agent_id] += 1
                return result

        # 2. 检测模糊循环
        if self.config.fuzzy_match_enabled:
            result = self._detect_fuzzy_loop(calls)
            if result:
                self.loop_count[agent_id] += 1
                return result

        # 3. 检测频率异常
        result = self._detect_frequency_loop(calls)
        if result:
            self.loop_count[agent_id] += 1
            return result

        # 4. 检测状态停滞
        result = self._detect_stagnation(calls)
        if result:
            return result

        # 无循环，重置计数
        self.loop_count[agent_id] = 0
        return None

    def _detect_exact_loop(self, calls: List[ToolCall]) -> Optional[LoopDetectionResult]:
        """检测精确循环"""
        result = find_repeated_pattern(calls, min_length=2)
        if result:
            pattern, repeat_count = result
            return LoopDetectionResult(
                is_loop=True,
                loop_type="exact",
                confidence=0.95,
                pattern=pattern,
                repeated_count=repeat_count,
                message=f"检测到精确循环: {' -> '.join(pattern)} 重复 {repeat_count} 次"
            )
        return None

    def _detect_fuzzy_loop(self, calls: List[ToolCall]) -> Optional[LoopDetectionResult]:
        """检测模糊循环"""
        if len(calls) < self.config.window_size * 2:
            return None

        # 分割为两个窗口进行比较
        window = self.config.window_size
        seq1 = [c.to_signature() for c in calls[-window*2:-window]]
        seq2 = [c.to_signature() for c in calls[-window:]]

        similarity = calculate_sequence_similarity(seq1, seq2)

        if similarity >= self.config.similarity_threshold:
            return LoopDetectionResult(
                is_loop=True,
                loop_type="fuzzy",
                confidence=similarity,
                pattern=seq2,
                repeated_count=2,
                message=f"检测到模糊循环模式，相似度: {similarity:.2%}"
            )

        return None

    def _detect_frequency_loop(self, calls: List[ToolCall]) -> Optional[LoopDetectionResult]:
        """检测频率异常"""
        freq = analyze_tool_frequency(calls)
        total_calls = len(calls)

        for tool_name, count in freq.items():
            ratio = count / total_calls if total_calls > 0 else 0

            # 如果单个工具占比超过 60%
            if ratio > 0.6 and count >= self.config.min_repeat_count:
                return LoopDetectionResult(
                    is_loop=True,
                    loop_type="frequency",
                    confidence=ratio,
                    pattern=[tool_name],
                    repeated_count=count,
                    message=f"检测到频率异常: {tool_name} 被调用 {count} 次 ({ratio:.1%})"
                )

        return None

    def _detect_stagnation(self, calls: List[ToolCall]) -> Optional[LoopDetectionResult]:
        """检测状态停滞"""
        if len(calls) < 3:
            return None

        # 检查最近几次调用是否产生相同的结果
        recent = calls[-3:]
        if len(set(c.to_signature() for c in recent)) == 1:
            # 结果完全相同，可能陷入停滞
            return LoopDetectionResult(
                is_loop=True,
                loop_type="stagnation",
                confidence=0.7,
                pattern=[calls[-1].tool_name],
                repeated_count=3,
                message="检测到状态停滞: 连续调用返回相似结果"
            )

        return None

    def get_alert(self, agent_id: str, result: LoopDetectionResult) -> Alert:
        """生成告警"""
        calls = self.call_history.get(agent_id, [])[-10:]
        return Alert(
            level=AlertLevel.WARNING if result.loop_type != "stagnation" else AlertLevel.INFO,
            issue_type=IssueType.LOOP_DETECTED,
            message=result.message,
            agent_id=agent_id,
            tool_calls=calls,
            metadata={
                'loop_type': result.loop_type,
                'confidence': result.confidence,
                'pattern': result.pattern,
                'repeated_count': result.repeated_count,
                'loop_count': self.loop_count.get(agent_id, 0)
            }
        )

    def reset(self, agent_id: str) -> None:
        """重置检测状态"""
        if agent_id in self.call_history:
            self.call_history[agent_id] = []
        self.loop_count[agent_id] = 0
        self.last_check_time.pop(agent_id, None)

    def get_stats(self, agent_id: str) -> Dict:
        """获取统计信息"""
        calls = self.call_history.get(agent_id, [])
        return {
            'total_calls': len(calls),
            'loop_count': self.loop_count.get(agent_id, 0),
            'unique_tools': len(set(c.tool_name for c in calls)),
            'frequency': analyze_tool_frequency(calls)
        }
