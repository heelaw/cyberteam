from __future__ import annotations
"""Pluggable transport backends for message delivery."""


# Import base first
from cyberteam.transport.base import Transport

# Import implementations (avoid name collision with 'file' module by using alias)
from cyberteam.transport.file import FileTransport as _FileTransport
from cyberteam.transport.p2p import P2PTransport as _P2PTransport


def get_transport(name: str, team_name: str, **kwargs) -> Transport:
    """Factory: create a transport by name."""
    if name == "p2p":
        return _P2PTransport(team_name, **kwargs)
    return _FileTransport(team_name)


# Re-export for convenience
FileTransport = _FileTransport
P2PTransport = _P2PTransport


__all__ = [
    "Transport",
    "get_transport",
    "FileTransport",
    "P2PTransport",
]
