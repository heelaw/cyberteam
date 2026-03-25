from __future__ import annotations
"""Pluggable transport backends for message delivery."""


from cyberteam.transport.base import Transport


def get_transport(name: str, team_name: str, **kwargs) -> Transport:
    """Factory: create a transport by name."""
    if name == "p2p":
        from cyberteam.transport.p2p import P2PTransport
        return P2PTransport(team_name, **kwargs)
    from cyberteam.transport.file import FileTransport
    return FileTransport(team_name)


__all__ = [
    "Transport",
    "get_transport",
    # 新增模块
    "TransportLayer",
    "MessageRouter",
    "InboxManager",
    "HandoffProtocol",
]

# 延迟导入避免循环依赖
from cyberteam.transport.transport import TransportLayer
from cyberteam.transport.message_router import MessageRouter
from cyberteam.transport.inbox_manager import InboxManager
from cyberteam.transport.handoff_protocol import HandoffProtocol