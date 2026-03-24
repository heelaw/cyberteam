"""
Token Budget Management - Token 预算管理
=========================================

提供 Token 预算管理功能，包括：
- 预算分配和追踪
- 溢出检测和处理
- 压缩调度策略
- 多级预算阈值

参考: PentAGI Chain Summarization
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


class BudgetPolicy(str, Enum):
    """预算策略"""
    FIFO = "fifo"              # 先进先出压缩
    LRU = "lru"               # 最近最少使用压缩
    PRIORITY = "priority"     # 优先级压缩
    ADAPTIVE = "adaptive"     # 自适应压缩
    CONSERVATIVE = "conservative"  # 保守压缩


class CompressionTrigger(str, Enum):
    """压缩触发条件"""
    MANUAL = "manual"           # 手动触发
    THRESHOLD_WARNING = "threshold_warning"   # 达到警告阈值
    THRESHOLD_CRITICAL = "threshold_critical"  # 达到临界阈值
    TOKEN_LIMIT = "token_limit"  # 达到Token限制
    IDLE_TIMEOUT = "idle_timeout"  # 空闲超时
    MESSAGE_COUNT = "message_count"  # 消息数量触发


@dataclass
class TokenBudget:
    """
    Token 预算

    Attributes:
        max_tokens: 最大Token数
        used_tokens: 已使用Token数
        reserved_tokens: 保留Token数 (用于系统消息等)
        warning_threshold: 警告阈值 (0-1)
        critical_threshold: 临界阈值 (0-1)
        compression_level: 当前压缩级别
    """
    max_tokens: int = 100000
    used_tokens: int = 0
    reserved_tokens: int = 5000
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    compression_level: str = "none"

    @property
    def available_tokens(self) -> int:
        """可用Token数"""
        return self.max_tokens - self.reserved_tokens - self.used_tokens

    @property
    def usage_ratio(self) -> float:
        """使用比率"""
        effective_max = self.max_tokens - self.reserved_tokens
        if effective_max <= 0:
            return 1.0
        return self.used_tokens / effective_max

    @property
    def is_warning(self) -> bool:
        """是否达到警告阈值"""
        return self.usage_ratio >= self.warning_threshold

    @property
    def is_critical(self) -> bool:
        """是否达到临界阈值"""
        return self.usage_ratio >= self.critical_threshold

    @property
    def should_compress(self) -> bool:
        """是否应该压缩"""
        return self.usage_ratio >= self.warning_threshold

    def allocate(self, tokens: int) -> bool:
        """
        分配Token

        Args:
            tokens: 要分配的Token数

        Returns:
            是否分配成功
        """
        if tokens > self.available_tokens:
            return False
        self.used_tokens += tokens
        return True

    def release(self, tokens: int) -> int:
        """
        释放Token

        Args:
            tokens: 要释放的Token数

        Returns:
            实际释放的Token数
        """
        released = min(tokens, self.used_tokens)
        self.used_tokens -= released
        return released

    def reset(self):
        """重置预算"""
        self.used_tokens = 0
        self.compression_level = "none"


@dataclass
class CompressionAction:
    """
    压缩动作记录

    Attributes:
        id: 唯一ID
        trigger: 触发原因
        policy: 使用的策略
        before_tokens: 压缩前Token数
        after_tokens: 压缩后Token数
        target_ids: 目标ID列表
        created_at: 创建时间
        duration_ms: 耗时(毫秒)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger: CompressionTrigger = CompressionTrigger.MANUAL
    policy: BudgetPolicy = BudgetPolicy.FIFO
    before_tokens: int = 0
    after_tokens: int = 0
    target_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0


