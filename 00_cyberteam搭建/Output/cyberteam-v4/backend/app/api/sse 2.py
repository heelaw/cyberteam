"""SSE (Server-Sent Events) 流式输出端点。

核心功能：
- 用于不支持 WebSocket 的场景
- 流式推送 Agent 执行进度
- 支持 CORS 跨域
- 标准 SSE 协议

SSE 协议议格式：
- 每条消息以 "data: {json}\\n\\n" 格式发送
- 以 "data: [DONE]\\n\\n" 结束流
- Content-Type: text/event-stream

事件类型：
- thinking: Agent 思考中
- routed: CEO 路由完成，分配到部门
- agent_start: Agent 开始执行
- agent_output: Agent 输出内容（流式）
- agent_complete: Agent 执行完成
- debate_start: 辩论开始
- debate_output: 辩论内容
- debate_converged: 辩论收敛
- approval_request: 审批请求
- done: 流结束
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import logging
import asyncio
from datetime import datetime

log = logging.getLogger("cyberteam.sse")

router = APIRouter()


async def _generate_task_events(
    task_id: str,
    message: str,
) -> None:
    """生成任务执行事件流。

    这是一个模拟实现，后续需要集成真实的 Agent 引擎。
    真实实现应该：
    1. 将 message 发送给 CEO 路由引擎
    2. CEO 路由后分配部门
    3. 部门 Agent 执行
    4. 流式输出每个阶段的结果
    """
    # 阶段1: CEO 思考
    yield {
        "type": "thinking",
        "data": {
            "stage": "ceo_routing",
            "message": "CEO 正在分析任务意图意图...",
            "task_id": task_id,
        },
        "timestamp": datetime.now().isoformat(),
    }
    await asyncio.sleep(0.1)

    # 阶段2: 路由结果
    yield {
        "type": "routed",
        "data": {
            "department": "growth",
            "reason": "任务涉及增长策略",
            "task_id": task_id,
        },
        "timestamp": datetime.now().isoformat(),
    }
    await asyncio.sleep(0.1)

    # 阶段3: Agent 开始
    yield {
        "type": "agent_start",
        "data": {
            "agent": "growth_director",
            "department": "growth",
            "task_id": task_id,
        },
        "timestamp": datetime.now().isoformat(),
    }
    await asyncio.sleep(0.1)

    # 阶段4: Agent 输出
    yield {
        "type": "agent_output",
        "data": {
            "agent": "growth_director",
            "content": "正在制定增长策略...",
            "task_id": task_id,
        },
        "timestamp": datetime.now().isoformat(),
    }
    await asyncio.sleep(0.1)

    # 阶段5: 完成
    yield {
        "type": "agent_complete",
        "data": {
            "agent": "growth_director",
            "task_id": task_id,
            "duration_ms": 1500,
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/{task_id}")
async def stream_response(
    task_id: str,
    message: str = Query("", description="用户消息"),
) -> StreamingResponse:
    """SSE 流式输出端点。

    路径: GET /{task_id}?message=xxx

    返回 SSE 事件流，客户端可以用 EventSource API 接收。

    示例（前端）:
        const eventSource = new EventSource('/stream/task123?message=帮我分析增长策略');
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data === '[DONE]') {
                eventSource.close();
                return;
            }
            console.log(data);
        });
    """

    async def event_generator():
        try:
            async for event in _generate_task_events(task_id, message):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            log.error(f"SSE stream error: {e}")
            error_event = {
                "type": "error",
                "data": {"message": str(e)},
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # nginx 不缓冲
        },
    )


@router.get("/{task_id}/status")
async def stream_status(task_id: str):
    """获取任务流式状态（非 SSE，普通 JSON）。"""
    return {
        "task_id": task_id,
        "stream_available": True,
        "supported_events": [
            "thinking",
            "routed",
            "agent_start",
            "agent_output",
            "agent_complete",
            "debate_start",
            "debate_output",
            "debate_converged",
            "approval_request",
            "done",
        ],
    }
