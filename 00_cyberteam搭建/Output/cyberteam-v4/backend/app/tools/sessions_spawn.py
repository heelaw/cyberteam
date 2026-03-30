"""
sessions_spawn - 子Agent生命周期管理

功能：
- 创建子Agent会话（spawn）
- 管理子Agent会话状态
- 提供会话信息查询

使用场景：
- 主Agent通过 sessions_spawn 创建子Agent
- 子Agent通过 session_key 与主Agent通信
- 主Agent通过 sessions_send 给子Agent发送指令

session_key 格式：
    spawn:{agent_type}:{agent_id}

示例：
    spawn:code_review:agent_001
    spawn:data_analysis:agent_002
"""

from __future__ import annotations

import time
import threading
import uuid
from typing import Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseTool, ToolResult


# ============================================================================
# 会话状态枚举
# ============================================================================

class SessionStatus(str, Enum):
    """会话状态"""
    PENDING = "pending"      # 创建但未启动
    RUNNING = "running"      # 运行中
    WAITING = "waiting"      # 等待主Agent指令
    COMPLETED = "completed"  # 任务完成
    FAILED = "failed"       # 执行失败
    CANCELLED = "cancelled"  # 已取消


# ============================================================================
# 数据模型
# ============================================================================

class SpawnSession(BaseModel):
    """子Agent会话信息"""
    session_key: str = Field(..., description="会话密钥")
    agent_type: str = Field(..., description="Agent类型，如 code_review, data_analysis")
    agent_id: str = Field(..., description="Agent唯一标识")
    team_name: str = Field(default="default", description="所属团队名称")
    status: SessionStatus = Field(default=SessionStatus.PENDING, description="会话状态")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="启动时间")
    finished_at: Optional[datetime] = Field(default=None, description="结束时间")
    context: dict[str, Any] = Field(default_factory=dict, description="额外上下文")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class SpawnParams(BaseModel):
    """sessions_spawn 参数"""
    agent_type: str = Field(
        ...,
        description="Agent类型，如 code_review, data_analysis, user_research"
    )
    team_name: str = Field(
        default="default",
        description="所属团队名称"
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="传递给子Agent的上下文信息"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="额外元数据"
    )


class SpawnResult(BaseModel):
    """sessions_spawn 返回"""
    session_key: str = Field(..., description="会话密钥，用于后续通信")
    agent_type: str = Field(..., description="Agent类型")
    agent_id: str = Field(..., description="Agent唯一标识")
    status: str = Field(..., description="会话状态")
    created_at: datetime = Field(..., description="创建时间")
    message: str = Field(default="", description="提示信息")

    def to_dict(self) -> dict:
        return {
            'session_key': self.session_key,
            'agent_type': self.agent_type,
            'agent_id': self.agent_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'message': self.message
        }


class ListSessionsParams(BaseModel):
    """list_sessions 参数"""
    team_name: Optional[str] = Field(
        default=None,
        description="过滤条件：团队名称"
    )
    status: Optional[SessionStatus] = Field(
        default=None,
        description="过滤条件：会话状态"
    )


class ListSessionsResult(BaseModel):
    """list_sessions 返回"""
    sessions: list[dict] = Field(default_factory=list, description="会话列表")
    total: int = Field(default=0, description="总会话数")


class GetSessionParams(BaseModel):
    """get_session 参数"""
    session_key: str = Field(..., description="会话密钥")


class GetSessionResult(BaseModel):
    """get_session 返回"""
    session_key: str = Field(..., description="会话密钥")
    found: bool = Field(..., description="会话是否存在")
    session: Optional[dict] = Field(default=None, description="会话详情")


class UpdateSessionParams(BaseModel):
    """update_session 参数"""
    session_key: str = Field(..., description="会话密钥")
    status: Optional[SessionStatus] = Field(default=None, description="新状态")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="更新的元数据")


class UpdateSessionResult(BaseModel):
    """update_session 返回"""
    session_key: str = Field(..., description="会话密钥")
    status: str = Field(..., description="操作状态")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


# ============================================================================
# SpawnSessionManager - 会话管理器
# ============================================================================

