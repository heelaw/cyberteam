"""Spawn API v1 - 子Agent双向通信管理

API 路由：
- POST /api/v1/spawn/sessions - 创建子Agent会话
- GET /api/v1/spawn/sessions - 列出所有会话
- GET /api/v1/spawn/sessions/{session_key} - 获取会话详情
- DELETE /api/v1/spawn/sessions/{session_key} - 删除会话
- POST /api/v1/spawn/sessions/{session_key}/send - 向子Agent发送消息并等待回复
- POST /api/v1/spawn/sessions/{session_key}/reply - 子Agent提交回复
- POST /api/v1/spawn/sessions/{session_key}/update - 更新会话状态
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.tools.sessions_spawn import (
    SpawnSessionManager,
    SpawnParams,
    SpawnResult,
    SessionStatus,
    ListSessionsParams,
    ListSessionsResult,
)
from backend.app.tools.sessions_send import (
    SessionsSendParams,
    SessionsSendResult,
    sessions_send,
)
from backend.app.tools.sessions_receive import (
    SessionsReceiveParams,
    SessionsReceiveResult,
    SessionsReplyParams,
    SessionsReplyResult,
    sessions_receive,
    sessions_reply,
)

router = APIRouter(prefix="/spawn", tags=["spawn v1"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SpawnRequest(BaseModel):
    """创建子Agent会话请求"""
    agent_type: str = Field(..., description="Agent类型，如 code_review, data_analysis")
    team_name: str = Field(default="default", description="所属团队名称")
    context: dict = Field(default_factory=dict, description="传递给子Agent的上下文")
    metadata: dict = Field(default_factory=dict, description="额外元数据")


class SpawnResponse(BaseModel):
    """创建子Agent会话响应"""
    session_key: str
    agent_type: str
    agent_id: str
    status: str
    created_at: str
    message: str


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    message: str = Field(..., description="发送给子Agent的消息")
    timeout_seconds: int = Field(default=30, description="等待回复超时秒数")
    round_limit: Optional[int] = Field(default=5, description="最大轮次限制")


class ReplyRequest(BaseModel):
    """子Agent提交回复请求"""
    reply: str = Field(..., description="回复内容")
    success: bool = Field(default=True, description="是否成功完成任务")


class UpdateSessionRequest(BaseModel):
    """更新会话状态请求"""
    status: Optional[str] = Field(default=None, description="新状态")
    metadata: Optional[dict] = Field(default=None, description="更新的元数据")


class SessionResponse(BaseModel):
    """会话响应"""
    session_key: str
    found: bool
    session: Optional[dict] = None


# ============================================================================
# Routes
# ============================================================================

@router.post("/sessions", response_model=SpawnResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SpawnRequest):
    """创建新的子Agent会话

    主Agent调用此接口创建子Agent，获得 session_key 用于后续通信。
    """
    manager = SpawnSessionManager.get_instance()

    params = SpawnParams(
        agent_type=request.agent_type,
        team_name=request.team_name,
        context=request.context,
        metadata=request.metadata
    )

    result = manager.create_session(params)

    return SpawnResponse(
        session_key=result.session_key,
        agent_type=result.agent_type,
        agent_id=result.agent_id,
        status=result.status,
        created_at=result.created_at.isoformat(),
        message=result.message
    )


@router.get("/sessions", response_model=dict)
async def list_sessions(
    team_name: Optional[str] = None,
    status_filter: Optional[str] = None
):
    """列出所有子Agent会话（支持过滤）

    Args:
        team_name: 团队名称过滤
        status_filter: 状态过滤 (pending/running/waiting/completed/failed/cancelled)
    """
    manager = SpawnSessionManager.get_instance()

    session_status = None
    if status_filter:
        try:
            session_status = SessionStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {status_filter}"
            )

    result = manager.list_sessions(team_name=team_name, status=session_status)

    return {
        "sessions": result.sessions,
        "total": result.total
    }


@router.get("/sessions/{session_key}", response_model=SessionResponse)
async def get_session(session_key: str):
    """获取子Agent会话详情

    Args:
        session_key: 会话密钥，格式: spawn:{agent_type}:{agent_id}
    """
    manager = SpawnSessionManager.get_instance()
    session = manager.get_session(session_key)

    if not session:
        return SessionResponse(
            session_key=session_key,
            found=False,
            session=None
        )

    return SessionResponse(
        session_key=session_key,
        found=True,
        session=session
    )


@router.delete("/sessions/{session_key}")
async def delete_session(session_key: str):
    """删除子Agent会话

    Args:
        session_key: 会话密钥
    """
    manager = SpawnSessionManager.get_instance()
    success = manager.delete_session(session_key)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_key} 不存在"
        )

    return {"status": "ok", "session_key": session_key}


@router.post("/sessions/{session_key}/send")
async def send_to_session(session_key: str, request: SendMessageRequest):
    """向子Agent发送消息并同步等待回复（乒乓球协议）

    主Agent调用此接口向子Agent发送指令，等待子Agent执行结果。
    支持最多5轮对话。

    Args:
        session_key: 会话密钥
        message: 发送给子Agent的消息
        timeout_seconds: 等待回复超时时间（默认30秒）
    """
    params = SessionsSendParams(
        session_key=session_key,
        message=request.message,
        timeout_seconds=request.timeout_seconds,
        round_limit=request.round_limit
    )

    result = sessions_send(params)

    if result.status == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_key} 不存在"
        )

    return result.to_dict()


@router.post("/sessions/{session_key}/reply")
async def reply_from_session(session_key: str, request: ReplyRequest):
    """子Agent提交回复给主Agent

    子Agent调用此接口提交执行结果或错误信息。

    Args:
        session_key: 会话密钥
        reply: 回复内容
        success: 是否成功完成任务
    """
    params = SessionsReplyParams(
        session_key=session_key,
        reply=request.reply,
        success=request.success
    )

    result = sessions_reply(params)

    if result.error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result.to_dict()


@router.get("/sessions/{session_key}/receive")
async def receive_message(session_key: str, timeout_seconds: int = 30):
    """子Agent获取主Agent发来的消息

    子Agent轮询此接口检查是否有来自主Agent的新消息。

    Args:
        session_key: 会话密钥
        timeout_seconds: 等待消息的超时时间（默认30秒）
    """
    params = SessionsReceiveParams(
        session_key=session_key,
        timeout_seconds=timeout_seconds
    )

    result = sessions_receive(params)

    return result.to_dict()


@router.post("/sessions/{session_key}/update")
async def update_session_status(session_key: str, request: UpdateSessionRequest):
    """更新子Agent会话状态

    Args:
        session_key: 会话密钥
        status: 新状态 (pending/running/waiting/completed/failed/cancelled)
        metadata: 更新的元数据
    """
    manager = SpawnSessionManager.get_instance()

    new_status = None
    if request.status:
        try:
            new_status = SessionStatus(request.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {request.status}"
            )

    params = UpdateSessionParams(
        session_key=session_key,
        status=new_status,
        metadata=request.metadata
    )

    result = manager.update_session(params)

    if result.status == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"会话 {session_key} 不存在"
        )

    return {
        "session_key": result.session_key,
        "status": result.status,
        "updated_at": result.updated_at.isoformat()
    }


# ============================================================================
# 健康检查
# ============================================================================

@router.get("/health")
async def spawn_health():
    """Spawn 服务健康检查"""
    manager = SpawnSessionManager.get_instance()
    sessions_result = manager.list_sessions()

    return {
        "status": "healthy",
        "total_sessions": sessions_result.total,
        "services": {
            "spawn_manager": "ok",
            "conversation_manager": "ok"
        }
    }