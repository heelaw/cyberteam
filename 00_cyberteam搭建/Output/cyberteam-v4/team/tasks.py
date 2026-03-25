#!/usr/bin/env python3
"""
CyberTeam V4 - Task 任务系统
实现任务依赖链 + 自动解除阻塞
"""

import json
import uuid
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Callable

from .models import TaskItem, TaskStatus


# 默认任务存储路径
DEFAULT_TASK_DIR = Path.home() / ".cyberteam" / "tasks"


class TaskLockError(Exception):
    """任务锁异常"""
    pass


class TaskNotFoundError(Exception):
    """任务不存在"""
    pass


class TaskStore:
    """任务存储 (带依赖链)"""

    def __init__(self, team_name: str, task_dir: Optional[Path] = None):
        self.team_name = team_name
        self.task_dir = task_dir or DEFAULT_TASK_DIR / team_name
        self.task_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = self.task_dir / ".tasks.lock"
        self._lock = threading.Lock()

        # 内存缓存
        self._tasks: Dict[str, TaskItem] = {}
        self._load_all()

    def _load_all(self) -> None:
        """加载所有任务"""
        for task_file in self.task_dir.glob("task-*.json"):
            try:
                data = json.loads(task_file.read_text())
                task = TaskItem.from_dict(data)
                self._tasks[task.task_id] = task
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self, task: TaskItem) -> None:
        """保存任务到文件"""
        task_file = self.task_dir / f"task-{task.task_id}.json"
        task_file.write_text(json.dumps(task.to_dict(), indent=2, ensure_ascii=False))

    def _acquire_lock(self, task: TaskItem, caller: str, force: bool = False) -> None:
        """获取任务锁"""
        if task.locked_by and task.locked_by != caller:
            raise TaskLockError(
                f"Task {task.task_id} is locked by {task.locked_by}"
            )
        task.locked_by = caller

    def _release_lock(self, task: TaskItem) -> None:
        """释放任务锁"""
        task.locked_by = None

    def create(
        self,
        subject: str,
        description: str = "",
        owner: Optional[str] = None,
        blocked_by: Optional[List[str]] = None
    ) -> TaskItem:
        """
        创建任务

        Args:
            subject: 任务主题
            description: 任务描述
            owner: 负责人
            blocked_by: 依赖的任务 IDs

        Returns:
            TaskItem
        """
        with self._lock:
            task_id = str(uuid.uuid4())[:8].upper()

            task = TaskItem(
                task_id=task_id,
                subject=subject,
                description=description,
                owner=owner,
                blocked_by=blocked_by or [],
                status=TaskStatus.PENDING
            )

            # 如果有依赖，自动设置为 blocked
            if task.blocked_by:
                task.status = TaskStatus.BLOCKED

            self._tasks[task_id] = task
            self._save(task)

            return task

    def get(self, task_id: str) -> Optional[TaskItem]:
        """获取任务"""
        return self._tasks.get(task_id)

    def update(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        owner: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
        force: bool = False
    ) -> TaskItem:
        """
        更新任务状态

        Args:
            task_id: 任务 ID
            status: 新状态
            owner: 负责人
            result: 执行结果
            error: 错误信息
            force: 是否强制更新

        Returns:
            TaskItem
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task not found: {task_id}")

            if status:
                old_status = task.status
                task.status = status

                # 状态变更处理
                if status == TaskStatus.IN_PROGRESS:
                    self._acquire_lock(task, owner or "unknown", force=force)
                elif status == TaskStatus.COMPLETED:
                    self._release_lock(task)
                    task.completed_at = task.updated_at
                    # 关键: 解除依赖任务的阻塞
                    self._resolve_dependents_unlocked(task_id)
                elif status == TaskStatus.FAILED:
                    self._release_lock(task)

            if owner:
                task.owner = owner
            if result is not None:
                task.result = result
            if error is not None:
                task.error = error

            task.updated_at = task.updated_at  # 简化，实际应该更新

            self._save(task)
            return task

    def _resolve_dependents_unlocked(self, completed_task_id: str) -> None:
        """
        解除依赖此任务的其他任务的阻塞
        (必须在持有 _lock 的情况下调用)
        """
        for task in self._tasks.values():
            if completed_task_id in task.blocked_by:
                task.blocked_by.remove(completed_task_id)

                # 如果不再被阻塞，且原状态是 blocked → 改为 pending
                if not task.blocked_by and task.status == TaskStatus.BLOCKED:
                    task.status = TaskStatus.PENDING
                    self._save(task)

    def delete(self, task_id: str) -> bool:
        """删除任务"""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks.pop(task_id)

                # 删除文件
                task_file = self.task_dir / f"task-{task_id}.json"
                if task_file.exists():
                    task_file.unlink()

                # 清理其他任务的 blocked_by
                for t in self._tasks.values():
                    if task_id in t.blocked_by:
                        t.blocked_by.remove(task_id)
                        self._save(t)

                return True
            return False

    def list_all(self) -> List[TaskItem]:
        """列出所有任务"""
        return list(self._tasks.values())

    def list_by_status(self, status: TaskStatus) -> List[TaskItem]:
        """按状态列出任务"""
        return [t for t in self._tasks.values() if t.status == status]

    def list_by_owner(self, owner: str) -> List[TaskItem]:
        """按负责人列出任务"""
        return [t for t in self._tasks.values() if t.owner == owner]

    def list_pending(self) -> List[TaskItem]:
        """列出待处理任务"""
        return self.list_by_status(TaskStatus.PENDING)

    def list_blocked(self) -> List[TaskItem]:
        """列出被阻塞的任务"""
        return self.list_by_status(TaskStatus.BLOCKED)

    def list_in_progress(self) -> List[TaskItem]:
        """列出进行中的任务"""
        return self.list_by_status(TaskStatus.IN_PROGRESS)

    def list_completed(self) -> List[TaskItem]:
        """列出已完成任务"""
        return self.list_by_status(TaskStatus.COMPLETED)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        tasks = list(self._tasks.values())
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
            "blocked": len([t for t in tasks if t.status == TaskStatus.BLOCKED]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in tasks if t.status == TaskStatus.FAILED]),
        }

    def resolve_dependencies(self, task_ids: List[str]) -> List[List[str]]:
        """
        解析依赖，返回分组执行顺序

        Returns:
            [[task_id_1, task_id_2], [task_id_3], ...]
            可以并行执行的任务在同一组
        """
        # 构建依赖图
        task_map = {tid: self._tasks[tid] for tid in task_ids if tid in self._tasks}

        # 拓扑排序 + 分层
        resolved = []
        remaining = set(task_ids)

        while remaining:
            # 找出所有没有被依赖的任务
            ready = []
            for tid in remaining:
                task = task_map[tid]
                # 检查是否所有依赖都已完成
                deps_done = all(
                    self._tasks[d].status == TaskStatus.COMPLETED
                    for d in task.blocked_by
                    if d in self._tasks
                )
                if deps_done:
                    ready.append(tid)

            if not ready:
                # 死锁 - 还有任务但没有可以执行的
                break

            resolved.append(ready)
            for tid in ready:
                remaining.remove(tid)

        return resolved


def main():
    """测试"""
    print("Task Store 测试")
    print("=" * 50)

    store = TaskStore("test-team")

    # 创建任务
    t1 = store.create("任务1", owner="agent-a")
    print(f"创建任务1: {t1.task_id}")

    t2 = store.create("任务2", owner="agent-b")
    print(f"创建任务2: {t2.task_id}")

    t3 = store.create("任务3", owner="agent-c", blocked_by=[t1.task_id, t2.task_id])
    print(f"创建任务3 (依赖任务1,2): {t3.task_id}")

    # 统计
    print(f"\n统计: {store.get_stats()}")

    # 完成任务1
    print(f"\n完成任务1...")
    store.update(t1.task_id, status=TaskStatus.COMPLETED)

    # 检查任务3状态
    t3_updated = store.get(t3.task_id)
    print(f"任务3状态: {t3_updated.status.value}")
    print(f"任务3 blocked_by: {t3_updated.blocked_by}")

    # 完成任务2
    print(f"\n完成任务2...")
    store.update(t2.task_id, status=TaskStatus.COMPLETED)

    # 再次检查任务3状态
    t3_updated = store.get(t3.task_id)
    print(f"任务3状态: {t3_updated.status.value} (应该变为 pending)")


if __name__ == "__main__":
    main()
