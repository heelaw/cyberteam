"""
Inbox Manager - 收件箱管理模块

负责消息的存储、检索和管理，支持多Agent独立收件箱。
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import threading
import uuid
import json


@dataclass
class Message:
    """消息结构"""
    id: str
    from_agent: str
    to_agent: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # 优先级：0=普通, 1=高, 2=紧急
    consumed: bool = False

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "priority": self.priority,
            "consumed": self.consumed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """从字典创建"""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class Inbox:
    """单个Agent的收件箱"""

    def __init__(self, agent_id: str, max_size: int = 1000):
        self.agent_id = agent_id
        self._messages: deque = deque(maxlen=max_size)
        self._lock = threading.RLock()

    def add(self, message: Message) -> None:
        """添加消息到收件箱"""
        with self._lock:
            self._messages.append(message)

    def receive(self) -> Optional[Message]:
        """取出并移除第一条消息"""
        with self._lock:
            for i, msg in enumerate(self._messages):
                if not msg.consumed:
                    msg.consumed = True
                    return msg
            return None

    def peek(self) -> Optional[Message]:
        """查看第一条消息（不移除）"""
        with self._lock:
            for msg in self._messages:
                if not msg.consumed:
                    return msg
            return None

    def peek_all(self) -> List[Message]:
        """查看所有未消费消息"""
        with self._lock:
            return [msg for msg in self._messages if not msg.consumed]

    def count(self) -> int:
        """统计未消费消息数量"""
        with self._lock:
            return sum(1 for msg in self._messages if not msg.consumed)

    def clear(self) -> int:
        """清空所有消息，返回清除数量"""
        with self._lock:
            count = len(self._messages)
            self._messages.clear()
            return count

    def get_by_priority(self, min_priority: int = 0) -> List[Message]:
        """按优先级获取消息"""
        with self._lock:
            return [msg for msg in self._messages
                    if not msg.consumed and msg.priority >= min_priority]


class InboxManager:
    """
    收件箱管理器

    负责管理所有Agent的收件箱，支持：
    - 发送消息到指定Agent
    - 接收来自指定Agent的消息
    - 查看（不删除）消息
    - 消息计数
    """

    def __init__(self, default_max_size: int = 1000):
        self._inboxes: Dict[str, Inbox] = {}
        self._default_max_size = default_max_size
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[callable]] = {}  # 消息订阅回调

    def _get_or_create_inbox(self, agent_id: str) -> Inbox:
        """获取或创建收件箱"""
        with self._lock:
            if agent_id not in self._inboxes:
                self._inboxes[agent_id] = Inbox(agent_id, self._default_max_size)
            return self._inboxes[agent_id]

    def send(self, to: str, message: dict) -> str:
        """
        发送消息到指定Agent的收件箱

        Args:
            to: 目标Agent ID
            message: 消息字典，需包含 'from' 字段

        Returns:
            消息ID
        """
        inbox = self._get_or_create_inbox(to)

        msg = Message(
            id=str(uuid.uuid4()),
            from_agent=message.get("from", "unknown"),
            to_agent=to,
            content=message.get("content", message),
            metadata=message.get("metadata", {}),
            priority=message.get("priority", 0)
        )

        inbox.add(msg)

        # 触发订阅回调
        self._notify_subscribers(to, msg)

        return msg.id

    def receive(self, agent_id: str) -> Optional[dict]:
        """
        从收件箱接收消息（会移除消息）

        Args:
            agent_id: Agent ID

        Returns:
            消息字典，若无消息则返回None
        """
        inbox = self._get_or_create_inbox(agent_id)
        msg = inbox.receive()
        return msg.to_dict() if msg else None

    def peek(self, agent_id: str) -> Optional[dict]:
        """
        查看消息（不移除）

        Args:
            agent_id: Agent ID

        Returns:
            消息字典，若无消息则返回None
        """
        inbox = self._get_or_create_inbox(agent_id)
        msg = inbox.peek()
        return msg.to_dict() if msg else None

    def peek_all(self, agent_id: str) -> List[dict]:
        """
        查看所有未消费消息

        Args:
            agent_id: Agent ID

        Returns:
            消息字典列表
        """
        inbox = self._get_or_create_inbox(agent_id)
        return [msg.to_dict() for msg in inbox.peek_all()]

    def count(self, agent_id: str) -> int:
        """
        获取未消费消息数量

        Args:
            agent_id: Agent ID

        Returns:
            消息数量
        """
        inbox = self._get_or_create_inbox(agent_id)
        return inbox.count()

    def subscribe(self, agent_id: str, callback: callable) -> None:
        """
        订阅消息通知

        Args:
            agent_id: Agent ID
            callback: 回调函数，接收消息字典
        """
        with self._lock:
            if agent_id not in self._subscribers:
                self._subscribers[agent_id] = []
            self._subscribers[agent_id].append(callback)

    def _notify_subscribers(self, agent_id: str, message: Message) -> None:
        """通知订阅者有新消息"""
        with self._lock:
            callbacks = self._subscribers.get(agent_id, [])
        for callback in callbacks:
            try:
                callback(message.to_dict())
            except Exception:
                pass  # 回调异常不影响主流程

    def clear(self, agent_id: str) -> int:
        """
        清空收件箱

        Args:
            agent_id: Agent ID

        Returns:
            清除的消息数量
        """
        inbox = self._get_or_create_inbox(agent_id)
        return inbox.clear()

    def get_inbox_stats(self, agent_id: str) -> dict:
        """
        获取收件箱统计信息

        Args:
            agent_id: Agent ID

        Returns:
            统计信息字典
        """
        inbox = self._get_or_create_inbox(agent_id)
        all_messages = list(inbox._messages)

        return {
            "agent_id": agent_id,
            "total_messages": len(all_messages),
            "unconsumed": inbox.count(),
            "consumed": sum(1 for m in all_messages if m.consumed),
            "by_priority": {
                "urgent": sum(1 for m in all_messages if m.priority >= 2),
                "high": sum(1 for m in all_messages if m.priority >= 1),
                "normal": sum(1 for m in all_messages if m.priority == 0)
            }
        }

    def list_all_inboxes(self) -> List[str]:
        """列出所有有收件箱的Agent"""
        with self._lock:
            return list(self._inboxes.keys())

    def broadcast(self, from_agent: str, content: Any, agent_ids: List[str],
                   metadata: Optional[dict] = None) -> List[str]:
        """
        广播消息到多个Agent

        Args:
            from_agent: 发送者
            content: 消息内容
            agent_ids: 接收者列表
            metadata: 元数据

        Returns:
            发送成功的消息ID列表
        """
        message = {
            "from": from_agent,
            "content": content,
            "metadata": metadata or {}
        }

        message_ids = []
        for agent_id in agent_ids:
            try:
                msg_id = self.send(agent_id, message)
                message_ids.append(msg_id)
            except Exception:
                pass

        return message_ids