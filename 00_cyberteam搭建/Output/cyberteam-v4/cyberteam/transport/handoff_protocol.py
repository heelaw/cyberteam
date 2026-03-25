"""
Handoff Protocol - 交接协议模块

负责Agent之间的任务交接，确保交接过程的可靠性和可追溯性。
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import uuid
import json


class HandoffStatus(Enum):
    """交接状态"""
    PENDING = "pending"           # 待处理
    INITIATED = "initiated"       # 已发起
    ACKNOWLEDGED = "acknowledged" # 已确认
    IN_PROGRESS = "in_progress"   # 进行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"      # 已取消


@dataclass
class HandoffContext:
    """交接上下文"""
    handoff_id: str
    from_agent: str
    to_agent: str
    task: dict
    status: HandoffStatus = HandoffStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "handoff_id": self.handoff_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "task": self.task,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "metadata": self.metadata,
            "history": self.history
        }

    def _add_history(self, action: str, details: str = "") -> None:
        """添加历史记录"""
        self.history.append({
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })


class HandoffProtocol:
    """
    任务交接协议

    管理Agent之间的任务交接生命周期：
    1. 发起交接 (initiate)
    2. 确认交接 (acknowledge)
    3. 完成交接 (complete)

    支持：
    - 交接确认机制
    - 超时处理
    - 交接历史追踪
    - 失败重试
    """

    def __init__(self, default_timeout: float = 300.0):
        """
        初始化交接协议

        Args:
            default_timeout: 默认超时时间（秒）
        """
        self._handovers: Dict[str, HandoffContext] = {}
        self._lock = threading.RLock()
        self._default_timeout = default_timeout
        self._callbacks: Dict[str, List[callable]] = {}  # 状态变更回调

    def initiate(self, from_agent: str, to_agent: str, task: dict,
                 metadata: Optional[dict] = None) -> str:
        """
        发起任务交接

        Args:
            from_agent: 交出方Agent
            to_agent: 接收方Agent
            task: 任务内容
            metadata: 元数据

        Returns:
            交接ID
        """
        with self._lock:
            handoff_id = str(uuid.uuid4())

            context = HandoffContext(
                handoff_id=handoff_id,
                from_agent=from_agent,
                to_agent=to_agent,
                task=task,
                status=HandoffStatus.INITIATED,
                metadata=metadata or {}
            )
            context._add_history("initiated", f"{from_agent} -> {to_agent}")

            self._handovers[handoff_id] = context
            self._notify_callbacks(handoff_id, HandoffStatus.INITIATED)

            return handoff_id

    def acknowledge(self, handoff_id: str) -> bool:
        """
        确认交接

        Args:
            handoff_id: 交接ID

        Returns:
            是否成功确认
        """
        with self._lock:
            if handoff_id not in self._handovers:
                return False

            context = self._handovers[handoff_id]

            if context.status != HandoffStatus.INITIATED:
                return False

            context.status = HandoffStatus.ACKNOWLEDGED
            context.acknowledged_at = datetime.now()
            context._add_history("acknowledged", f"by {context.to_agent}")

            self._notify_callbacks(handoff_id, HandoffStatus.ACKNOWLEDGED)

            return True

    def start_progress(self, handoff_id: str) -> bool:
        """
        开始处理交接任务

        Args:
            handoff_id: 交接ID

        Returns:
            是否成功开始
        """
        with self._lock:
            if handoff_id not in self._handovers:
                return False

            context = self._handovers[handoff_id]

            if context.status != HandoffStatus.ACKNOWLEDGED:
                return False

            context.status = HandoffStatus.IN_PROGRESS
            context._add_history("started", f"{context.to_agent} started processing")

            self._notify_callbacks(handoff_id, HandoffStatus.IN_PROGRESS)

            return True

    def complete(self, handoff_id: str, result: dict) -> bool:
        """
        完成交接

        Args:
            handoff_id: 交接ID
            result: 任务结果

        Returns:
            是否成功完成
        """
        with self._lock:
            if handoff_id not in self._handovers:
                return False

            context = self._handovers[handoff_id]

            if context.status not in [HandoffStatus.INITIATED, HandoffStatus.ACKNOWLEDGED, HandoffStatus.IN_PROGRESS]:
                return False

            context.status = HandoffStatus.COMPLETED
            context.completed_at = datetime.now()
            context.result = result
            context._add_history("completed", f"result: {str(result)[:100]}")

            self._notify_callbacks(handoff_id, HandoffStatus.COMPLETED)

            return True

    def fail(self, handoff_id: str, error: str) -> bool:
        """
        标记交接失败

        Args:
            handoff_id: 交接ID
            error: 错误信息

        Returns:
            是否成功标记
        """
        with self._lock:
            if handoff_id not in self._handovers:
                return False

            context = self._handovers[handoff_id]
            context.status = HandoffStatus.FAILED
            context._add_history("failed", error)
            context.metadata["error"] = error

            self._notify_callbacks(handoff_id, HandoffStatus.FAILED)

            return True

    def cancel(self, handoff_id: str) -> bool:
        """
        取消交接

        Args:
            handoff_id: 交接ID

        Returns:
            是否成功取消
        """
        with self._lock:
            if handoff_id not in self._handovers:
                return False

            context = self._handovers[handoff_id]

            if context.status in [HandoffStatus.COMPLETED, HandoffStatus.FAILED]:
                return False

            context.status = HandoffStatus.CANCELLED
            context._add_history("cancelled", "handoff was cancelled")

            self._notify_callbacks(handoff_id, HandoffStatus.CANCELLED)

            return True

    def get_status(self, handoff_id: str) -> Optional[HandoffStatus]:
        """
        获取交接状态

        Args:
            handoff_id: 交接ID

        Returns:
            交接状态，若不存在则返回None
        """
        with self._lock:
            context = self._handovers.get(handoff_id)
            return context.status if context else None

    def get_context(self, handoff_id: str) -> Optional[dict]:
        """
        获取完整的交接上下文

        Args:
            handoff_id: 交接ID

        Returns:
            交接上下文字典
        """
        with self._lock:
            context = self._handovers.get(handoff_id)
            return context.to_dict() if context else None

    def get_pending_for_agent(self, agent_id: str) -> List[dict]:
        """
        获取Agent待处理的交接列表

        Args:
            agent_id: Agent ID

        Returns:
            待处理交接列表
        """
        with self._lock:
            return [
                ctx.to_dict()
                for ctx in self._handovers.values()
                if ctx.to_agent == agent_id and ctx.status in [
                    HandoffStatus.INITIATED,
                    HandoffStatus.ACKNOWLEDGED,
                    HandoffStatus.IN_PROGRESS
                ]
            ]

    def get_history_for_agent(self, agent_id: str, limit: int = 50) -> List[dict]:
        """
        获取Agent的交接历史

        Args:
            agent_id: Agent ID
            limit: 返回条数限制

        Returns:
            交接历史列表
        """
        with self._lock:
            results = [
                ctx.to_dict()
                for ctx in self._handovers.values()
                if ctx.from_agent == agent_id or ctx.to_agent == agent_id
            ]
            # 按时间倒序
            results.sort(key=lambda x: x["created_at"], reverse=True)
            return results[:limit]

    def register_callback(self, event: str, callback: callable) -> None:
        """
        注册状态变更回调

        Args:
            event: 事件类型（状态名称或 "all"）
            callback: 回调函数
        """
        with self._lock:
            if event not in self._callbacks:
                self._callbacks[event] = []
            self._callbacks[event].append(callback)

    def _notify_callbacks(self, handoff_id: str, status: HandoffStatus) -> None:
        """通知所有注册的回调"""
        callbacks_to_call = []

        with self._lock:
            if "all" in self._callbacks:
                callbacks_to_call.extend(self._callbacks["all"])
            if status.value in self._callbacks:
                callbacks_to_call.extend(self._callbacks[status.value])

        context = self._handovers.get(handoff_id)
        for callback in callbacks_to_call:
            try:
                callback(handoff_id, status, context.to_dict() if context else None)
            except Exception:
                pass

    def cleanup_completed(self, older_than_seconds: float = 3600) -> int:
        """
        清理已完成的交接记录

        Args:
            older_than_seconds: 只清理早于该秒数的记录

        Returns:
            清理的记录数
        """
        with self._lock:
            now = datetime.now()
            to_remove = []

            for handoff_id, context in self._handovers.items():
                if context.status in [HandoffStatus.COMPLETED, HandoffStatus.FAILED, HandoffStatus.CANCELLED]:
                    age = (now - context.completed_at).total_seconds() if context.completed_at else 0
                    if age > older_than_seconds:
                        to_remove.append(handoff_id)

            for handoff_id in to_remove:
                del self._handovers[handoff_id]

            return len(to_remove)

    def get_statistics(self) -> dict:
        """
        获取交接统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            total = len(self._handovers)
            by_status = {}

            for ctx in self._handovers.values():
                status_name = ctx.status.value
                by_status[status_name] = by_status.get(status_name, 0) + 1

            return {
                "total_handovers": total,
                "by_status": by_status,
                "active": sum(1 for ctx in self._handovers.values()
                              if ctx.status in [HandoffStatus.INITIATED, HandoffStatus.ACKNOWLEDGED, HandoffStatus.IN_PROGRESS])
            }