class SpawnSessionManager:
    """子Agent会话管理器

    单例模式，管理所有子Agent会话的生命周期。

    功能：
    - 创建会话（spawn）
    - 查询会话
    - 更新会话状态
    - 清理过期会话
    """

    _instance: Optional['SpawnSessionManager'] = None

    def __init__(self):
        self._sessions: dict[str, SpawnSession] = {}  # session_key -> SpawnSession
        self._agent_index: dict[str, str] = {}  # agent_id -> session_key
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> 'SpawnSessionManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def create_session(self, params: SpawnParams) -> SpawnResult:
        """创建新的子Agent会话

        Args:
            params: SpawnParams 参数

        Returns:
            SpawnResult: 包含 session_key 等信息
        """
        agent_id = f"{params.agent_type}_{uuid.uuid4().hex[:8]}"

        # 构建 session_key: spawn:{agent_type}:{agent_id}
        session_key = f"spawn:{params.agent_type}:{agent_id}"

        session = SpawnSession(
            session_key=session_key,
            agent_type=params.agent_type,
            agent_id=agent_id,
            team_name=params.team_name,
            status=SessionStatus.PENDING,
            context=params.context,
            metadata=params.metadata
        )

        with self._lock:
            self._sessions[session_key] = session
            self._agent_index[agent_id] = session_key

        # 注册到 ConversationManager（如果可用）
        try:
            from .sessions_send import ConversationManager
            manager = ConversationManager.get_instance()
            manager.register_session(session_key, {
                'agent_id': agent_id,
                'team_name': params.team_name,
                'agent_type': params.agent_type
            })
        except ImportError:
            pass

        return SpawnResult(
            session_key=session_key,
            agent_type=params.agent_type,
            agent_id=agent_id,
            status=session.status.value,
            created_at=session.created_at,
            message=f"子Agent会话已创建，session_key: {session_key}"
        )

    def get_session(self, session_key: str) -> Optional[dict]:
        """获取会话信息

        Args:
            session_key: 会话密钥

        Returns:
            会话字典，或 None
        """
        with self._lock:
            session = self._sessions.get(session_key)
            if session:
                return session.model_dump()
            return None

    def get_session_by_agent_id(self, agent_id: str) -> Optional[dict]:
        """通过 agent_id 获取会话

        Args:
            agent_id: Agent唯一标识

        Returns:
            会话字典，或 None
        """
        with self._lock:
            session_key = self._agent_index.get(agent_id)
            if session_key:
                session = self._sessions.get(session_key)
                if session:
                    return session.model_dump()
            return None

    def list_sessions(
        self,
        team_name: Optional[str] = None,
        status: Optional[SessionStatus] = None
    ) -> ListSessionsResult:
        """列出所有会话（带过滤）

        Args:
            team_name: 团队名称过滤
            status: 状态过滤

        Returns:
            ListSessionsResult: 会话列表
        """
        with self._lock:
            sessions = list(self._sessions.values())

        # 过滤
        if team_name:
            sessions = [s for s in sessions if s.team_name == team_name]
        if status:
            sessions = [s for s in sessions if s.status == status]

        return ListSessionsResult(
            sessions=[s.model_dump() for s in sessions],
            total=len(sessions)
        )

    def update_session(self, params: UpdateSessionParams) -> UpdateSessionResult:
        """更新会话状态或元数据

        Args:
            params: UpdateSessionParams 参数

        Returns:
            UpdateSessionResult: 更新结果
        """
        with self._lock:
            session = self._sessions.get(params.session_key)
            if not session:
                return UpdateSessionResult(
                    session_key=params.session_key,
                    status="not_found"
                )

            if params.status is not None:
                session.status = params.status
                if params.status == SessionStatus.RUNNING and session.started_at is None:
                    session.started_at = datetime.utcnow()
                elif params.status in (SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED):
                    session.finished_at = datetime.utcnow()

            if params.metadata is not None:
                session.metadata.update(params.metadata)

            return UpdateSessionResult(
                session_key=params.session_key,
                status="ok",
                updated_at=datetime.utcnow()
            )

    def delete_session(self, session_key: str) -> bool:
        """删除会话

        Args:
            session_key: 会话密钥

        Returns:
            是否成功删除
        """
        with self._lock:
            session = self._sessions.pop(session_key, None)
            if session:
                self._agent_index.pop(session.agent_id, None)
                return True
            return False

    def cleanup_stale_sessions(self, max_age_seconds: int = 3600) -> int:
        """清理过期会话

        Args:
            max_age_seconds: 最大存活时间（秒）

        Returns:
            清理的会话数量
        """
        now = datetime.utcnow()
        to_delete = []

        with self._lock:
            for session_key, session in self._sessions.items():
                age = (now - session.created_at).total_seconds()
                if age > max_age_seconds and session.status in (
                    SessionStatus.COMPLETED,
                    SessionStatus.FAILED,
                    SessionStatus.CANCELLED
                ):
                    to_delete.append(session_key)

            for session_key in to_delete:
                session = self._sessions.pop(session_key, None)
                if session:
                    self._agent_index.pop(session.agent_id, None)

        return len(to_delete)


# ============================================================================
# 便捷函数
# ============================================================================

def sessions_spawn(params: SpawnParams) -> SpawnResult:
    """创建子Agent会话

    Args:
        params: SpawnParams 参数

    Returns:
        SpawnResult: 包含 session_key
    """
    manager = SpawnSessionManager.get_instance()
    return manager.create_session(params)


def get_session(session_key: str) -> Optional[dict]:
    """获取会话信息"""
    manager = SpawnSessionManager.get_instance()
    return manager.get_session(session_key)


def list_sessions(
    team_name: Optional[str] = None,
    status: Optional[SessionStatus] = None
) -> ListSessionsResult:
    """列出所有会话"""
    manager = SpawnSessionManager.get_instance()
    return manager.list_sessions(team_name, status)


def update_session(
    session_key: str,
    status: Optional[SessionStatus] = None,
    metadata: Optional[dict] = None
) -> UpdateSessionResult:
    """更新会话"""
    manager = SpawnSessionManager.get_instance()
    return manager.update_session(UpdateSessionParams(
        session_key=session_key,
        status=status,
        metadata=metadata
    ))


# ============================================================================
# BaseTool 实现
# ============================================================================

class SessionsSpawnTool(BaseTool[SpawnParams]):
    """sessions_spawn 工具类"""

    name = "sessions_spawn"
    description = """创建子Agent会话

    主Agent调用此工具创建子Agent，获得 session_key 用于后续通信。

    参数：
    - agent_type: Agent类型（如 code_review, data_analysis, user_research）
    - team_name: 团队名称（可选）
    - context: 传递给子Agent的上下文（可选）
    - metadata: 额外元数据（可选）
    """
    params_class = SpawnParams

    async def execute(self, context: Any, params: SpawnParams) -> ToolResult:
        result = sessions_spawn(params)
        return ToolResult(
            success=True,
            output=result.to_dict()
        )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    'SessionStatus',
    'SpawnSession',
    'SpawnParams',
    'SpawnResult',
    'ListSessionsParams',
    'ListSessionsResult',
    'GetSessionParams',
    'GetSessionResult',
    'UpdateSessionParams',
    'UpdateSessionResult',
    'SpawnSessionManager',
    'sessions_spawn',
    'get_session',
    'list_sessions',
    'update_session',
    'SessionsSpawnTool'
]