"""Task MCP tools."""

from __future__ import annotations

from ..helpers import coerce_enum, fail, task_store, to_payload, translate_error
from cyberteam.team.models import TaskPriority, TaskStatus
from typing import Union, List


def task_list(
    team_name: str,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by_priority: bool = False,
) -> List[dict]:
    """List tasks for a team with optional filters."""
    store = task_store(team_name)
    return to_payload(
        store.list_tasks(
            status=coerce_enum(TaskStatus, status),
            owner=owner,
            priority=coerce_enum(TaskPriority, priority),
            sort_by_priority=sort_by_priority,
        )
    )


def task_get(team_name: str, task_id: str) -> dict:
    """Get one task by ID."""
    task = task_store(team_name).get(task_id)
    if task is None:
        fail(f"Task '{task_id}' not found")
    return to_payload(task)


def task_stats(team_name: str) -> dict:
    """Get task counts and timing stats for a team."""
    return to_payload(task_store(team_name).get_stats())


def task_create(
    team_name: str,
    subject: str,
    description: str = "",
    owner: str = "",
    priority: Optional[str] = None,
    blocks: Union[List[str], None]=
    blocked_by: Union[List[str], None]=
    metadata: Union[dict, None] = None
) -> dict:
    """Create a task with optional owner, dependencies, and metadata."""
    return to_payload(
        task_store(team_name).create(
            subject=subject,
            description=description,
            owner=owner,
            priority=coerce_enum(TaskPriority, priority),
            blocks=blocks,
            blocked_by=blocked_by,
            metadata=metadata,
        )
    )


def task_update(
    team_name: str,
    task_id: str,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    add_blocks: Union[List[str], None]=
    add_blocked_by: Union[List[str], None]=
    metadata: Union[dict, None] = None
    caller: str = "",
    force: bool = False,
) -> dict:
    """Update a task's fields, status, dependencies, or metadata."""
    try:
        task = task_store(team_name).update(
            task_id=task_id,
            status=coerce_enum(TaskStatus, status),
            owner=owner,
            subject=subject,
            description=description,
            priority=coerce_enum(TaskPriority, priority),
            add_blocks=add_blocks,
            add_blocked_by=add_blocked_by,
            metadata=metadata,
            caller=caller,
            force=force,
        )
    except Exception as exc:
        raise translate_error(exc) from exc
    if task is None:
        fail(f"Task '{task_id}' not found")
    return to_payload(task)

