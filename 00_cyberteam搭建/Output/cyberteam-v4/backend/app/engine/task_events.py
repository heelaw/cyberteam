"""任务事件"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class TaskEvent(Enum):
    """任务事件枚举"""
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_RETRY = "task.retry"
    TASK_CANCELLED = "task.cancelled"
    TASK_TIMEOUT = "task.timeout"


@dataclass
class TaskEventPayload:
    """任务事件负载"""
    event: TaskEvent
    task_id: str
    task_name: str
    metadata: Optional[dict] = None
