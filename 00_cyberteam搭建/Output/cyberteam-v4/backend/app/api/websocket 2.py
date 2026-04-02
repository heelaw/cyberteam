"""WebSocket 实时通信端点。

核心功能：
- 多用户 WebSocket 连接管理
- 消息路由：根据 type 分发到不同处理器
- 心跳检测：客户端定期发送 heartbeat，服务端回复 ack
- 广播：向所有在线用户推送消息
- 事件总线集成：将事件总线中的事件实时推送到前端

消息协议：
- 客户端 -> 服务端:
  - {"type": "chat_message", "data": {"message": "...", "task_id": "..."}}
  - {"type": "heartbeat"}
- 服务端 -> 客户端:
  - {"type": "agent_thinking", "data": {"message": "..."}}
  - {"type": "agent_output", "data": {"content": "...", "agent": "..."}}
  - {"type": "agent_complete", "data": {"task_id": "..."}}
  - {"type": "heartbeat_ack"}
  - {"type": "approval_request", "data": {...}}
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional, Set
import json
import logging
from datetime import datetime

log = logging.getLogger("cyberteam.websocket")

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器。

    功能：
    - 用户连接/断开管理
    - 单播（send to specific user）
    - 广播（broadcast to all）
    - 按会话分组（group by conversation）
    """

    def __init__(self):
        # user_id -> WebSocket
        self.active: Dict[str, WebSocket] = {}
        # conversation_id -> set of user_ids
        self._rooms: Dict[str, Set[str]] = {}

    async def connect(self, user_id: str, ws: WebSocket) -> None:
        """建立连接。"""
        await ws.accept()
        self.active[user_id] = ws
        log.info(f"WebSocket connected: {user_id} (total: {len(self.active)})")

    def disconnect(self, user_id: str) -> None:
        """断开连接。"""
        self.active.pop(user_id, None)
        # 从所有房间中移除
        for room_users in self._rooms.values():
            room_users.discard(user_id)
        log.info(f"WebSocket disconnected: {user_id} (total: {len(self.active)})")

    async def send(self, user_id: str, data: dict) -> bool:
        """发送消息给指定用户。

        Returns:
            True 表示发送成功，False 表示用户不在线
        """
        ws = self.active.get(user_id)
        if ws:
            try:
                await ws.send_json(data)
                return True
            except Exception as e:
                log.error(f"WebSocket send error to {user_id}: {e}")
                self.disconnect(user_id)
        return False

    async def broadcast(self, data: dict) -> None:
        """广播消息给所有在线用户。"""
        disconnected = []
        for user_id, ws in self.active.items():
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(user_id)

        for user_id in disconnected:
            self.disconnect(user_id)

    async def join_room(self, conversation_id: str, user_id: str) -> None:
        """加入会话房间。"""
        if conversation_id not in self._rooms:
            self._rooms[conversation_id] = set()
        self._rooms[conversation_id].add(user_id)

    async def leave_room(self, conversation_id: str, user_id: str) -> None:
        """离开会话房间。"""
        if conversation_id in self._rooms:
            self._rooms[conversation_id].discard(user_id)

    async def send_to_room(self, conversation_id: str, data: dict) -> None:
        """发送消息给房间内所有用户。"""
        user_ids = self._rooms.get(conversation_id, set())
        for user_id in user_ids:
            await self.send(user_id, data)

    def get_online_count(self) -> int:
        """获取在线用户数。"""
        return len(self.active)

    def get_online_users(self) -> list:
        """获取在线用户列表。"""
        return list(self.active.keys())


# 全局连接管理器
ws_manager = ConnectionManager()


async def _handle_chat_message(user_id: str, data: dict) -> None:
    """处理聊天消息。"""
    message = data.get("message", "")
    task_id = data.get("task_id", "")
    conversation_id = data.get("conversation_id", "")

    log.info(f"Chat message from {user_id}: task={task_id} msg_len={len(message)}")

    # 通知用户：Agent 开始思考
    await ws_manager.send(user_id, {
        "type": "agent_thinking",
        "data": {
            "message": "CEO 正在分析任务...",
            "task_id": task_id,
            "stage": "ceo_routing",
        },
        "timestamp": datetime.now().isoformat(),
    })

    # 尝试转发给 Agent 引擎（如果引擎已加载）
    try:
        from ..main import _module_status
        if _module_status.get("engine.ceo", {}).get("status") == "ok":
            # 真实引擎路由 - TODO: 集成引擎后实现
            pass
    except Exception:
        pass


async def _handle_heartbeat(user_id: str) -> None:
    """处理心跳。"""
    await ws_manager.send(user_id, {"type": "heartbeat_ack"})


# 消息处理器映射
_MESSAGE_HANDLERS = {
    "chat_message": _handle_chat_message,
    "heartbeat": _handle_heartbeat,
}


@router.websocket("/ws/{user_id}")
async def ws_endpoint(ws: WebSocket, user_id: str) -> None:
    """WebSocket 主端点。

    路径: /ws/{user_id}

    连接后客户端可发送以下消息：
    - {"type": "chat_message", "data": {"message": "...", "task_id": "..."}}
    - {"type": "heartbeat"}
    """
    await ws_manager.connect(user_id, ws)

    # 发送欢迎消息
    await ws_manager.send(user_id, {
        "type": "connected",
        "data": {
            "user_id": user_id,
            "online_count": ws_manager.get_online_count(),
        },
    })

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws_manager.send(user_id, {
                    "type": "error",
                    "data": {"message": "Invalid JSON"},
                })
                continue

            msg_type = data.get("type", "")
            handler = _MESSAGE_HANDLERS.get(msg_type)

            if handler:
                try:
                    if msg_type == "heartbeat":
                        await handler(user_id)
                    else:
                        await handler(user_id, data.get("data", {}))
                except Exception as e:
                    log.error(f"Handler error for {msg_type}: {e}")
                    await ws_manager.send(user_id, {
                        "type": "error",
                        "data": {"message": f"Handler error: {str(e)}"},
                    })
            else:
                log.warning(f"Unknown message type: {msg_type}")
                await ws_manager.send(user_id, {
                    "type": "error",
                    "data": {"message": f"Unknown type: {msg_type}"},
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
    except Exception as e:
        log.error(f"WebSocket error for {user_id}: {e}")
        ws_manager.disconnect(user_id)


@router.get("/ws/status")
async def ws_status():
    """获取 WebSocket 连接状态。"""
    return {
        "online_count": ws_manager.get_online_count(),
        "online_users": ws_manager.get_online_users(),
    }