class BudgetManager:
    """
    Token 预算管理器

    提供预算分配、追踪、压缩调度等功能。
    """

    def __init__(
        self,
        max_tokens: int = 100000,
        reserved_tokens: int = 5000,
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.95,
        default_policy: BudgetPolicy = BudgetPolicy.ADAPTIVE,
    ):
        """
        初始化预算管理器

        Args:
            max_tokens: 最大Token数
            reserved_tokens: 保留Token数
            warning_threshold: 警告阈值
            critical_threshold: 临界阈值
            default_policy: 默认压缩策略
        """
        self.budget = TokenBudget(
            max_tokens=max_tokens,
            reserved_tokens=reserved_tokens,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
        )

        self.default_policy = default_policy
        self.compression_history: list[CompressionAction] = []

        # 节点优先级 (node_id -> priority)
        self._priorities: dict[str, float] = {}
        # 节点访问时间 (node_id -> timestamp)
        self._last_access: dict[str, float] = {}
        # 节点Token数 (node_id -> tokens)
        self._node_tokens: dict[str, int] = {}

        # 回调函数
        self.on_warning: Optional[Callable[[], None]] = None
        self.on_critical: Optional[Callable[[], None]] = None
        self.on_compress: Optional[Callable[[CompressionAction], None]] = None

    def register_node(
        self,
        node_id: str,
        token_count: int,
        priority: float = 1.0,
    ):
        """
        注册节点到预算管理

        Args:
            node_id: 节点ID
            token_count: Token数
            priority: 优先级 (越高越重要)
        """
        self._node_tokens[node_id] = token_count
        self._priorities[node_id] = priority
        self._last_access[node_id] = time.time()

    def unregister_node(self, node_id: str) -> int:
        """
        注销节点

        Args:
            node_id: 节点ID

        Returns:
            释放的Token数
        """
        tokens = self._node_tokens.pop(node_id, 0)
        self._priorities.pop(node_id, None)
        self._last_access.pop(node_id, None)
        self.budget.release(tokens)
        return tokens

    def update_node_tokens(self, node_id: str, token_count: int):
        """更新节点Token数"""
        old_tokens = self._node_tokens.get(node_id, 0)
        diff = token_count - old_tokens

        if diff > 0:
            if not self.budget.allocate(diff):
                raise RuntimeError(f"Token预算不足: 需要 {diff}, 可用 {self.budget.available_tokens}")
        else:
            self.budget.release(-diff)

        self._node_tokens[node_id] = token_count

    def access_node(self, node_id: str):
        """记录节点访问"""
        self._last_access[node_id] = time.time()

    def get_compression_candidates(
        self,
        policy: Optional[BudgetPolicy] = None,
        target_tokens: Optional[int] = None,
    ) -> list[str]:
        """
        获取待压缩的候选节点

        Args:
            policy: 压缩策略 (None 使用默认)
            target_tokens: 目标Token数

        Returns:
            候选节点ID列表 (按优先级排序)
        """
        policy = policy or self.default_policy

        if policy == BudgetPolicy.FIFO:
            # 按访问时间排序 (最久未访问优先)
            return sorted(
                self._node_tokens.keys(),
                key=lambda x: self._last_access.get(x, 0)
            )

        elif policy == BudgetPolicy.LRU:
            # 按访问时间排序 (最近最少使用)
            return sorted(
                self._node_tokens.keys(),
                key=lambda x: self._last_access.get(x, time.time())
            )

        elif policy == BudgetPolicy.PRIORITY:
            # 按优先级排序 (低优先级优先)
            return sorted(
                self._node_tokens.keys(),
                key=lambda x: self._priorities.get(x, 1.0)
            )

        elif policy == BudgetPolicy.ADAPTIVE:
            # 自适应: 综合考虑优先级、访问时间和Token数
            candidates = []
            for node_id in self._node_tokens:
                priority = self._priorities.get(node_id, 1.0)
                last_access = self._last_access.get(node_id, time.time())
                tokens = self._node_tokens.get(node_id, 0)

                # 综合评分 (越低越应该压缩)
                score = (
                    (1 - priority) * 0.4 +  # 优先级权重
                    (time.time() - last_access) / 3600 * 0.3 +  # 时间权重
                    tokens / 10000 * 0.3  # Token数权重
                )
                candidates.append((node_id, score))

            return [x[0] for x in sorted(candidates, key=lambda x: x[1], reverse=True)]

        else:  # CONSERVATIVE
            # 保守: 只压缩最老的节点
            return sorted(
                self._node_tokens.keys(),
                key=lambda x: self._last_access.get(x, 0)
            )[:1] if self._node_tokens else []

    def calculate_compression_plan(
        self,
        target_tokens: Optional[int] = None,
    ) -> dict:
        """
        计算压缩计划

        Args:
            target_tokens: 目标Token数 (None 则自动计算)

        Returns:
            压缩计划
        """
        if target_tokens is None:
            # 自动计算: 压缩到警告阈值以下
            target_tokens = int(
                (self.budget.max_tokens - self.budget.reserved_tokens) *
                self.budget.warning_threshold
            )

        current = self.budget.used_tokens
        if current <= target_tokens:
            return {
                "needed": False,
                "target_tokens": target_tokens,
                "current_tokens": current,
                "candidates": [],
            }

        excess = current - target_tokens

        # 获取候选节点
        candidates = self.get_compression_candidates()

        # 计算需要压缩的节点
        plan = []
        accumulated = 0

        for node_id in candidates:
            tokens = self._node_tokens.get(node_id, 0)
            plan.append({
                "node_id": node_id,
                "tokens": tokens,
                "priority": self._priorities.get(node_id, 1.0),
            })
            accumulated += tokens

            if accumulated >= excess:
                break

        return {
            "needed": True,
            "target_tokens": target_tokens,
            "current_tokens": current,
            "excess_tokens": excess,
            "candidates": plan,
            "estimated_savings": accumulated,
        }

    def execute_compression(
        self,
        compressor: Callable[[list[str]], list[str]],
        policy: Optional[BudgetPolicy] = None,
    ) -> CompressionAction:
        """
        执行压缩

        Args:
            compressor: 压缩函数 (输入节点ID列表, 返回摘要列表)
            policy: 压缩策略

        Returns:
            压缩动作记录
        """
        before_tokens = self.budget.used_tokens

        # 确定触发原因
        trigger = CompressionTrigger.MANUAL
        if self.budget.is_critical:
            trigger = CompressionTrigger.THRESHOLD_CRITICAL
        elif self.budget.is_warning:
            trigger = CompressionTrigger.THRESHOLD_WARNING

        # 计算压缩计划
        plan = self.calculate_compression_plan()

        if not plan["needed"]:
            return CompressionAction(
                trigger=trigger,
                policy=policy or self.default_policy,
                before_tokens=before_tokens,
                after_tokens=before_tokens,
            )

        # 执行压缩
        target_ids = [c["node_id"] for c in plan["candidates"]]
        start_time = time.time()

        try:
            summaries = compressor(target_ids)

            # 更新Token计数
            for node_id, summary in zip(target_ids, summaries):
                new_tokens = len(summary) // 4 if summary else 10
                self.update_node_tokens(node_id, new_tokens)

        except Exception as e:
            # 压缩失败，记录但不更新
            pass

        duration = int((time.time() - start_time) * 1000)

        action = CompressionAction(
            trigger=trigger,
            policy=policy or self.default_policy,
            before_tokens=before_tokens,
            after_tokens=self.budget.used_tokens,
            target_ids=target_ids,
            duration_ms=duration,
        )

        self.compression_history.append(action)

        # 触发回调
        if self.on_compress:
            self.on_compress(action)

        # 根据状态触发回调
        if self.budget.is_critical and self.on_critical:
            self.on_critical()
        elif self.budget.is_warning and self.on_warning:
            self.on_warning()

        return action

    def check_and_trigger_compression(
        self,
        compressor: Callable[[list[str]], list[str]],
        auto_trigger: bool = True,
    ) -> Optional[CompressionAction]:
        """
        检查并触发压缩

        Args:
            compressor: 压缩函数
            auto_trigger: 是否自动触发

        Returns:
            压缩动作，如果不需要压缩则返回 None
        """
        if not auto_trigger:
            return None

        if self.budget.should_compress:
            return self.execute_compression(compressor)

        return None

    def get_status(self) -> dict:
        """获取预算状态"""
        return {
            "max_tokens": self.budget.max_tokens,
            "used_tokens": self.budget.used_tokens,
            "available_tokens": self.budget.available_tokens,
            "reserved_tokens": self.budget.reserved_tokens,
            "usage_ratio": self.budget.usage_ratio,
            "warning_threshold": self.budget.warning_threshold,
            "critical_threshold": self.budget.critical_threshold,
            "is_warning": self.budget.is_warning,
            "is_critical": self.budget.is_critical,
            "compression_level": self.budget.compression_level,
            "registered_nodes": len(self._node_tokens),
            "compression_history_count": len(self.compression_history),
        }

    def get_compression_stats(self) -> dict:
        """获取压缩统计"""
        if not self.compression_history:
            return {
                "total_compressions": 0,
                "total_tokens_saved": 0,
                "avg_duration_ms": 0,
                "trigger_distribution": {},
            }

        total_saved = sum(
            a.before_tokens - a.after_tokens
            for a in self.compression_history
        )

        triggers = {}
        for a in self.compression_history:
            triggers[a.trigger.value] = triggers.get(a.trigger.value, 0) + 1

        return {
            "total_compressions": len(self.compression_history),
            "total_tokens_saved": total_saved,
            "avg_duration_ms": sum(a.duration_ms for a in self.compression_history) // len(self.compression_history),
            "trigger_distribution": triggers,
            "last_compression": self.compression_history[-1].created_at.isoformat() if self.compression_history else None,
        }

    def adjust_thresholds(
        self,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None,
    ):
        """调整阈值"""
        if warning_threshold is not None:
            self.budget.warning_threshold = warning_threshold
        if critical_threshold is not None:
            self.budget.critical_threshold = critical_threshold

    def set_reserved_tokens(self, tokens: int):
        """设置保留Token数"""
        diff = tokens - self.budget.reserved_tokens
        if diff > 0:
            if not self.budget.allocate(diff):
                raise RuntimeError("保留Token数设置失败: 预算不足")
        else:
            self.budget.release(-diff)

        self.budget.reserved_tokens = tokens
