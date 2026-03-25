"""
TaskDAG - 任务依赖图管理

基于有向无环图(DAG)的任务调度系统
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque


class TaskDAG:
    """任务依赖图管理器"""

    def __init__(self):
        # 任务节点: task_id -> {deps: [], status: str}
        self._tasks: Dict[str, dict] = {}
        # 拓扑排序缓存
        self._topo_order: Optional[List[str]] = None
        # 完成的任务
        self._completed: Set[str] = set()

    def add_task(self, task_id: str, deps: List[str] = None) -> None:
        """
        添加任务节点

        Args:
            task_id: 任务唯一标识
            deps: 依赖任务ID列表
        """
        if task_id in self._tasks:
            raise ValueError(f"Task {task_id} already exists")

        self._tasks[task_id] = {
            "deps": deps or [],
            "status": "pending",
        }
        # 使拓扑排序缓存失效
        self._topo_order = None

    def get_executable(self) -> List[str]:
        """
        获取可执行的任务列表（入度为0且未完成）

        Returns:
            可执行的任务ID列表
        """
        executable = []
        in_degree = self._compute_in_degree()

        for task_id, degree in in_degree.items():
            if degree == 0 and task_id not in self._completed:
                executable.append(task_id)

        return executable

    def _compute_in_degree(self) -> Dict[str, int]:
        """计算所有任务的入度"""
        in_degree = defaultdict(int)

        for task_id in self._tasks:
            in_degree[task_id] = 0

        for task_id, task_info in self._tasks.items():
            for dep in task_info["deps"]:
                if dep in in_degree:
                    in_degree[task_id] += 1

        return dict(in_degree)

    def get_topological_order(self) -> List[str]:
        """
        获取拓扑排序结果

        Returns:
            任务ID的有序列表
        """
        if self._topo_order is not None:
            return self._topo_order

        # Kahn算法
        in_degree = self._compute_in_degree()
        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            task_id = queue.popleft()
            result.append(task_id)

            for other_id, other_info in self._tasks.items():
                if task_id in other_info["deps"]:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        if len(result) != len(self._tasks):
            raise ValueError("Cycle detected in task DAG")

        self._topo_order = result
        return result

    def complete(self, task_id: str) -> None:
        """
        标记任务完成

        Args:
            task_id: 任务ID
        """
        if task_id not in self._tasks:
            raise ValueError(f"Task {task_id} not found")

        self._tasks[task_id]["status"] = "completed"
        self._completed.add(task_id)

    def is_complete(self) -> bool:
        """检查所有任务是否完成"""
        return len(self._completed) == len(self._tasks)

    def get_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        if task_id not in self._tasks:
            return None
        return self._tasks[task_id]["status"]

    def get_pending_tasks(self) -> List[str]:
        """获取待处理任务"""
        return [tid for tid, info in self._tasks.items()
                if info["status"] == "pending" and tid not in self._completed]

    def get_task_info(self, task_id: str) -> Optional[dict]:
        """获取任务详情"""
        return self._tasks.get(task_id)