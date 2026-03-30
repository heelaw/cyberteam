"""
聊天 API 接口

提供对话和消息管理接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 内存存储（生产环境应使用数据库）
conversations_db: dict[str, dict] = {}
messages_db: dict[str, list[dict]] = {}


# === Models ===

class ConversationCreate(BaseModel):
    title: str = "新对话"


class MessageCreate(BaseModel):
    message: str


class Conversation(BaseModel):
    id: str
    title: str
    created_at: int
    updated_at: int


class Message(BaseModel):
    id: str
    role: str
    content: str
    timestamp: int


# === Routes ===

@router.get("/conversations", response_model=list[Conversation])
async def list_conversations():
    """列出所有对话"""
    return [
        Conversation(
            id=cid,
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
        for cid, data in conversations_db.items()
    ]


@router.post("/conversations", response_model=Conversation)
async def create_conversation(data: ConversationCreate):
    """创建新对话"""
    cid = str(uuid.uuid4())
    now = int(datetime.now().timestamp() * 1000)

    conversations_db[cid] = {
        "title": data.title,
        "created_at": now,
        "updated_at": now
    }
    messages_db[cid] = []

    return Conversation(
        id=cid,
        title=data.title,
        created_at=now,
        updated_at=now
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="对话不存在")

    del conversations_db[conversation_id]
    if conversation_id in messages_db:
        del messages_db[conversation_id]

    return {"message": "删除成功"}


@router.get("/conversations/{conversation_id}/messages", response_model=list[Message])
async def get_messages(conversation_id: str):
    """获取对话消息"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="对话不存在")

    return [
        Message(
            id=msg["id"],
            role=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"]
        )
        for msg in messages_db.get(conversation_id, [])
    ]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, data: MessageCreate):
    """发送消息"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="对话不存在")

    now = int(datetime.now().timestamp() * 1000)
    user_message = Message(
        id=f"msg_{now}_user",
        role="user",
        content=data.message,
        timestamp=now
    )

    # 存储用户消息
    if conversation_id not in messages_db:
        messages_db[conversation_id] = []
    messages_db[conversation_id].append(user_message.model_dump())

    # 更新对话时间
    conversations_db[conversation_id]["updated_at"] = now

    # 生成模拟响应（生产环境应调用 Agent 引擎）
    assistant_message = Message(
        id=f"msg_{now}_assistant",
        role="assistant",
        content=f"收到任务: {data.message}\n\n正在调度数字员工执行...",
        timestamp=now + 1
    )

    messages_db[conversation_id].append(assistant_message.model_dump())

    return {
        "conversation_id": conversation_id,
        "message": assistant_message
    }
