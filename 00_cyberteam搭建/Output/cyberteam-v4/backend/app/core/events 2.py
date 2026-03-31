"""全局事件总线 - 抄 Magic 的事件驱动架构。

核心功能：
- 支持同步和异步事件处理器
- 事件类型注册与分发
- 错误隔离（单个处理器异常不影响其他处理器）

关键事件类型：
- task.created: 任务创建
- ceo.routed: CEO 路由完成
- coo.planned: COO 规划完成
- agent.started: Agent 开始执行
- agent.completed: Agent 执行完成
- agent.failed: Agent 执行失败
- debate.started: 辩论开始
- debate.converged: 辩论收敛
- approval.requested: 审批请求
- approval.approved: 审批通过
- approval.rejected: 审批拒绝
- budget.warning: 预算预警
- task.completed: 任务完成
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

log = logging.getLogger("cyberteam.events")


@dataclass
class Event:
    """事件对象。"""

    type: str
    data: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp,
            "source": self.source,
        }


class EventBus:
    """全局事件总线。

    用法:
        bus = EventBus()
        bus.on("task.created", handler)
        await bus.emit(Event(type="task.created", data={"task_id": "xxx"}))
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000

    def on(self, event_type: str, handler: Callable) -> None:
        """注册事件处理器。"""
        self._handlers.setdefault(event_type, []).append(handler)
        log.debug(f"Event handler registered: {event_type} -> {handler.__name__}")

    def off(self, event_type: str, handler: Callable) -> None:
        """移除事件处理器。"""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def emit(self, event: Event) -> None:
        """发射事件，通知所有注册的处理器。"""
        # 记录事件历史
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        handlers = self._handlers.get(event.type, [])
        if not handlers:
            log.debug(f"No handlers for event: {event.type}")
            return

        log.info(f"Event emitted: {event.type} (handlers: {len(handlers)})")

        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                log.error(f"Event handler error [{event.type} -> {handler.__name__}]: {e}")

    def get_history(self, event_type: Optional[str] = None, limit: int = 50) -> List[Event]:
        """获取事件历史记录。"""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]


# 全局单例
event_bus = EventBus()
