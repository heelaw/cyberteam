"""
任务客户端 - 提供统一的对外接口
"""
import asyncio
import json
from typing import Optional, Dict, Any, List

from manager import BackgroundTaskManager, get_manager
from storage import TaskStorage, get_storage


class BackgroundTaskClient:
    """后台任务客户端"""

    def __init__(self):
        self.manager = get_manager()
        self.storage = get_storage()

    async def launch(
        self,
        description: str,
        prompt: str,
        agent: str = "cyberwiz",
        model: str = "sonnet",
        skills: List[str] = None,
        concurrency_key: str = None
    ) -> Dict[str, Any]:
        """
        启动后台任务

        Args:
            description: 任务描述
            prompt: 任务指令
            agent: 使用的 Agent
            model: 模型选择
            skills: 技能列表
            concurrency_key: 并发控制键

        Returns:
            任务信息 dict
        """
        return await self.manager.launch_task(
            description=description,
            prompt=prompt,
            agent=agent,
            model=model,
            skills=skills,
            concurrency_key=concurrency_key
        )

    def status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        查询任务状态

        Args:
            task_id: 任务 ID

        Returns:
            状态信息 dict
        """
        return self.manager.get_task_status(task_id)

    async def wait(
        self,
        task_id: str,
        timeout: int = 300000
    ) -> Dict[str, Any]:
        """
        等待任务完成

        Args:
            task_id: 任务 ID
            timeout: 超时时间（毫秒）

        Returns:
            结果 dict
        """
        return await self.manager.wait_for_task(task_id, timeout)

    def output(self, task_id: str) -> Optional[str]:
        """
        获取任务输出

        Args:
            task_id: 任务 ID

        Returns:
            输出内容
        """
        return self.manager.get_task_output(task_id)

    def cancel(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务 ID

        Returns:
            是否成功
        """
        return self.manager.cancel_task(task_id)

    def list(self, filter_status: str = None) -> List[Dict[str, Any]]:
        """
        列出任务

        Args:
            filter_status: 状态过滤 (all/running/completed/failed)

        Returns:
            任务列表
        """
        if filter_status == "all":
            filter_status = None
        return self.manager.list_tasks(filter_status)

    def create_task_sync(
        self,
        description: str,
        prompt: str,
        agent: str = "cyberwiz",
        model: str = "sonnet",
        skills: List[str] = None,
        concurrency_key: str = None
    ) -> Dict[str, Any]:
        """
        同步方式创建任务（简化版）
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.launch(description, prompt, agent, model, skills, concurrency_key)
            )
        finally:
            loop.close()


# 全局客户端实例
_client = None


def get_client() -> BackgroundTaskClient:
    """获取全局客户端"""
    global _client
    if _client is None:
        _client = BackgroundTaskClient()
    return _client


# 便捷函数
def launch_task(**kwargs) -> Dict[str, Any]:
    """启动后台任务的便捷函数"""
    return get_client().create_task_sync(**kwargs)


def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """查询任务状态的便捷函数"""
    return get_client().status(task_id)


def wait_task(task_id: str, timeout: int = 300000) -> Dict[str, Any]:
    """等待任务完成的便捷函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_client().wait(task_id, timeout))
    finally:
        loop.close()


def get_task_output(task_id: str) -> Optional[str]:
    """获取任务输出的便捷函数"""
    return get_client().output(task_id)


def cancel_task(task_id: str) -> bool:
    """取消任务的便捷函数"""
    return get_client().cancel(task_id)


def list_tasks(filter_status: str = None) -> List[Dict[str, Any]]:
    """列出任务的便捷函数"""
    return get_client().list(filter_status)
