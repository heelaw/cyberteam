"""
sessions_send - 子Agent双向通信工具（主Agent调用）

参考 IMA 笔记：
- 同步等待子Agent回复
- 支持最多5轮"乒乓"对话
- 子Agent可返回错误信息，主Agent实时指导

使用场景：
- 主Agent发送任务给子Agent，等待子Agent执行结果
- 子Agent遇到问题时返回错误信息，主Agent可以实时指导
- 实现"乒乓协议"：发送→等待→回复→发送→...（最多5轮）

使用示例：
    # 主Agent调用
    params = SessionsSendParams(
        session_key="spawn:agent:123",
        message="请完成代码审查任务",
        timeout_seconds=30
    )
    result = sessions_send(params)
    # result.reply 包含子Agent的回复
"""

from __future__ import annotations

import time
import threading
import asyncio
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field

from .base import BaseTool, ToolResult

if TYPE_CHECKING:
    from .sessions_spawn import SpawnSession

# 最大对话轮次
MAX_ROUNDS = 5


# ============================================================================
# 参数和结果模型
# ============================================================================

class SessionsSendParams(BaseModel):
    """sessions_send 参数"""
    session_key: str = Field(
        ...,
        description="子会话密钥，格式: spawn:{agent_type}:{agent_id}，从 sessions_spawn 返回"
    )
    message: str = Field(
        ...,
        description="发送给子Agent的消息"
    )
    timeout_seconds: int = Field(
        default=30,
        description="等待回复超时秒数，默认30秒"
    )
    round_limit: Optional[int] = Field(
        default=MAX_ROUNDS,
        description="最大轮次限制，默认5轮"
    )


class SessionsSendResult(BaseModel):
    """sessions_send 返回"""
    session_key: str = Field(..., description="会话密钥")
    status: str = Field(
        ...,
        description="状态: ok=成功, timeout=超时, max_rounds=已达最大轮次, not_found=会话不存在, error=发送失败"
    )
    reply: Optional[str] = Field(
        default=None,
        description="子Agent的回复内容"
    )
    round: int = Field(
        default=0,
        description="当前轮次"
    )
    sent_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="发送时间"
    )
    reply_at: Optional[datetime] = Field(
        default=None,
        description="回复时间"
    )
    error: Optional[str] = Field(
        default=None,
        description="错误信息"
    )

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'session_key': self.session_key,
            'status': self.status,
            'reply': self.reply,
            'round': self.round,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'reply_at': self.reply_at.isoformat() if self.reply_at else None,
            'error': self.error
        }


# ============================================================================
# ConversationManager - 管理主Agent与子Agent的对话
# ============================================================================

