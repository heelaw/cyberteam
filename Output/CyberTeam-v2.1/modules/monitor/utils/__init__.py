"""
Utils Module - 工具函数
"""

import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueType(Enum):
    """问题类型"""
    LOOP_DETECTED = "loop_detected"
    TOOL_LIMIT_REACHED = "tool_limit_reached"
    AGENT_STUCK = "agent_stuck"
    CONTEXT_OVERFLOW = "context_overflow"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    agent_id: str = ""

    def to_signature(self) -> str:
        """生成工具调用签名"""
        args_str = str(sorted(self.arguments.items()))
        return hashlib.md5(f"{self.tool_name}:{args_str}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'tool_name': self.tool_name,
            'arguments': self.arguments,
            'result': str(self.result)[:100] if self.result else None,
            'error': self.error,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'agent_id': self.agent_id,
            'signature': self.to_signature()
        }


@dataclass
class Alert:
    """告警"""
    level: AlertLevel
    issue_type: IssueType
    message: str
    agent_id: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            'level': self.level.value,
            'issue_type': self.issue_type.value,
            'message': self.message,
            'agent_id': self.agent_id,
            'tool_calls': [tc.to_dict() for tc in self.tool_calls],
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


def calculate_sequence_similarity(seq1: List[str], seq2: List[str]) -> float:
    """
    计算两个序列的相似度
    使用最长公共子序列(LCS)比率
    """
    if not seq1 or not seq2:
        return 0.0

    # 简化的相似度计算
    set1, set2 = set(seq1), set(seq2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)

    if union == 0:
        return 0.0

    return intersection / union


def find_repeated_pattern(calls: List[ToolCall], min_length: int = 2) -> Optional[Tuple[List[str], int]]:
    """
    查找重复模式
    返回: (模式列表, 重复次数)
    """
    if len(calls) < min_length * 2:
        return None

    signatures = [c.to_signature() for c in calls]

    # 检查精确重复
    for pattern_len in range(min_length, len(signatures) // 2 + 1):
        for i in range(len(signatures) - pattern_len * 2 + 1):
            pattern = signatures[i:i + pattern_len]
            repeat_count = 1

            # 计算模式重复次数
            j = i + pattern_len
            while j + pattern_len <= len(signatures):
                if signatures[j:j + pattern_len] == pattern:
                    repeat_count += 1
                    j += pattern_len
                else:
                    break

            if repeat_count >= 2:
                return (pattern, repeat_count)

    return None


def analyze_tool_frequency(calls: List[ToolCall]) -> Dict[str, int]:
    """分析工具调用频率"""
    freq = {}
    for call in calls:
        freq[call.tool_name] = freq.get(call.tool_name, 0) + 1
    return freq


def get_time_window_calls(calls: List[ToolCall], window_seconds: float) -> List[ToolCall]:
    """获取时间窗口内的调用"""
    if not calls:
        return []
    current_time = time.time()
    return [c for c in calls if current_time - c.timestamp <= window_seconds]
