"""Redis Stream 任务队列 - 抄 Magic。

核心功能：
- 基于 Redis Stream 的分布式任务队列
- 支持任务优先级
- 支持延迟任务
- 支持任务分组和消费者组
- 完整的任务状态追踪

设计理念：
- 持久化：任务不会丢失
- 可靠：使用消费者组确保任务被处理
- 可扩展：多个消费者并行处理
- 可观测：完整的任务状态和历史
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging

log = logging.getLogger("cyberteam.queue")


class TaskStatus(str, Enum):
    """任务状态。"""
    PENDING = "pending"
    DELAYED = "delayed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务对象。"""

    id: str
    type: str
    payload: dict
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0  # 越大优先级越高
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "status": self.status.value,
            "priority": self.priority,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "result": self.result,
            "metadata": self.metadata,
            "retries": self.retries,
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典创建任务。"""
        return cls(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            status=TaskStatus(data.get("status", "pending")),
            priority=data.get("priority", 0),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error=data.get("error"),
            result=data.get("result"),
            metadata=data.get("metadata", {}),
            retries=data.get("retries", 0),
            max_retries=data.get("max_retries", 3),
        )


class TaskQueue:
    """Redis Stream 任务队列。

    用法:
        queue = TaskQueue()
        task_id = await queue.enqueue("agent.execute", {"agent_id": "xxx"})
        task = await queue.dequeue()  # 阻塞获取任务
        await queue.complete(task_id, result={"output": "yyy"})
    """

    STREAM_KEY = "cyberteam:tasks"
    CONSUMER_GROUP = "cyberteam-workers"
    CONSUMER_NAME_PREFIX = "worker"

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._redis = None
        self._use_memory_queue = False

    async def _get_redis(self):
        """获取 Redis 连接。"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self._redis_url, decode_responses=True)
                # 测试连接
                await self._redis.ping()
                log.info(f"Connected to Redis: {self._redis_url}")

                # 确保消费者组存在
                try:
                    await self._redis.xgroup_create(
                        self.STREAM_KEY,
                        self.CONSUMER_GROUP,
                        id="0",
                        mkstream=True,
                    )
                except Exception:
                    pass  # 消费者组已存在

            except Exception as e:
                log.warning(f"Redis not available, using memory queue: {e}")
                self._use_memory_queue = True
                self._memory_queue: List[Task] = []
                self._redis = None

        return self._redis

    async def enqueue(
        self,
        task_type: str,
        payload: dict,
        priority: int = 0,
        delay_seconds: int = 0,
        metadata: Optional[dict] = None,
    ) -> str:
        """入队一个任务。

        Args:
            task_type: 任务类型
            payload: 任务数据
            priority: 优先级
            delay_seconds: 延迟秒数
            metadata: 额外元数据

        Returns:
            任务 ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            type=task_type,
            payload=payload,
            priority=priority,
            metadata=metadata or {},
        )

        if delay_seconds > 0:
            task.status = TaskStatus.DELAYED
            from datetime import timedelta
            task.scheduled_at = datetime.utcnow() + timedelta(seconds=delay_seconds)

        redis = await self._get_redis()

        if self._use_memory_queue:
            self._memory_queue.append(task)
            log.info(f"Task enqueued (memory): {task_id} type={task_type}")
            return task_id

        # 使用 Redis Stream
        task_data = {
            "id": task_id,
            "type": task_type,
            "payload": json.dumps(payload),
            "status": task.status.value,
            "priority": str(priority),
            "data": json.dumps(task.to_dict()),
        }

        if delay_seconds > 0:
            from datetime import timedelta
            scheduled_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
            await self._redis.zadd(
                f"{self.STREAM_KEY}:delayed",
                {task_id: scheduled_at.timestamp()},
            )

        await self._redis.xadd(self.STREAM_KEY, task_data)

        log.info(f"Task enqueued: {task_id} type={task_type} priority={priority}")
        return task_id

    async def dequeue(self, timeout: int = 5) -> Optional[Task]:
        """出队一个任务（阻塞）。

        Args:
            timeout: 阻塞超时秒数

        Returns:
            Task 对象或 None
        """
        redis = await self._get_redis()

        if self._use_memory_queue:
            if self._memory_queue:
                task = self._memory_queue.pop(0)
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                return task
            return None

        # 使用 Redis Stream 消费者组
        consumer_name = f"{self.CONSUMER_NAME_PREFIX}:{uuid.uuid4()}"

        try:
            # 先检查延迟队列
            now = datetime.utcnow().timestamp()
            delayed = await redis.zrangebyscore(
                f"{self.STREAM_KEY}:delayed",
                min="-inf",
                max=now,
            )

            for task_id in delayed:
                # 将延迟任务移回主队列
                data = await redis.hget(f"{self.STREAM_KEY}:delayed:{task_id}", "data")
                if data:
                    task_dict = json.loads(data)
                    task = Task.from_dict(task_dict)
                    await redis.xadd(self.STREAM_KEY, {
                        "id": task.id,
                        "type": task.type,
                        "payload": json.dumps(task.payload),
                        "status": TaskStatus.PENDING.value,
                        "priority": str(task.priority),
                        "data": json.dumps(task.to_dict()),
                    })
                await redis.zrem(f"{self.STREAM_KEY}:delayed", task_id)

            # 读取新任务
            result = await redis.xreadgroup(
                self.CONSUMER_GROUP,
                consumer_name,
                {self.STREAM_KEY: ">"},
                count=1,
                block=timeout * 1000,
            )

            if not result:
                return None

            stream_name, messages = result[0]
            message_id, fields = messages[0]

            task_data = json.loads(fields["data"])
            task = Task.from_dict(task_data)
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()

            log.info(f"Task dequeued: {task.id} type={task.type}")
            return task

        except Exception as e:
            log.error(f"Dequeue error: {e}")
            return None

    async def complete(self, task_id: str, result: Any = None) -> None:
        """标记任务完成。"""
        redis = await self._get_redis()

        if self._use_memory_queue:
            for task in self._memory_queue:
                if task.id == task_id:
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
                    task.result = result
                    break
            return

        await redis.xadd(self.STREAM_KEY, {
            "id": task_id,
            "status": TaskStatus.COMPLETED.value,
            "result": json.dumps(result) if result else "null",
        })

        log.info(f"Task completed: {task_id}")

    async def fail(self, task_id: str, error: str) -> None:
        """标记任务失败。"""
        redis = await self._get_redis()

        if self._use_memory_queue:
            for task in self._memory_queue:
                if task.id == task_id:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.utcnow()
                    task.error = error
                    break
            return

        await redis.xadd(self.STREAM_KEY, {
            "id": task_id,
            "status": TaskStatus.FAILED.value,
            "error": error,
        })

        log.info(f"Task failed: {task_id} error={error}")

    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务详情。"""
        redis = await self._get_redis()

        if self._use_memory_queue:
            for task in self._memory_queue:
                if task.id == task_id:
                    return task
            return None

        # 从 Stream 中查找
        data = await redis.xrange(self.STREAM_KEY, "-", "+")
        for _, fields in data:
            if fields.get("id") == task_id:
                return Task.from_dict(json.loads(fields["data"]))

        return None

    async def get_queue_stats(self) -> dict:
        """获取队列统计。"""
        redis = await self._get_redis()

        if self._use_memory_queue:
            pending = sum(1 for t in self._memory_queue if t.status == TaskStatus.PENDING)
            running = sum(1 for t in self._memory_queue if t.status == TaskStatus.RUNNING)
            completed = sum(1 for t in self._memory_queue if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in self._memory_queue if t.status == TaskStatus.FAILED)

            return {
                "total": len(self._memory_queue),
                "pending": pending,
                "running": running,
                "completed": completed,
                "failed": failed,
            }

        try:
            info = await redis.xinfo_stream(self.STREAM_KEY)
            groups = await redis.xinfo_groups(self.STREAM_KEY)

            return {
                "stream_length": info.get("length", 0),
                "consumer_groups": len(groups),
                "pending": sum(g.get("pending", 0) for g in groups),
            }
        except Exception as e:
            return {"error": str(e)}


# 全局队列实例
_task_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """获取任务队列单例。"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue
