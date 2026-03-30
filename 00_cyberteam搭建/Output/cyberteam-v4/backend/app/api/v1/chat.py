"""对话 API v1 - 抄 Magic。

核心功能：
- 创建/获取/删除会话
- 发送消息
- 流式响应（SSE）
- WebSocket 实时通信

API 路由：
- POST /api/v1/chat/conversations - 创建会话
- GET /api/v1/chat/conversations - 获取会话列表
- GET /api/v1/chat/conversations/{id} - 获取会话详情
- DELETE /api/v1/chat/conversations/{id} - 删除会话
- POST /api/v1/chat/conversations/{id}/messages - 发送消息
- GET /api/v1/chat/conversations/{id}/messages - 获取消息历史
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_db
from ...auth import get_current_user
from ..repositories import ConversationRepository, MessageRepository

router = APIRouter(prefix="/chat", tags=["chat v1"])


# === Request/Response Models ===

class CreateConversationRequest(BaseModel):
    """创建会话请求。"""
    title: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    """发送消息请求。"""
    content: str
    metadata: dict = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """消息响应。"""
    id: str
    conversation_id: str
    sender_type: str
    sender_id: Optional[str]
    content: str
    metadata: dict
    created_at: str


class ConversationResponse(BaseModel):
    """会话响应。"""
    id: str
    user_id: str
    agent_id: Optional[str]
    title: Optional[str]
    status: str
    metadata: dict
    created_at: str
    updated_at: str
    message_count: int = 0


# === Routes ===

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """创建新会话。"""
    repo = ConversationRepository(db)

    conversation = await repo.create(
        user_id=user["sub"],
        title=request.title,
        project_id=request.metadata.get("project_id") if request.metadata else None,
        meta=request.metadata,
    )

    return ConversationResponse(
        id=conversation.id,
        user_id=user["sub"],
        agent_id=request.metadata.get("agent_id") if request.metadata else None,
        title=conversation.title,
        status=conversation.status,
        metadata=conversation.meta or {},
        created_at=conversation.created_at.isoformat() if conversation.created_at else "",
        updated_at=conversation.updated_at.isoformat() if conversation.updated_at else "",
        message_count=0,
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取会话列表。"""
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    conversations = await conv_repo.list_by_user(
        user_id=user["sub"],
        limit=limit,
        offset=offset,
    )

    result = []
    for conv in conversations:
        message_count = await msg_repo.count_by_conversation(conv.id)
        result.append(
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                agent_id=conv.meta.get("agent_id") if conv.meta else None,
                title=conv.title,
                status=conv.status,
                metadata=conv.meta or {},
                created_at=conv.created_at.isoformat() if conv.created_at else "",
                updated_at=conv.updated_at.isoformat() if conv.updated_at else "",
                message_count=message_count,
            )
        )

    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取会话详情。"""
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    conversation = await conv_repo.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    message_count = await msg_repo.count_by_conversation(conversation.id)

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        agent_id=conversation.meta.get("agent_id") if conversation.meta else None,
        title=conversation.title,
        status=conversation.status,
        metadata=conversation.meta or {},
        created_at=conversation.created_at.isoformat() if conversation.created_at else "",
        updated_at=conversation.updated_at.isoformat() if conversation.updated_at else "",
        message_count=message_count,
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """删除会话。"""
    repo = ConversationRepository(db)
    success = await repo.delete(conversation_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return {"status": "ok", "conversation_id": conversation_id}


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """发送消息。"""
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    # 验证会话存在
    conversation = await conv_repo.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    message = await msg_repo.create(
        conversation_id=conversation_id,
        sender_type="user",
        sender_id=user["sub"],
        content=request.content,
        content_type="markdown",
        meta=request.metadata,
    )

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_type=message.sender_type,
        sender_id=message.sender_id,
        content=message.content or "",
        metadata=message.meta or {},
        created_at=message.created_at.isoformat() if message.created_at else "",
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取消息历史。"""
    repo = MessageRepository(db)

    messages = await repo.list_by_conversation(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_type=msg.sender_type,
            sender_id=msg.sender_id,
            content=msg.content or "",
            metadata=msg.meta or {},
            created_at=msg.created_at.isoformat() if msg.created_at else "",
        )
        for msg in messages
    ]
