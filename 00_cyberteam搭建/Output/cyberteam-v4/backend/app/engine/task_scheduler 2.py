"""任务调度器 - DDD 领域服务"""
import asyncio
import uuid
import logging
from datetime import datetime
from typing import Optional, Callable, Awaitable, Any
from dataclasses import dataclass, field

from .task_types import TaskStatus, TaskType, TaskResult
from .task_events import TaskEvent, TaskEventPayload

log = logging.getLogger("cyberteam.engine.task_scheduler")


@dataclass
class TaskScheduler:
    """任务调度实体"""
    id: str
    name: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.UNKNOWN
    expect_time: Optional[datetime] = None
    actual_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    retry_times: int = 0
    max_retries: int = 3
    callback_method: str = ""
    callback_params: dict = field(default_factory=dict)
    result: Optional[TaskResult] = None
    error_message: Optional[str] = None

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """状态转换合法性检查"""
        valid = {
            TaskStatus.UNKNOWN: [TaskStatus.PENDING],
            TaskStatus.PENDING: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
            TaskStatus.RUNNING: [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT],
            TaskStatus.FAILED: [TaskStatus.RETRY, TaskStatus.PENDING],
            TaskStatus.RETRY: [TaskStatus.PENDING, TaskStatus.FAILED],
            TaskStatus.SUCCESS: [],
            TaskStatus.CANCELLED: [],
            TaskStatus.TIMEOUT: [TaskStatus.RETRY, TaskStatus.FAILED],
        }
        return new_status in valid.get(self.status, [])

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "expect_time": self.expect_time.isoformat() if self.expect_time else None,
            "actual_time": self.actual_time.isoformat() if self.actual_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "retry_times": self.retry_times,
            "max_retries": self.max_retries,
            "callback_method": self.callback_method,
            "callback_params": self.callback_params,
            "result": {
                "success": self.result.success if self.result else None,
                "output": self.result.output if self.result else None,
                "error": self.result.error if self.result else None,
                "cost_time_ms": self.result.cost_time_ms if self.result else None,
                "retry_count": self.result.retry_count if self.result else None,
            } if self.result else None,
            "error_message": self.error_message,
        }


