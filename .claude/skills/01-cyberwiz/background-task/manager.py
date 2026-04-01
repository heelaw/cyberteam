"""
后台任务管理器 - 核心模块
"""
import os
import json
import asyncio
import subprocess
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from storage import TaskStorage, get_storage


class ConcurrencyManager:
    """并发控制器"""

    def __init__(self, max_concurrency: int = 3):
        self.max_concurrency = max_concurrency
        self.queues: Dict[str, List[Callable]] = {}
        self.running: Dict[str, int] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    def get_lock(self, key: str) -> asyncio.Lock:
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        return self.locks[key]

    async def acquire(self, key: str) -> bool:
        """获取执行许可"""
        lock = self.get_lock(key)
        async with lock:
            current = self.running.get(key, 0)
            if current >= self.max_concurrency:
                return False
            self.running[key] = current + 1
            return True

    def release(self, key: str):
        """释放执行许可"""
        if key in self.running:
            self.running[key] = max(0, self.running[key] - 1)

    def get_running_count(self, key: str) -> int:
        """获取当前运行数"""
        return self.running.get(key, 0)


class BackgroundTaskManager:
    """后台任务管理器"""

    def __init__(self, storage: TaskStorage = None):
        self.storage = storage or get_storage()
        self.concurrency_manager = ConcurrencyManager(max_concurrency=3)
        self.pollers: Dict[str, threading.Thread] = {}
        self.callbacks: Dict[str, List[Callable]] = {}

    async def launch_task(
        self,
        description: str,
        prompt: str,
        agent: str = "cyberwiz",
        model: str = "sonnet",
        skills: List[str] = None,
        concurrency_key: str = None,
        parent_session_id: str = None
    ) -> Dict[str, Any]:
        """启动后台任务"""
        # 创建任务
        task = self.storage.create_task(
            description=description,
            prompt=prompt,
            agent=agent,
            model=model,
            skills=skills,
            concurrency_key=concurrency_key
        )

        task_id = task["task_id"]

        # 启动任务执行（异步）
        asyncio.create_task(self._execute_task(task_id))

        return {
            "task_id": task_id,
            "status": "pending",
            "description": description
        }

    async def _execute_task(self, task_id: str):
        """执行任务"""
        task = self.storage.get_task(task_id)
        if not task:
            return

        concurrency_key = task.get("concurrency_key", task["agent"])

        # 等待获取执行许可
        while True:
            if await self.concurrency_manager.acquire(concurrency_key):
                break
            await asyncio.sleep(1)

        try:
            # 更新状态为运行中
            self.storage.update_task(task_id, {
                "status": "running",
                "started_at": datetime.now().isoformat()
            })

            # 执行任务（使用 Claude Code 的 Task 工具）
            result = await self._run_with_claude(task)

            # 更新完成状态
            self.storage.update_task(task_id, {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "output": result.get("output"),
                "error": result.get("error")
            })

            # 触发回调
            self._trigger_callbacks(task_id, "completed", result)

        except Exception as e:
            # 更新失败状态
            self.storage.update_task(task_id, {
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error": str(e)
            })
            self._trigger_callbacks(task_id, "failed", {"error": str(e)})

        finally:
            self.concurrency_manager.release(concurrency_key)

    async def _run_with_claude(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Claude Code 执行任务"""
        # 构建任务提示
        prompt = task["prompt"]
        agent = task.get("agent", "cyberwiz")
        skills = task.get("skills", [])

        # 构建完整的提示
        full_prompt = f"""[{task['description']}]
{prompt}"""

        if skills:
            skill_names = ", ".join(skills)
            full_prompt = f"使用技能: {skill_names}\n\n{full_prompt}"

        try:
            # 使用 Task 工具创建后台任务
            # 这里通过调用 Claude Code 的 Task 工具来实现
            # 由于 Claude Code 的 Task 工具是同步的，我们需要特殊处理

            # 方案：使用 subprocess 调用 Claude Code
            cmd = [
                "claude",
                "-p",
                "--print",
                f"task: {agent}\n{full_prompt}"
            ]

            # 异步执行
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            )

            if process.returncode == 0:
                return {"output": process.stdout}
            else:
                return {"error": process.stderr}

        except asyncio.TimeoutError:
            return {"error": "任务执行超时"}
        except Exception as e:
            return {"error": str(e)}

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.storage.get_task(task_id)
        if task:
            return {
                "task_id": task["task_id"],
                "status": task["status"],
                "description": task["description"],
                "created_at": task["created_at"],
                "started_at": task.get("started_at"),
                "completed_at": task.get("completed_at"),
                "error": task.get("error")
            }
        return None

    def get_task_output(self, task_id: str) -> Optional[str]:
        """获取任务输出"""
        task = self.storage.get_task(task_id)
        if task and task.get("status") == "completed":
            return task.get("output")
        return None

    async def wait_for_task(self, task_id: str, timeout: int = 300000) -> Dict[str, Any]:
        """等待任务完成"""
        start_time = time.time()
        poll_interval = 2  # 初始轮询间隔

        while True:
            task = self.storage.get_task(task_id)
            if not task:
                return {"error": "任务不存在"}

            status = task["status"]
            if status in ["completed", "failed", "cancelled"]:
                return {
                    "task_id": task_id,
                    "status": status,
                    "output": task.get("output"),
                    "error": task.get("error")
                }

            # 检查超时
            elapsed = (time.time() - start_time) * 1000
            if elapsed > timeout:
                return {"error": "等待超时"}

            # 智能轮询间隔
            await asyncio.sleep(min(poll_interval, 30))
            poll_interval = min(poll_interval * 1.2, 30)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.storage.get_task(task_id)
        if task and task["status"] in ["pending", "running"]:
            self.storage.update_task(task_id, {
                "status": "cancelled",
                "completed_at": datetime.now().isoformat()
            })
            return True
        return False

    def list_tasks(self, filter_status: str = None) -> List[Dict[str, Any]]:
        """列出任务"""
        tasks = self.storage.list_tasks(filter_status)
        return [
            {
                "task_id": t["task_id"],
                "status": t["status"],
                "description": t["description"],
                "created_at": t["created_at"]
            }
            for t in tasks
        ]

    def register_callback(self, task_id: str, callback: Callable):
        """注册任务回调"""
        if task_id not in self.callbacks:
            self.callbacks[task_id] = []
        self.callbacks[task_id].append(callback)

    def _trigger_callbacks(self, task_id: str, event: str, data: Dict[str, Any]):
        """触发回调"""
        if task_id in self.callbacks:
            for callback in self.callbacks[task_id]:
                try:
                    callback(event, data)
                except Exception:
                    pass


# 全局管理器实例
_manager = None


def get_manager() -> BackgroundTaskManager:
    """获取全局管理器"""
    global _manager
    if _manager is None:
        _manager = BackgroundTaskManager()
    return _manager
