"""
任务存储模块 - 管理任务持久化
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class TaskStorage:
    """任务持久化存储"""

    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.claude/tasks/background")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"

    def _load_index(self) -> Dict[str, Any]:
        """加载任务索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"tasks": [], "last_updated": None}

    def _save_index(self, index: Dict[str, Any]):
        """保存任务索引"""
        index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def create_task(self, description: str, prompt: str, agent: str = "cyberwiz",
                   model: str = "sonnet", skills: List[str] = None,
                   concurrency_key: str = None) -> Dict[str, Any]:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "description": description,
            "prompt": prompt,
            "agent": agent,
            "model": model,
            "skills": skills or [],
            "concurrency_key": concurrency_key or agent,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "session_id": None,
            "output": None,
            "error": None
        }

        # 保存任务文件
        task_file = self.storage_dir / f"{task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)

        # 更新索引
        index = self._load_index()
        index["tasks"].append(task_id)
        self._save_index(index)

        return task

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务详情"""
        task_file = self.storage_dir / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新任务"""
        task = self.get_task(task_id)
        if task:
            task.update(updates)
            task["updated_at"] = datetime.now().isoformat()
            task_file = self.storage_dir / f"{task_id}.json"
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task, f, indent=2, ensure_ascii=False)
            return task
        return None

    def list_tasks(self, filter_status: str = None) -> List[Dict[str, Any]]:
        """列出所有任务"""
        index = self._load_index()
        tasks = []
        for task_id in index.get("tasks", []):
            task = self.get_task(task_id)
            if task:
                if filter_status is None or task.get("status") == filter_status:
                    tasks.append(task)
        # 按创建时间排序
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        task_file = self.storage_dir / f"{task_id}.json"
        if task_file.exists():
            task_file.unlink()
            index = self._load_index()
            index["tasks"] = [t for t in index.get("tasks", []) if t != task_id]
            self._save_index(index)
            return True
        return False

    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """按状态获取任务"""
        return self.list_tasks(filter_status=status)

    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """获取正在运行的任务"""
        return self.get_tasks_by_status("running")

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """获取等待中的任务"""
        return self.get_tasks_by_status("pending")


# 全局存储实例
_storage = None


def get_storage() -> TaskStorage:
    """获取全局存储实例"""
    global _storage
    if _storage is None:
        _storage = TaskStorage()
    return _storage
