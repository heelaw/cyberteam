"""
sessions_receive - 子Agent获取主Agent消息并提交回复

这是子Agent调用的工具，不是主Agent调用。

功能：
- 子Agent获取主Agent发来的消息
- 子Agent提交执行结果或错误信息给主Agent
- 支持"乒乓协议"：主Agent发送→子Agent接收→子Agent回复→...

使用场景：
- 子Agent调用此工具检查是否有来自主Agent的新消息
- 子Agent完成任务后调用此工具提交回复
- 子Agent遇到问题时调用此工具返回错误信息

使用示例：
    # 子Agent调用
    params = SessionsReceiveParams(
        session_key="spawn:agent:123",
        timeout_seconds=30
    )
    result = sessions_receive(params)

    if result.has_message:
        message = result.message
        # 处理主Agent的消息
        # ...

        # 完成后提交回复
        sessions_reply(params.session_key, "任务已完成")
"""

from __future__ import annotations

import time
import threading
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .base import BaseTool, ToolResult

# 导入 ConversationManager
try:
    from .sessions_send import ConversationManager
except ImportError:
    ConversationManager = None


# ============================================================================
# 参数和结果模型
# ============================================================================

class SessionsReceiveParams(BaseModel):
    """sessions_receive 参数"""
    session_key: str = Field(
        ...,
        description="子会话密钥，格式: spawn:{agent_type}:{agent_id}"
    )
    timeout_seconds: int = Field(
        default=30,
        description="等待消息的超时时间，默认30秒"
    )


class SessionsReceiveResult(BaseModel):
    """sessions_receive 返回"""
    session_key: str = Field(..., description="会话密钥")
    has_message: bool = Field(
        ...,
        description="是否有来自主Agent的消息"
    )
    message: Optional[str] = Field(
        default=None,
        description="主Agent发送的消息内容"
    )
    reply_required: bool = Field(
        default=False,
        description="主Agent是否等待回复（乒乓协议）"
    )
    received_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="消息接收时间"
    )
    error: Optional[str] = Field(
        default=None,
        description="错误信息"
    )

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'session_key': self.session_key,
            'has_message': self.has_message,
            'message': self.message,
            'reply_required': self.reply_required,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'error': self.error
        }


class SessionsReplyParams(BaseModel):
    """sessions_reply 参数（子Agent提交回复）"""
    session_key: str = Field(
        ...,
        description="子会话密钥"
    )
    reply: str = Field(
        ...,
        description="回复内容（任务结果或错误信息）"
    )
    success: bool = Field(
        default=True,
        description="是否成功完成任务"
    )


class SessionsReplyResult(BaseModel):
    """sessions_reply 返回"""
    session_key: str = Field(..., description="会话密钥")
    status: str = Field(
        ...,
        description="提交状态: ok=成功, error=失败"
    )
    submitted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="提交时间"
    )
    error: Optional[str] = Field(
        default=None,
        description="错误信息"
    )

    def to_dict(self) -> dict:
        return {
            'session_key': self.session_key,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'error': self.error
        }


# ============================================================================
# 消息队列（子Agent专用）
# ============================================================================

class SubAgentMessageQueue:
    """子Agent消息队列（内存存储）

    由于子Agent运行在独立的进程中或线程中，
    这里使用内存存储来模拟消息队列。

    Attributes:
        _instance: 单例实例
        _inbox: agent_id -> list[message]
        _waiting_for_reply: session_key -> bool（主Agent是否在等待回复）
        _lock: 线程锁
    """

    _instance: Optional['SubAgentMessageQueue'] = None

    def __init__(self):
        self._inbox: dict[str, list[dict]] = {}  # agent_id -> [{message, reply_required, timestamp}, ...]
        self._waiting_for_reply: dict[str, bool] = {}  # session_key -> bool
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> 'SubAgentMessageQueue':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def push_message(
        self,
        session_key: str,
        agent_id: str,
        message: str,
        reply_required: bool = True
    ) -> None:
        """主Agent发送消息到子Agent的收件箱

        Args:
            session_key: 会话密钥
            agent_id: 子Agent ID
            message: 消息内容
            reply_required: 主Agent是否等待回复
        """
        with self._lock:
            if agent_id not in self._inbox:
                self._inbox[agent_id] = []

            self._inbox[agent_id].append({
                'session_key': session_key,
                'message': message,
                'reply_required': reply_required,
                'timestamp': datetime.utcnow()
            })

            # 标记主Agent正在等待回复
            if reply_required:
                self._waiting_for_reply[session_key] = True

    def pop_message(self, agent_id: str) -> Optional[dict]:
        """子Agent获取消息（FIFO）

        Args:
            agent_id: 子Agent ID

        Returns:
            消息字典，或 None（队列为空）
        """
        with self._lock:
            if agent_id not in self._inbox or not self._inbox[agent_id]:
                return None

            return self._inbox[agent_id].pop(0)

    def peek_message(self, agent_id: str) -> Optional[dict]:
        """子Agent查看下一条消息（不取出）

        Args:
            agent_id: 子Agent ID

        Returns:
            消息字典，或 None
        """
        with self._lock:
            if agent_id not in self._inbox or not self._inbox[agent_id]:
                return None

            return self._inbox[agent_id][0]

    def is_empty(self, agent_id: str) -> bool:
        """检查收件箱是否为空"""
        with self._lock:
            return agent_id not in self._inbox or len(self._inbox[agent_id]) == 0

    def clear(self, agent_id: str) -> None:
        """清空指定Agent的收件箱"""
        with self._lock:
            if agent_id in self._inbox:
                self._inbox[agent_id] = []

    def is_waiting_for_reply(self, session_key: str) -> bool:
        """检查主Agent是否正在等待此session的回复"""
        with self._lock:
            return self._waiting_for_reply.get(session_key, False)

    def clear_waiting(self, session_key: str) -> None:
        """清除等待标记"""
        with self._lock:
            self._waiting_for_reply.pop(session_key, None)


