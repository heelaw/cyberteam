"""
Transport Layer - 传输层主模块

整合消息路由、收件箱管理和交接协议，提供统一的通信接口。
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any, Callable
import threading
import logging

from cyberteam.transport.base import Transport
from cyberteam.transport.message_router import MessageRouter, RouteStrategy, RouteRule
from cyberteam.transport.inbox_manager import InboxManager, Message
from cyberteam.transport.handoff_protocol import HandoffProtocol, HandoffStatus

logger = logging.getLogger(__name__)


class TransportLayer:
    """
    Transport层主类

    整合三大核心模块：
    - MessageRouter: 消息路由
    - InboxManager: 收件箱管理
    - HandoffProtocol: 交接协议

    提供统一的通信接口给上层Agent系统调用。
    """

    def __init__(self, backend_transport: Optional[Transport] = None):
        """
        初始化Transport层

        Args:
            backend_transport: 底层传输后端（可选），用于跨进程/跨机器通信
        """
        self._router = MessageRouter()
        self._inbox = InboxManager()
        self._handoff = HandoffProtocol()
        self._backend = backend_transport
        self._running = False
        self._lock = threading.RLock()
        self._started = False

    def start(self) -> None:
        """启动Transport层"""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._started = True
            logger.info("TransportLayer started")

    def stop(self) -> None:
        """停止Transport层"""
        with self._lock:
            if not self._running:
                return
            self._running = False
            if self._backend:
                self._backend.close()
            logger.info("TransportLayer stopped")

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    # ==================== 消息发送接口 ====================

    def send_message(self, to: str, msg: dict) -> str:
        """
        发送消息到指定Agent

        Args:
            to: 目标Agent ID
            msg: 消息字典，需包含 'from' 字段

        Returns:
            消息ID
        """
        if not self._running:
            raise RuntimeError("TransportLayer is not started")

        # 如果有后端传输，先路由
        if self._backend:
            path = self._router.route(msg)
            # 消息会通过路由送达
            logger.debug(f"Routing message from {msg.get('from')} to {to} via {path}")

        # 存入收件箱
        message_id = self._inbox.send(to, msg)
        logger.debug(f"Message {message_id} sent to {to}")
        return message_id

    def receive_message(self, agent_id: str) -> Optional[dict]:
        """
        接收消息（阻塞式）

        Args:
            agent_id: Agent ID

        Returns:
            消息字典，若无消息则返回None
        """
        if not self._running:
            raise RuntimeError("TransportLayer is not started")

        return self._inbox.receive(agent_id)

    def peek_message(self, agent_id: str) -> Optional[dict]:
        """
        查看消息（不删除）

        Args:
            agent_id: Agent ID

        Returns:
            消息字典，若无消息则返回None
        """
        return self._inbox.peek(agent_id)

    def peek_all_messages(self, agent_id: str) -> List[dict]:
        """
        查看所有未消费消息

        Args:
            agent_id: Agent ID

        Returns:
            消息字典列表
        """
        return self._inbox.peek_all(agent_id)

    def message_count(self, agent_id: str) -> int:
        """
        获取未读消息数量

        Args:
            agent_id: Agent ID

        Returns:
            消息数量
        """
        return self._inbox.count(agent_id)

    # ==================== 路由接口 ====================

    def register_agent(self, agent_id: str, reachable_agents: Optional[List[str]] = None) -> None:
        """
        注册Agent到通信网络

        Args:
            agent_id: Agent ID
            reachable_agents: 该Agent可直接通信的其他Agent列表
        """
        self._router.register_agent(agent_id, reachable_agents)

    def add_route_rule(self, from_agent: str, to_agent: str,
                       strategy: RouteStrategy = RouteStrategy.DIRECT,
                       via_agents: Optional[List[str]] = None) -> None:
        """
        添加路由规则

        Args:
            from_agent: 源Agent
            to_agent: 目标Agent
            strategy: 路由策略
            via_agents: 链式路由经过的Agent列表
        """
        rule = RouteRule(
            from_agent=from_agent,
            to_agent=to_agent,
            strategy=strategy,
            via_agents=via_agents or []
        )
        self._router.add_route_rule(rule)

    def get_route_path(self, from_agent: str, to_agent: str) -> List[str]:
        """
        获取两个Agent之间的路由路径

        Args:
            from_agent: 源Agent
            to_agent: 目标Agent

        Returns:
            路由路径列表
        """
        return self._router.get_path(from_agent, to_agent)

    # ==================== 交接协议接口 ====================

    def initiate_handoff(self, from_agent: str, to_agent: str,
                          task: dict, metadata: Optional[dict] = None) -> str:
        """
        发起任务交接

        Args:
            from_agent: 交出方
            to_agent: 接收方
            task: 任务内容
            metadata: 元数据

        Returns:
            交接ID
        """
        return self._handoff.initiate(from_agent, to_agent, task, metadata)

    def acknowledge_handoff(self, handoff_id: str) -> bool:
        """
        确认交接

        Args:
            handoff_id: 交接ID

        Returns:
            是否成功
        """
        return self._handoff.acknowledge(handoff_id)

    def complete_handoff(self, handoff_id: str, result: dict) -> bool:
        """
        完成交接

        Args:
            handoff_id: 交接ID
            result: 任务结果

        Returns:
            是否成功
        """
        return self._handoff.complete(handoff_id, result)

    def get_handoff_status(self, handoff_id: str) -> Optional[HandoffStatus]:
        """
        获取交接状态

        Args:
            handoff_id: 交接ID

        Returns:
            交接状态
        """
        return self._handoff.get_status(handoff_id)

    def get_pending_handoffs(self, agent_id: str) -> List[dict]:
        """
        获取Agent待处理的交接

        Args:
            agent_id: Agent ID

        Returns:
            待处理交接列表
        """
        return self._handoff.get_pending_for_agent(agent_id)

    # ==================== 订阅接口 ====================

    def subscribe_messages(self, agent_id: str, callback: Callable[[dict], None]) -> None:
        """
        订阅消息通知

        Args:
            agent_id: Agent ID
            callback: 回调函数
        """
        self._inbox.subscribe(agent_id, callback)

    def register_handoff_callback(self, event: str, callback: Callable) -> None:
        """
        注册交接状态变更回调

        Args:
            event: 事件类型
            callback: 回调函数
        """
        self._handoff.register_callback(event, callback)

    # ==================== 统计和管理接口 ====================

    def get_inbox_stats(self, agent_id: str) -> dict:
        """
        获取收件箱统计

        Args:
            agent_id: Agent ID

        Returns:
            统计信息
        """
        return self._inbox.get_inbox_stats(agent_id)

    def get_handoff_statistics(self) -> dict:
        """
        获取交接统计

        Returns:
            统计信息
        """
        return self._handoff.get_statistics()

    def broadcast(self, from_agent: str, content: Any, agent_ids: List[str],
                  metadata: Optional[dict] = None) -> List[str]:
        """
        广播消息

        Args:
            from_agent: 发送者
            content: 消息内容
            agent_ids: 接收者列表
            metadata: 元数据

        Returns:
            发送成功的消息ID列表
        """
        return self._inbox.broadcast(from_agent, content, agent_ids, metadata)

    def clear_inbox(self, agent_id: str) -> int:
        """
        清空收件箱

        Args:
            agent_id: Agent ID

        Returns:
            清除的消息数量
        """
        return self._inbox.clear(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        """
        从通信网络中移除Agent

        Args:
            agent_id: Agent ID
        """
        self._router.remove_agent(agent_id)

    # ==================== 组件访问接口 ====================

    @property
    def router(self) -> MessageRouter:
        """获取路由器实例"""
        return self._router

    @property
    def inbox_manager(self) -> InboxManager:
        """获取收件箱管理器实例"""
        return self._inbox

    @property
    def handoff_protocol(self) -> HandoffProtocol:
        """获取交接协议实例"""
        return self._handoff


# 向后兼容：保留Transport别名
Transport = TransportLayer