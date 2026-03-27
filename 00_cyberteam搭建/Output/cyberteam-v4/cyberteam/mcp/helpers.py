"""Helper utilities for CyberTeam MCP tools.

This module provides the helper functions that were originally expected
from 'clawteam.mcp.helpers' but do not exist in ClawTeam 0.2.0.
These are implemented here to maintain compatibility.
"""

from __future__ import annotations

from typing import Any, TypeVar
from enum import Enum

from cyberteam.team.models import TaskPriority, TaskStatus
from cyberteam.team.tasks import TaskStore


E = TypeVar("E", bound=Enum)


def task_store(team_name: str) -> TaskStore:
    """Get or create a task store for a team."""
    return TaskStore(team_name)


def cost_store(team_name: str) -> Any:
    """Get cost tracking store for a team.

    TODO: Implement cost tracking if needed.
    """
    raise NotImplementedError("cost_store not yet implemented")


def plan_manager(team_name: str) -> Any:
    """Get plan manager for a team.

    TODO: Implement plan management if needed.
    """
    raise NotImplementedError("plan_manager not yet implemented")


def team_mailbox(team_name: str) -> Any:
    """Get team mailbox for a team.

    TODO: Implement team mailbox if needed.
    """
    raise NotImplementedError("team_mailbox not yet implemented")


def to_payload(data: Any) -> dict:
    """Convert data to MCP payload format.

    Converts Pydantic models and other data to dictionary format
    suitable for MCP tool responses.
    """
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_none=True)
    if hasattr(data, "dict"):
        return data.dict(exclude_none=True)
    if hasattr(data, "__dict__"):
        return {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
    return data


def coerce_enum(enum_class: type[E], value: Any) -> E | None:
    """Coerce a value to an enum, returning None if invalid.

    Args:
        enum_class: The enum class to coerce to
        value: The value to coerce

    Returns:
        The enum value if valid, None otherwise
    """
    if value is None:
        return None
    if isinstance(value, enum_class):
        return value
    try:
        return enum_class(value)
    except (ValueError, TypeError):
        return None


def fail(message: str) -> None:
    """Raise a failure exception with a message.

    Args:
        message: The error message

    Raises:
        Exception: Always raises with the given message
    """
    raise Exception(message)


def translate_error(exc: Exception) -> Exception:
    """Translate an exception to a user-friendly error.

    Args:
        exc: The original exception

    Returns:
        A user-friendly exception
    """
    return exc


def require_team(func):
    """Decorator to require a valid team context.

    TODO: Implement team requirement decorator if needed.
    """
    return func