class ConversationManager:
    """管理主Agent与子Agent的对话（乒乓球协议）

    单例模式，确保全局只有一个对话管理器。

    Attributes:
        _instance: 单例实例
        _reply_queues: session_key -> asyncio.Queue[reply]
        _rounds: session_key -> round_count
        _lock: 线程锁
    """

    _instance: Optional['ConversationManager'] = None

    def __init__(self):
        self._reply_queues: dict[str, asyncio.Queue] = {}
        self._rounds: dict[str, int] = {}
        self._lock = threading.RLock()
        self._sessions: dict[str, 'SpawnSession'] = {}  # session_key -> session info

    @classmethod
    def get_instance(cls) -> 'ConversationManager':
        """获取 ConversationManager 单例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        cls._instance = None

    def register_session(self, session_key: str, session_info: Optional[dict] = None) -> None:
        """注册一个新会话，开始对话

        Args:
            session_key: 会话密钥
            session_info: 会话信息（包含 agent_id, team_name 等）
        """
        with self._lock:
            if session_key not in self._reply_queues:
                self._reply_queues[session_key] = asyncio.Queue()
            if session_key not in self._rounds:
                self._rounds[session_key] = 0
            if session_info:
                self._sessions[session_key] = session_info

    def is_session_registered(self, session_key: str) -> bool:
        """检查会话是否已注册"""
        with self._lock:
            return session_key in self._reply_queues

    def get_round(self, session_key: str) -> int:
        """获取当前轮次"""
        with self._lock:
            return self._rounds.get(session_key, 0)

    def reset_rounds(self, session_key: str) -> None:
        """重置对话轮次（开始新一轮任务时）"""
        with self._lock:
            if session_key in self._rounds:
                self._rounds[session_key] = 0

    def send_and_wait(
        self,
        session_key: str,
        message: str,
        timeout_seconds: int = 30,
        round_limit: Optional[int] = None
    ) -> SessionsSendResult:
        """发送消息并同步等待回复（核心方法）

        实现乒乓球协议：
        1. 检查轮次限制
        2. 检查会话是否存在
        3. 发送消息到子Agent
        4. 等待子Agent回复（使用事件或轮询）
        5. 返回回复结果

        Args:
            session_key: 会话密钥
            message: 发送给子Agent的消息
            timeout_seconds: 等待回复的超时时间
            round_limit: 最大轮次限制

        Returns:
            SessionsSendResult: 包含发送状态和子Agent回复
        """
        limit = round_limit if round_limit is not None else MAX_ROUNDS
        current_round = self.get_round(session_key)

        # Step 1: 检查轮次限制
        if current_round >= limit:
            return SessionsSendResult(
                session_key=session_key,
                status="max_rounds",
                reply=None,
                round=current_round,
                sent_at=datetime.utcnow(),
                error=f"已达最大对话轮次 {limit}"
            )

        # Step 2: 检查会话是否存在
        session_info = self._sessions.get(session_key)
        if not session_info:
            # 尝试从 SpawnSessionManager 获取
            session_info = self._get_session_from_manager(session_key)
            if not session_info:
                return SessionsSendResult(
                    session_key=session_key,
                    status="not_found",
                    reply=None,
                    round=current_round,
                    sent_at=datetime.utcnow(),
                    error="会话不存在或已清理"
                )

        sent_at = datetime.utcnow()

        # Step 3: 发送消息到子Agent
        send_error = self._send_message_to_agent(session_key, message, session_info)
        if send_error:
            return SessionsSendResult(
                session_key=session_key,
                status="error",
                reply=None,
                round=current_round,
                sent_at=sent_at,
                error=send_error
            )

        # Step 4: 轮次+1
        with self._lock:
            self._rounds[session_key] = current_round + 1

        # Step 5: 等待子Agent回复
        reply, reply_at = self._wait_for_reply(session_key, timeout_seconds)

        if reply is None:
            return SessionsSendResult(
                session_key=session_key,
                status="timeout",
                reply=None,
                round=self._rounds.get(session_key, current_round),
                sent_at=sent_at,
                reply_at=None,
                error=f"等待回复超时（{timeout_seconds}秒）"
            )

        return SessionsSendResult(
            session_key=session_key,
            status="ok",
            reply=reply,
            round=self._rounds.get(session_key, current_round),
            sent_at=sent_at,
            reply_at=reply_at
        )

    def _get_session_from_manager(self, session_key: str) -> Optional[dict]:
        """从 SpawnSessionManager 获取会话信息"""
        try:
            # 延迟导入避免循环依赖
            from .sessions_spawn import SpawnSessionManager
            manager = SpawnSessionManager.get_instance()
            session = manager.get_session(session_key)
            if session:
                # 缓存会话信息
                self._sessions[session_key] = session
            return session
        except ImportError:
            return None
        except Exception:
            return None

    def _send_message_to_agent(
        self,
        session_key: str,
        message: str,
        session_info: dict
    ) -> Optional[str]:
        """发送消息到子Agent

        Args:
            session_key: 会话密钥
            message: 消息内容
            session_info: 会话信息

        Returns:
            错误信息，如果成功则返回 None
        """
        try:
            # 方式1: 尝试使用 MailboxManager
            from cyberteam.team.mailbox import MailboxManager
            mailbox = MailboxManager.get_instance()

            agent_name = session_info.get("agent_id", "")
            team_name = session_info.get("team_name", "default")

            mailbox.send(
                to_agent=agent_name,
                team=team_name,
                content=message,
                msg_type="message",
                session_key=session_key
            )
            return None

        except ImportError:
            pass
        except Exception as e:
            pass

        # 方式2: 尝试使用 tmux backend
        try:
            from cyberteam.spawn import get_backend
            backend = get_backend("tmux")
            backend.send_message(session_key, message)
            return None
        except ImportError:
            pass
        except Exception as e:
            pass

        # 方式3: 通过内部的 spawn 机制发送
        try:
            from .sessions_spawn import SpawnSessionManager
            manager = SpawnSessionManager.get_instance()
            # 尝试通过 manager 发送
            if hasattr(manager, 'send_message'):
                manager.send_message(session_key, message)
                return None
        except ImportError:
            pass
        except Exception as e:
            pass

        return f"无法发送消息：未找到可用的通信后端"

    def _wait_for_reply(self, session_key: str, timeout_seconds: int) -> tuple[Optional[str], Optional[datetime]]:
        """等待子Agent的回复

        实现方式：
        1. 先尝试从队列获取（事件驱动）
        2. 超过 timeout_seconds 则返回 None

        Args:
            session_key: 会话密钥
            timeout_seconds: 超时时间

        Returns:
            (reply, reply_at) 或 (None, None)
        """
        queue = self._reply_queues.get(session_key)
        if not queue:
            return None, None

        start = time.time()
        while time.time() - start < timeout_seconds:
            try:
                # 非阻塞获取
                reply = queue.get_nowait()
                return reply, datetime.utcnow()
            except asyncio.QueueEmpty:
                pass

            # 检查会话是否还存在
            if session_key not in self._reply_queues:
                break

            # 短暂休眠避免CPU空转
            time.sleep(0.1)

        return None, None

    def receive_reply(self, session_key: str, reply: str) -> None:
        """子Agent调用此方法提交回复（由 mailbox 或其他机制触发）

        Args:
            session_key: 会话密钥
            reply: 回复内容
        """
        queue = self._reply_queues.get(session_key)
        if queue:
            try:
                queue.put_nowait(reply)
            except Exception:
                pass

    def unregister_session(self, session_key: str) -> None:
        """注销会话，清理相关资源

        Args:
            session_key: 会话密钥
        """
        with self._lock:
            self._reply_queues.pop(session_key, None)
            self._rounds.pop(session_key, None)
            self._sessions.pop(session_key, None)


# ============================================================================
# 便捷函数
# ============================================================================

def sessions_send(params: SessionsSendParams) -> SessionsSendResult:
    """sessions_send 同步调用函数

    这是主Agent调用的主入口。

    Args:
        params: SessionsSendParams 参数

    Returns:
        SessionsSendResult: 包含子Agent回复
    """
    manager = ConversationManager.get_instance()

    # 确保会话已注册
    if not manager.is_session_registered(params.session_key):
        manager.register_session(params.session_key)

    return manager.send_and_wait(
        session_key=params.session_key,
        message=params.message,
        timeout_seconds=params.timeout_seconds,
        round_limit=params.round_limit
    )


# ============================================================================
# BaseTool 实现
# ============================================================================

class SessionsSendTool(BaseTool[SessionsSendParams]):
    """sessions_send 工具类

    用于工具注册系统（ToolRegistry/ToolFactory）
    """

    name = "sessions_send"
    description = """向子Agent发送消息并同步等待回复（乒乓球协议）

    核心功能：
    - 主Agent发送消息给子Agent，等待子Agent执行
    - 子Agent可返回错误信息（如"标签步骤卡住了"）
    - 主Agent根据回复实时指导子Agent，而非盲目重试
    - 最多5轮对话，超时可配置

    使用场景：
    - 主Agent给子Agent分配任务
    - 子Agent遇到问题需要主Agent指导
    - 需要实时交互的复杂任务分解

    参数：
    - session_key: 子会话密钥（从 sessions_spawn 返回）
    - message: 发送给子Agent的消息
    - timeout_seconds: 等待回复超时时间（默认30秒）
    - round_limit: 最大轮次限制（默认5轮）
    """
    params_class = SessionsSendParams

    async def execute(self, context: Any, params: SessionsSendParams) -> ToolResult:
        """执行 sessions_send

        Args:
            context: 执行上下文
            params: 验证后的参数

        Returns:
            ToolResult: 执行结果
        """
        import asyncio
        import concurrent.futures

        # 在线程池中执行同步的 sessions_send
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                sessions_send,
                params
            )

        return ToolResult(
            success=(result.status in ("ok", "timeout")),
            output=result.to_dict(),
            error=result.error
        )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    'SessionsSendParams',
    'SessionsSendResult',
    'SessionsSendTool',
    'ConversationManager',
    'sessions_send',
    'MAX_ROUNDS'
]