# ============================================================================
# 便捷函数
# ============================================================================

def sessions_receive(params: SessionsReceiveParams) -> SessionsReceiveResult:
    """子Agent获取主Agent发来的消息

    这是子Agent的主入口。

    Args:
        params: SessionsReceiveParams 参数

    Returns:
        SessionsReceiveResult: 包含消息内容
    """
    # 从 session_key 提取 agent_id
    # 格式: spawn:{agent_type}:{agent_id}
    agent_id = _extract_agent_id(params.session_key)
    if not agent_id:
        return SessionsReceiveResult(
            session_key=params.session_key,
            has_message=False,
            error="无效的 session_key 格式"
        )

    queue = SubAgentMessageQueue.get_instance()

    # 带超时的轮询
    start = time.time()
    while time.time() - start < params.timeout_seconds:
        msg = queue.pop_message(agent_id)
        if msg:
            return SessionsReceiveResult(
                session_key=msg['session_key'],
                has_message=True,
                message=msg['message'],
                reply_required=msg['reply_required'],
                received_at=msg['timestamp']
            )

        # 检查是否需要等待
        if queue.is_waiting_for_reply(params.session_key):
            # 主Agent在等待，不能长时间阻塞
            break

        time.sleep(0.1)

    return SessionsReceiveResult(
        session_key=params.session_key,
        has_message=False,
        reply_required=False
    )


def sessions_reply(params: SessionsReplyParams) -> SessionsReplyResult:
    """子Agent提交回复给主Agent

    Args:
        params: SessionsReplyParams 参数

    Returns:
        SessionsReplyResult: 提交状态
    """
    if ConversationManager is not None:
        manager = ConversationManager.get_instance()
        manager.receive_reply(params.session_key, params.reply)

    # 清除等待标记
    queue = SubAgentMessageQueue.get_instance()
    queue.clear_waiting(params.session_key)

    return SessionsReplyResult(
        session_key=params.session_key,
        status="ok"
    )


def _extract_agent_id(session_key: str) -> Optional[str]:
    """从 session_key 提取 agent_id

    格式: spawn:{agent_type}:{agent_id}

    Args:
        session_key: 会话密钥

    Returns:
        agent_id，或 None
    """
    parts = session_key.split(':')
    if len(parts) >= 3:
        return parts[-1]
    return None


# ============================================================================
# BaseTool 实现
# ============================================================================

class SessionsReceiveTool(BaseTool[SessionsReceiveParams]):
    """sessions_receive 工具类（子Agent用）"""

    name = "sessions_receive"
    description = """子Agent获取主Agent发来的消息

    这是子Agent调用的工具，用于：
    - 检查是否有来自主Agent的新消息
    - 获取任务指令
    - 确认主Agent是否在等待回复

    参数：
    - session_key: 子会话密钥
    - timeout_seconds: 等待消息的超时时间（默认30秒）
    """
    params_class = SessionsReceiveParams

    async def execute(self, context: Any, params: SessionsReceiveParams) -> ToolResult:
        """执行 sessions_receive"""
        result = sessions_receive(params)
        return ToolResult(
            success=True,  # 即使没有消息也算成功
            output=result.to_dict()
        )


class SessionsReplyTool(BaseTool[SessionsReplyParams]):
    """sessions_reply 工具类（子Agent用）"""

    name = "sessions_reply"
    description = """子Agent提交回复给主Agent

    这是子Agent调用的工具，用于：
    - 提交任务执行结果
    - 报告错误信息（如"标签步骤卡住了"）
    - 发送进度更新

    参数：
    - session_key: 子会话密钥
    - reply: 回复内容
    - success: 是否成功完成任务（默认True）
    """
    params_class = SessionsReplyParams

    async def execute(self, context: Any, params: SessionsReplyParams) -> ToolResult:
        """执行 sessions_reply"""
        result = sessions_reply(params)
        return ToolResult(
            success=(result.status == "ok"),
            output=result.to_dict(),
            error=result.error
        )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    'SessionsReceiveParams',
    'SessionsReceiveResult',
    'SessionsReceiveTool',
    'SessionsReplyParams',
    'SessionsReplyResult',
    'SessionsReplyTool',
    'SubAgentMessageQueue',
    'sessions_receive',
    'sessions_reply',
    '_extract_agent_id'
]