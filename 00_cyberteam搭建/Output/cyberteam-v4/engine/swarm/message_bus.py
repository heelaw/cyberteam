"""
MessageBus - 消息总线

提供发布-订阅模式的消息传递机制
"""

from typing import Dict, List, Callable, Any, Set
from collections import defaultdict
import threading
import uuid
from datetime import datetime


class MessageBus:
    """消息总线，提供Topic-based发布订阅"""

    def __init__(self):
        # topic -> list of (subscriber_id, callback)
        self._subscriptions: dict[str, list[tuple]] = defaultdict(list)
        # 消息历史
        self._history: dict[str, list[dict]] = defaultdict(list)
        # 锁保证线程安全
        self._lock = threading.Lock()
        # 最大历史消息数
        self._max_history = 1000

    def publish(self, topic: str, msg: dict) -> str:
        """
        发布消息到Topic

        Args:
            topic: 主题名称
            msg: 消息内容字典

        Returns:
            message_id: 消息ID
        """
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        enriched_msg = {
            "id": message_id,
            "topic": topic,
            "data": msg,
            "timestamp": timestamp,
        }

        with self._lock:
            # 存储历史
            self._history[topic].append(enriched_msg)
            # 修剪历史
            if len(self._history[topic]) > self._max_history:
                self._history[topic] = self._history[topic][-self._max_history:]

            # 通知订阅者
            for subscriber_id, callback in self._subscriptions[topic]:
                try:
                    callback(enriched_msg)
                except Exception as e:
                    # 订阅回调错误不影响发布
                    pass

        return message_id

    def subscribe(self, topic: str, callback: Callable[[dict], None]) -> str:
        """
        订阅Topic

        Args:
            topic: 主题名称
            callback: 回调函数，接收消息字典

        Returns:
            subscription_id: 订阅ID
        """
        subscription_id = f"sub_{uuid.uuid4().hex[:8]}"

        with self._lock:
            self._subscriptions[topic].append((subscription_id, callback))

        return subscription_id

    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """
        取消订阅

        Args:
            topic: 主题名称
            subscription_id: 订阅ID

        Returns:
            是否成功取消
        """
        with self._lock:
            subscriptions = self._subscriptions[topic]
            for i, (sub_id, _) in enumerate(subscriptions):
                if sub_id == subscription_id:
                    del subscriptions[i]
                    return True
        return False

    def get_history(self, topic: str, limit: int = 100) -> list[dict]:
        """
        获取主题的历史消息

        Args:
            topic: 主题名称
            limit: 返回数量限制

        Returns:
            消息列表
        """
        with self._lock:
            history = self._history.get(topic, [])
            return history[-limit:]

    def list_topics(self) -> list[str]:
        """列出所有有订阅或历史的主题"""
        with self._lock:
            topics = set(self._subscriptions.keys()) | set(self._history.keys())
            return sorted(list(topics))

    def clear_topic(self, topic: str) -> None:
        """清空主题的历史消息"""
        with self._lock:
            if topic in self._history:
                self._history[topic] = []

    def subscriber_count(self, topic: str) -> int:
        """获取主题的订阅者数量"""
        with self._lock:
            return len(self._subscriptions.get(topic, []))