class TaskSchedulerDomainService:
    """
    任务调度领域服务
    - 创建即时/定时/Cron 任务
    - 执行任务（含重试逻辑）
    - 取消任务
    """

    def __init__(self):
        self._tasks: dict[str, TaskScheduler] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._cron_jobs: dict[str, str] = {}  # task_id -> cron_expr
        self._event_handlers: dict[TaskEvent, list[Callable]] = {}

    def on_task_event(self, event: TaskEvent, handler: Callable[[TaskEventPayload], Awaitable[None]]) -> None:
        """注册任务事件处理器"""
        self._event_handlers.setdefault(event, []).append(handler)

    async def _emit_event(self, event: TaskEvent, task: TaskScheduler, metadata: Optional[dict] = None) -> None:
        """发射任务事件"""
        payload = TaskEventPayload(
            event=event,
            task_id=task.id,
            task_name=task.name,
            metadata=metadata,
        )
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                result = handler(payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                log.error(f"Event handler error [{event.value} -> {handler.__name__}]: {e}")

    async def create_task(
        self,
        name: str,
        callback: Callable[[dict], Awaitable[Any]],
        params: dict,
        max_retries: int = 3
    ) -> str:
        """创建即时任务"""
        task_id = str(uuid.uuid4())[:8]
        task = TaskScheduler(
            id=task_id,
            name=name,
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.PENDING,
            max_retries=max_retries,
            callback_method=getattr(callback, '__name__', str(callback)),
            callback_params=params
        )
        self._tasks[task_id] = task
        await self._emit_event(TaskEvent.TASK_CREATED, task)
        # 立即调度执行
        asyncio.create_task(self._execute_task(task_id, callback))
        return task_id

    async def create_scheduled_task(
        self,
        name: str,
        run_at: datetime,
        callback: Callable[[dict], Awaitable[Any]],
        params: dict,
        max_retries: int = 3
    ) -> str:
        """创建定时任务"""
        task_id = str(uuid.uuid4())[:8]
        task = TaskScheduler(
            id=task_id,
            name=name,
            task_type=TaskType.SCHEDULED,
            status=TaskStatus.PENDING,
            expect_time=run_at,
            max_retries=max_retries,
            callback_method=getattr(callback, '__name__', str(callback)),
            callback_params=params
        )
        self._tasks[task_id] = task
        await self._emit_event(TaskEvent.TASK_CREATED, task)
        # 延迟执行
        delay = (run_at - datetime.utcnow()).total_seconds()
        if delay > 0:
            asyncio.create_task(self._delayed_execute(task_id, callback, delay))
        else:
            asyncio.create_task(self._execute_task(task_id, callback))
        return task_id

    async def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self._tasks.get(task_id)
        if not task:
            return False
        if task.can_transition_to(TaskStatus.CANCELLED):
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow()
            await self._emit_event(TaskEvent.TASK_CANCELLED, task)
            # 如果有运行中的任务，取消它
            if task_id in self._running_tasks:
                self._running_tasks[task_id].cancel()
            return True
        return False

    def get_task(self, task_id: str) -> Optional[TaskScheduler]:
        """获取任务"""
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> list[TaskScheduler]:
        """列出任务"""
        if status is None:
            return list(self._tasks.values())
        return [t for t in self._tasks.values() if t.status == status]

    async def _execute_task(
        self,
        task_id: str,
        callback: Callable[[dict], Awaitable[Any]]
    ) -> None:
        """执行任务（含重试逻辑）"""
        task = self._tasks.get(task_id)
        if not task:
            return

        task.status = TaskStatus.RUNNING
        task.actual_time = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        await self._emit_event(TaskEvent.TASK_STARTED, task)

        running_task = asyncio.current_task()
        self._running_tasks[task_id] = running_task

        start_time = datetime.utcnow()
        try:
            result = await callback(task.callback_params)
            end_time = datetime.utcnow()
            cost_time_ms = (end_time - start_time).total_seconds() * 1000
            task.result = TaskResult(success=True, output=str(result), retry_count=task.retry_times, cost_time_ms=cost_time_ms)
            task.status = TaskStatus.SUCCESS
            await self._emit_event(TaskEvent.TASK_COMPLETED, task)
        except asyncio.CancelledError:
            # 任务被取消，不视为失败
            task.status = TaskStatus.CANCELLED
            await self._emit_event(TaskEvent.TASK_CANCELLED, task)
        except Exception as e:
            end_time = datetime.utcnow()
            cost_time_ms = (end_time - start_time).total_seconds() * 1000
            task.error_message = str(e)
            if task.retry_times < task.max_retries:
                task.retry_times += 1
                task.status = TaskStatus.RETRY
                await self._emit_event(TaskEvent.TASK_RETRY, task, {"error": str(e), "retry": task.retry_times})
                await asyncio.sleep(2 ** task.retry_times)  # 指数退避
                asyncio.create_task(self._execute_task(task_id, callback))
            else:
                task.result = TaskResult(success=False, error=str(e), retry_count=task.retry_times, cost_time_ms=cost_time_ms)
                task.status = TaskStatus.FAILED
                await self._emit_event(TaskEvent.TASK_FAILED, task, {"error": str(e)})
        finally:
            task.updated_at = datetime.utcnow()
            self._running_tasks.pop(task_id, None)

    async def _delayed_execute(
        self,
        task_id: str,
        callback: Callable[[dict], Awaitable[Any]],
        delay_seconds: float
    ) -> None:
        """延迟执行（定时任务）"""
        await asyncio.sleep(delay_seconds)
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            await self._execute_task(task_id, callback)
