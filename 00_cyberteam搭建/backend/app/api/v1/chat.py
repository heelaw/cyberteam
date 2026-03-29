"""Chat API endpoints — 集成本地 Claude Code CLI 作为 AI 引擎。"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.deps import get_db, get_current_user
from app.db.models import Conversation, Message
from app.engine.claude_client import query_claude_stream
from app.engine.agent_compiler import agent_compiler

router = APIRouter()

# 对话历史最大回溯条数
_MAX_HISTORY_MESSAGES = 20


class ChatCreateRequest(BaseModel):
    """Request to create a new chat."""
    title: Optional[str] = None
    agent_name: Optional[str] = None


class ChatCreateResponse(BaseModel):
    """Response after creating a chat."""
    id: str
    title: Optional[str]
    agent_name: Optional[str]
    created_at: datetime


class MessageCreateRequest(BaseModel):
    """Request to send a message."""
    content: str
    agent_id: Optional[str] = None   # @提及 Agent 时传入
    agent_name: Optional[str] = None
    model: Optional[str] = None
    thinking_mode: Optional[str] = None
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    """Message response."""
    id: str
    role: str
    content: str
    thinking_mode: Optional[str]
    tokens_used: Optional[int]
    model_used: Optional[str]
    created_at: datetime


class ChatDetailResponse(BaseModel):
    """Chat detail with messages."""
    id: str
    title: Optional[str]
    agent_name: Optional[str]
    status: str
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime


@router.post("", response_model=ChatCreateResponse)
async def create_chat(
    request: ChatCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new conversation."""
    chat_id = str(uuid.uuid4())
    conversation = Conversation(
        id=chat_id,
        title=request.title or "新对话",
        user_id=current_user.get("sub", "anonymous"),
        agent_name=request.agent_name,
        status="active",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return ChatCreateResponse(
        id=conversation.id,
        title=conversation.title,
        agent_name=conversation.agent_name,
        created_at=conversation.created_at,
    )


@router.get("")
async def list_chats(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List user's conversations."""
    user_id = current_user.get("sub", "anonymous")
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "agent_name": c.agent_name,
            "status": c.status,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in conversations
    ]


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get conversation detail with messages."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(Conversation).where(
        Conversation.id == chat_id,
        Conversation.user_id == user_id,
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Load messages
    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == chat_id)
        .order_by(Message.created_at)
    )
    msg_result = await db.execute(msg_stmt)
    messages = msg_result.scalars().all()

    return ChatDetailResponse(
        id=conversation.id,
        title=conversation.title,
        agent_name=conversation.agent_name,
        status=conversation.status,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                thinking_mode=m.thinking_mode,
                tokens_used=m.tokens_used,
                model_used=m.model_used,
                created_at=m.created_at,
            )
            for m in messages
        ],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a conversation."""
    user_id = current_user.get("sub", "anonymous")
    stmt = delete(Conversation).where(
        Conversation.id == chat_id,
        Conversation.user_id == user_id,
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "deleted", "id": chat_id}


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: str,
    request: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Send a message and get AI response (non-streaming fallback)."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(Conversation).where(
        Conversation.id == chat_id,
        Conversation.user_id == user_id,
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=chat_id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)
    await db.commit()

    # Call Claude Code CLI synchronously
    full_response = ""
    model_used = "claude-code"
    tokens_used = 0
    async for evt in query_claude_stream(request.content):
        if evt["type"] == "assistant" and "text" in evt:
            full_response += evt["text"]
        elif evt["type"] == "result":
            model_used = evt.get("model", "claude-code")
            tokens_used = evt.get("usage", {}).get("output_tokens", 0)

    if not full_response:
        full_response = "抱歉，AI 暂时无法响应，请稍后重试。"

    ai_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=chat_id,
        role="assistant",
        content=full_response,
        thinking_mode=request.thinking_mode,
        model_used=model_used,
        tokens_used=tokens_used,
    )
    db.add(ai_msg)
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(ai_msg)

    return MessageResponse(
        id=ai_msg.id,
        role=ai_msg.role,
        content=ai_msg.content,
        thinking_mode=ai_msg.thinking_mode,
        tokens_used=ai_msg.tokens_used,
        model_used=ai_msg.model_used,
        created_at=ai_msg.created_at,
    )


@router.post("/{chat_id}/stream")
async def stream_message(
    chat_id: str,
    request: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Send a message and stream AI response via SSE (Server-Sent Events).

    参考 CodePilot 的 streamClaude 实现，通过 Claude Code CLI 的
    --output-format stream-json 模式获取实时流式输出。
    """
    user_id = current_user.get("sub", "anonymous")
    stmt = select(Conversation).where(
        Conversation.id == chat_id,
        Conversation.user_id == user_id,
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=chat_id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)
    await db.commit()

    # 查找 @提及的 Agent SOUL（支持 agent_name 字段）
    # 先从 YAML 编译器查，再从 DB 查 custom_agent
    system_prompt: str | None = None
    agent_name_str: str | None = None
    lookup_name = request.agent_name or request.agent_id

    if lookup_name:
        # 1. 先从 YAML 编译器查（内置 Agent）
        agent = agent_compiler.get_agent(lookup_name)
        if agent and agent.system_prompt:
            system_prompt = agent.system_prompt
            agent_name_str = agent.name
        else:
            # 2. 再从 DB 查 custom_agent
            from sqlalchemy import select as sa_select
            from app.db.models import CustomAgent
            stmt = sa_select(CustomAgent).where(
                CustomAgent.name == lookup_name,
                CustomAgent.is_active == True,
            )
            result = await db.execute(stmt)
            db_agent = result.scalar_one_or_none()
            if db_agent:
                compiled = agent_compiler.add_custom_agent(db_agent)
                system_prompt = compiled.system_prompt
                agent_name_str = compiled.name

    async def event_generator():
        full_response = ""
        model_used = "claude-code"
        tokens_used = 0
        session_id = None

        try:
            # 如果有 @提及的 Agent，先发一个状态事件
            if agent_name_str:
                yield f"data: {json.dumps({'type': 'status', 'agent': agent_name_str, 'data': f'正在调用 {agent_name_str}...'})}\n\n"

            async for evt in query_claude_stream(
                request.content,
                system_prompt=system_prompt,
            ):
                # 转发 SSE 事件
                yield f"data: {json.dumps(evt, ensure_ascii=False)}\n\n"

                # 收集完整响应用于保存
                if evt["type"] == "text":
                    full_response += evt.get("data", "")
                elif evt["type"] == "status":
                    session_id = evt.get("session_id")
                    m = evt.get("model")
                    if isinstance(m, str):
                        model_used = m
                elif evt["type"] == "result":
                    m = evt.get("model")
                    if isinstance(m, str):
                        model_used = m
                    elif isinstance(m, dict):
                        model_used = list(m.keys())[0] if m else model_used
                    tokens_used = evt.get("usage", {}).get("output_tokens", 0)

            # 流结束，保存 AI 消息到 DB
            if full_response:
                ai_msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=chat_id,
                    role="assistant",
                    content=full_response,
                    thinking_mode=request.thinking_mode,
                    model_used=model_used,
                    tokens_used=tokens_used,
                    metadata={"agent_name": agent_name_str} if agent_name_str else None,
                )
                db.add(ai_msg)
                conversation.updated_at = datetime.utcnow()
                await db.commit()

            yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
            # 保存部分响应
            if full_response:
                ai_msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=chat_id,
                    role="assistant",
                    content=full_response + f"\n\n[错误: {e}]",
                    model_used=model_used,
                )
                db.add(ai_msg)
                await db.commit()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{chat_id}/messages")
async def get_messages(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get messages for a conversation."""
    user_id = current_user.get("sub", "anonymous")
    # Verify ownership
    conv_stmt = select(Conversation).where(
        Conversation.id == chat_id,
        Conversation.user_id == user_id,
    )
    conv_result = await db.execute(conv_stmt)
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    stmt = select(Message).where(
        Message.conversation_id == chat_id,
    ).order_by(Message.created_at)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "sender_type": m.role,
            "sender_id": m.role,
            "content": m.content,
            "metadata": {
                "thinking_mode": m.thinking_mode,
                "tokens_used": m.tokens_used,
                "model_used": m.model_used,
            },
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]


