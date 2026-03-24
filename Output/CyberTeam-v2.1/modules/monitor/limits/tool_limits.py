"""
Tool Call Limits - 工具调用限制
================================
基于 PentAGI Execution Monitoring 设计

功能:
- 全局限制: 限制总调用次数
- Agent 限制: 限制单个 Agent 调用次数
- 工具限制: 限制单个工具调用次数
- 速率限制: 限制单位时间内的调用频率
- 冷却机制: 达到限制后进入冷却期
"""

import logging
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
from threading import Lock

from ..config import ToolLimitsConfig
from ..utils import Alert, AlertLevel, IssueType


@dataclass
class LimitStatus:
    """限制状态"""
    current: int
    limit: int
    percentage: float
    is_limited: bool
    cooldown_remaining: float = 0.0


@dataclass
class LimitCheckResult:
    """限制检查结果"""
    allowed: bool
    reason: str = ""
    status: Optional[LimitStatus] = None
    should_stop: bool = False


class ToolLimits:
    """
    工具调用限制器

    实现多层限制机制:
    1. Global Limit: 全局总调用限制
    2. Per-Agent Limit: 每个 Agent 的限制
    3. Per-Tool Limit: 每个工具的限制
    4. Rate Limit: 速率限制
    """

    def __init__(self, config: Optional[ToolLimitsConfig] = None):
        self.config = config or ToolLimitsConfig()
        self.logger = logging.getLogger(__name__)

        # 全局计数器
        self.global_count: int = 0

        # 每个 Agent 的调用计数
        self.agent_counts: Dict[str, int] = defaultdict(int)

        # 每个工具的调用计数
        self.tool_counts: Dict[str, int] = defaultdict(int)

        # 速率限制队列 (时间戳)
        self.rate_limit_queue: deque = deque()

        # 突发限制队列
        self.burst_queue: deque = deque()

        # 冷却期跟踪
        self.cooldowns: Dict[str, float] = {}

        # 锁定
        self._lock = Lock()

    def check(self, agent_id: str, tool_name: str) -> LimitCheckResult:
        """
        检查是否允许调用

        返回:
            LimitCheckResult: 检查结果
        """
        if not self.config.enabled:
            return LimitCheckResult(allowed=True)

        with self._lock:
            current_time = time.time()

            # 1. 检查冷却期
            if agent_id in self.cooldowns:
                remaining = self.cooldowns[agent_id] - current_time
                if remaining > 0:
                    return LimitCheckResult(
                        allowed=False,
                        reason=f"Agent 冷却中，剩余 {remaining:.1f} 秒",
                        should_stop=True
                    )
                else:
                    del self.cooldowns[agent_id]

            # 2. 检查全局限制
            global_status = self._check_global_limit()
            if not global_status.is_limited:
                # 检查是否触发硬性停止
                if self.global_count >= self.config.hard_stop_threshold:
                    return LimitCheckResult(
                        allowed=False,
                        reason="已达到全局硬性停止限制",
                        status=global_status,
                        should_stop=True
                    )

            # 3. 检查 Agent 限制
            agent_status = self._check_agent_limit(agent_id)
            if agent_status.is_limited:
                return LimitCheckResult(
                    allowed=False,
                    reason=f"Agent {agent_id} 达到限制 ({agent_status.current}/{agent_status.limit})",
                    status=agent_status,
                    should_stop=agent_status.current >= self.config.hard_stop_threshold // 2
                )

            # 4. 检查工具限制
            tool_status = self._check_tool_limit(tool_name)
            if tool_status.is_limited:
                return LimitCheckResult(
                    allowed=False,
                    reason=f"工具 {tool_name} 达到限制 ({tool_status.current}/{tool_status.limit})",
                    status=tool_status,
                    should_stop=False
                )

            # 5. 检查速率限制
            rate_status = self._check_rate_limit()
            if rate_status.is_limited:
                return LimitCheckResult(
                    allowed=False,
                    reason="速率限制触发，请稍后重试",
                    status=rate_status,
                    should_stop=False
                )

            # 6. 检查突发限制
            burst_status = self._check_burst_limit()
            if burst_status.is_limited:
                return LimitCheckResult(
                    allowed=False,
                    reason="突发限制触发",
                    status=burst_status,
                    should_stop=False
                )

            # 所有检查通过
            return LimitCheckResult(allowed=True)

    def record(self, agent_id: str, tool_name: str) -> None:
        """记录调用"""
        if not self.config.enabled:
            return

        with self._lock:
            current_time = time.time()

            # 更新全局计数
            self.global_count += 1

            # 更新 Agent 计数
            self.agent_counts[agent_id] += 1

            # 更新工具计数
            self.tool_counts[tool_name] += 1

            # 更新速率限制队列
            self.rate_limit_queue.append(current_time)

            # 更新突发限制队列
            self.burst_queue.append(current_time)

            # 清理过期的速率限制记录
            self._cleanup_rate_limit_queue(current_time)

            # 清理过期的突发限制记录
            self._cleanup_burst_queue(current_time)

    def _check_global_limit(self) -> LimitStatus:
        """检查全局限制"""
        limit = self.config.global_max_calls
        current = self.global_count
        percentage = current / limit if limit > 0 else 0

        is_limited = current >= limit * self.config.warning_threshold

        return LimitStatus(
            current=current,
            limit=limit,
            percentage=percentage,
            is_limited=is_limited
        )

    def _check_agent_limit(self, agent_id: str) -> LimitStatus:
        """检查 Agent 限制"""
        limit = self.config.per_agent_max_calls
        current = self.agent_counts[agent_id]
        percentage = current / limit if limit > 0 else 0

        is_limited = current >= limit * self.config.warning_threshold

        # 检查冷却
        cooldown_remaining = self.cooldowns.get(agent_id, 0) - time.time()

        return LimitStatus(
            current=current,
            limit=limit,
            percentage=percentage,
            is_limited=is_limited,
            cooldown_remaining=max(0, cooldown_remaining)
        )

    def _check_tool_limit(self, tool_name: str) -> LimitStatus:
        """检查工具限制"""
        limit = self.config.per_tool_max_calls
        current = self.tool_counts[tool_name]
        percentage = current / limit if limit > 0 else 0

        is_limited = current >= limit * self.config.warning_threshold

        return LimitStatus(
            current=current,
            limit=limit,
            percentage=percentage,
            is_limited=is_limited
        )

    def _check_rate_limit(self) -> LimitStatus:
        """检查速率限制"""
        current_time = time.time()
        window_start = current_time - 60  # 1分钟窗口

        # 清理旧记录
        while self.rate_limit_queue and self.rate_limit_queue[0] < window_start:
            self.rate_limit_queue.popleft()

        current = len(self.rate_limit_queue)
        limit = self.config.per_minute_limit

        return LimitStatus(
            current=current,
            limit=limit,
            percentage=current / limit if limit > 0 else 0,
            is_limited=current >= limit
        )

    def _check_burst_limit(self) -> LimitStatus:
        """检查突发限制"""
        current_time = time.time()
        window_start = current_time - 5  # 5秒窗口

        # 清理旧记录
        while self.burst_queue and self.burst_queue[0] < window_start:
            self.burst_queue.popleft()

        current = len(self.burst_queue)
        limit = self.config.burst_limit

        return LimitStatus(
            current=current,
            limit=limit,
            percentage=current / limit if limit > 0 else 0,
            is_limited=current >= limit
        )

    def _cleanup_rate_limit_queue(self, current_time: float) -> None:
        """清理速率限制队列"""
        window_start = current_time - 60
        while self.rate_limit_queue and self.rate_limit_queue[0] < window_start:
            self.rate_limit_queue.popleft()

    def _cleanup_burst_queue(self, current_time: float) -> None:
        """清理突发限制队列"""
        window_start = current_time - 5
        while self.burst_queue and self.burst_queue[0] < window_start:
            self.burst_queue.popleft()

    def trigger_cooldown(self, agent_id: str) -> None:
        """触发冷却"""
        self.cooldowns[agent_id] = time.time() + self.config.cooldown_period
        self.logger.warning(f"Agent {agent_id} 进入冷却期 {self.config.cooldown_period} 秒")

    def get_alert(self, agent_id: str, tool_name: str,
                 result: LimitCheckResult) -> Optional[Alert]:
        """生成告警"""
        if result.allowed:
            return None

        return Alert(
            level=AlertLevel.ERROR if result.should_stop else AlertLevel.WARNING,
            issue_type=IssueType.TOOL_LIMIT_REACHED,
            message=result.reason,
            agent_id=agent_id,
            tool_calls=[],
            metadata={
                'tool_name': tool_name,
                'status': result.status.__dict__ if result.status else {},
                'should_stop': result.should_stop
            }
        )

    def reset(self, agent_id: Optional[str] = None) -> None:
        """重置计数"""
        with self._lock:
            if agent_id:
                self.agent_counts[agent_id] = 0
                self.cooldowns.pop(agent_id, None)
            else:
                self.global_count = 0
                self.agent_counts.clear()
                self.tool_counts.clear()
                self.cooldowns.clear()
                self.rate_limit_queue.clear()
                self.burst_queue.clear()

    def get_stats(self, agent_id: Optional[str] = None) -> Dict:
        """获取统计信息"""
        with self._lock:
            stats = {
                'global': {
                    'current': self.global_count,
                    'limit': self.config.global_max_calls,
                    'percentage': self.global_count / self.config.global_max_calls
                }
            }

            if agent_id:
                stats['agent'] = {
                    'current': self.agent_counts.get(agent_id, 0),
                    'limit': self.config.per_agent_max_calls,
                    'percentage': self.agent_counts.get(agent_id, 0) / self.config.per_agent_max_calls
                }
                cooldown_remaining = self.cooldowns.get(agent_id, 0) - time.time()
                stats['cooldown'] = max(0, cooldown_remaining)

            stats['tools'] = dict(self.tool_counts)

            return stats


