"""
SSE (Server-Sent Events) for real-time agent execution status streaming.
<!--zh
SSE 流式 API：Agent 执行状态实时推送，替代 WebSocket 的轻量方案
-->
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.v1.auth import get_current_active_user, User

router = APIRouter(prefix="/sse", tags=["sse"])


# ─── Event models ──────────────────────────────────────────────────────────────


class SSETaskStatus(str):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentEvent(BaseModel):
    """SSE event envelope — matches Magic's event format."""

    event_id: str  # unique event ID
    event_type: str  # agent.started | agent.thinking | agent.tool_call | agent.completed | agent.error
    task_id: str  # conversation/task ID
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    content: str  # text content or tool name
    metadata: Optional[dict] = None  # extra data (tool args, timing, etc.)
    timestamp: str = ""

    def __init__(self, **data):
        data.setdefault("event_id", str(uuid.uuid4())[:8])
        data.setdefault("timestamp", datetime.utcnow().isoformat())
        super().__init__(**data)

    def to_sse(self) -> str:
        """Serialize to SSE format."""
        data = self.model_dump()
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return f"event: {self.event_type}\ndata: {json.dumps(data)}\n\n"


# ─── In-memory event bus (per-process) ───────────────────────────────────────
# In production, replace with Redis Pub/Sub or Kafka

_subscribers: dict[str, asyncio.Queue] = {}


async def event_bus_subscribe(task_id: str) -> asyncio.Queue:
    queue = asyncio.Queue(maxsize=100)
    _subscribers[f"{task_id}:{id(queue)}"] = queue
    return queue


def event_bus_publish(task_id: str, event: AgentEvent) -> None:
    """Fire-and-forget publish to all queues for a task_id."""
    dead = []
    key_prefix = f"{task_id}:"
    for key, queue in _subscribers.items():
        if key.startswith(key_prefix):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                dead.append(key)
    for key in dead:
        del _subscribers[key]


# ─── Simulated agent execution stream ────────────────────────────────────────
# Replace with real agent runner integration


async def simulate_agent_run(task_id: str, prompt: str, user: User) -> AsyncGenerator[str, None]:
    """
    Simulate a multi-step agent execution with SSE events.
    <!--zh
    模拟 Agent 执行流程：注入思考→工具调用→完成等事件流。
    真实场景替换为 AgentRunner.run_stream()
    -->
    """
    steps = [
        ("agent.started", f"🚀 Agent 启动，收到任务: {prompt[:50]}..."),
        ("agent.thinking", "🤔 正在分析问题，构建思维链..."),
        ("agent.thinking", "📊 调用 战略顾问专家 + 运营总监 协同分析..."),
        ("agent.tool_call", '🔧 执行工具: web_search("市场分析 + 竞品调研")'),
        ("agent.thinking", "📈 分析完成，生成方案中..."),
        ("agent.thinking", "✨ 方案优化，风险评估..."),
        ("agent.completed", "✅ 任务完成！方案已生成。"),
    ]

    for event_type, content in steps:
        event = AgentEvent(
            event_type=event_type,
            task_id=task_id,
            agent_id="ceo-agent",
            agent_name="CEO",
            content=content,
            metadata={"user": user.username, "org": user.org_id},
        )
        yield event.to_sse()
        await asyncio.sleep(0.3)  # Simulate processing delay

    # Final done marker
    yield f"event: done\ndata: {json.dumps({'task_id': task_id})}\n\n"


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.get("/tasks/{task_id}/stream")
async def stream_task_events(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """
    <!--zh
    SSE 流式端点：订阅 Agent 执行状态。
    前端 EventSource 连接到 /api/v1/sse/tasks/{task_id}/stream
    -->
    SSE stream for real-time task/agent execution events.
    Connect via EventSource: `new EventSource('/api/v1/sse/tasks/${task_id}/stream')`
    """
    return StreamingResponse(
        _sse_generator(task_id, current_user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


async def _sse_generator(task_id: str, user: User) -> AsyncGenerator[str, None]:
    """Internal generator that handles ping/keepalive and real events."""
    try:
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'task_id': task_id, 'user': user.username})}\n\n"

        # Keepalive ping every 30s
        async def keepalive():
            while True:
                await asyncio.sleep(30)
                yield f": keepalive ping\n\n"

        # Run both concurrently
        async for event in simulate_agent_run(task_id, f"task-{task_id}", user):
            yield event

    except asyncio.CancelledError:
        pass  # Client disconnected cleanly


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    <!--zh
    取消正在执行的 Agent 任务
    -->
    Cancel a running agent task.
    """
    # In production: look up task in Redis/DB and signal cancellation
    return {"task_id": task_id, "status": "cancelled", "cancelled_by": user.username}


@router.get("/tasks/{task_id}/status")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    <!--zh
    查询任务当前状态（非流式）
    -->
    Get current task status (non-streaming).
    """
    # Placeholder — in production query from DB/Redis
    return {
        "task_id": task_id,
        "status": "completed",  # mock
        "progress": 100,
        "events_count": 7,
    }
