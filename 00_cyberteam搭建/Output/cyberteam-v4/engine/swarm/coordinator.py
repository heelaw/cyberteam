"""
SwarmCoordinator - 蜂群协调器

负责创建和管理Swarm实例，协调多个Agent协同工作
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime


class SwarmCoordinator:
    """Swarm协调器，负责蜂群式多Agent协同"""

    def __init__(self):
        self._swarms: dict[str, dict[str, Any]] = {}
        self._message_bus = None  # 延迟加载
        self._task_dag = None  # 延迟加载

    def _get_message_bus(self):
        """延迟加载MessageBus"""
        if self._message_bus is None:
            from .message_bus import MessageBus
            self._message_bus = MessageBus()
        return self._message_bus

    def _get_task_dag(self):
        """延迟加载TaskDAG"""
        if self._task_dag is None:
            from .task_dag import TaskDAG
            self._task_dag = TaskDAG()
        return self._task_dag

    def create_swarm(self, goal: str, template: str = "default") -> str:
        """
        创建一个新的Swarm实例

        Args:
            goal: Swarm目标描述
            template: 使用的模板类型

        Returns:
            swarm_id: 唯一标识符
        """
        swarm_id = f"swarm_{uuid.uuid4().hex[:8]}"
        self._swarms[swarm_id] = {
            "id": swarm_id,
            "goal": goal,
            "template": template,
            "agents": [],
            "tasks": [],
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "task_dag": self._get_task_dag(),
            "message_bus": self._get_message_bus(),
        }
        return swarm_id

    def add_agent(self, swarm_id: str, agent_type: str) -> str:
        """
        向Swarm添加一个Agent

        Args:
            swarm_id: Swarm标识
            agent_type: Agent类型

        Returns:
            agent_id: 分配的Agent ID
        """
        if swarm_id not in self._swarms:
            raise ValueError(f"Swarm {swarm_id} not found")

        agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        agent_info = {
            "id": agent_id,
            "type": agent_type,
            "status": "idle",
            "added_at": datetime.now().isoformat(),
        }
        self._swarms[swarm_id]["agents"].append(agent_info)
        return agent_id

    def delegate_task(self, swarm_id: str, task: dict) -> str:
        """
        向Swarm分配任务

        Args:
            swarm_id: Swarm标识
            task: 任务描述字典，包含:
                - task_id: 任务ID
                - description: 任务描述
                - assigned_to: 分配的Agent ID (可选)
                - deps: 依赖任务列表 (可选)

        Returns:
            task_id: 任务ID
        """
        if swarm_id not in self._swarms:
            raise ValueError(f"Swarm {swarm_id} not found")

        task_id = task.get("task_id") or f"task_{uuid.uuid4().hex[:8]}"
        task_info = {
            "task_id": task_id,
            "description": task.get("description", ""),
            "assigned_to": task.get("assigned_to"),
            "deps": task.get("deps", []),
            "status": "pending",
            "delegated_at": datetime.now().isoformat(),
        }

        # 添加到DAG
        dag = self._swarms[swarm_id]["task_dag"]
        dag.add_task(task_id, task_info["deps"])

        self._swarms[swarm_id]["tasks"].append(task_info)
        return task_id

    def monitor(self, swarm_id: str) -> dict:
        """
        监控Swarm状态

        Args:
            swarm_id: Swarm标识

        Returns:
            状态字典
        """
        if swarm_id not in self._swarms:
            raise ValueError(f"Swarm {swarm_id} not found")

        swarm = self._swarms[swarm_id]
        return {
            "id": swarm_id,
            "goal": swarm["goal"],
            "template": swarm["template"],
            "status": swarm["status"],
            "agent_count": len(swarm["agents"]),
            "task_count": len(swarm["tasks"]),
            "pending_tasks": sum(1 for t in swarm["tasks"] if t["status"] == "pending"),
            "running_tasks": sum(1 for t in swarm["tasks"] if t["status"] == "running"),
            "completed_tasks": sum(1 for t in swarm["tasks"] if t["status"] == "completed"),
            "created_at": swarm["created_at"],
        }

    def get_swarm(self, swarm_id: str) -> Optional[dict]:
        """获取Swarm详情"""
        return self._swarms.get(swarm_id)

    def list_swarms(self) -> list[dict]:
        """列出所有Swarm"""
        return [self.monitor(sid) for sid in self._swarms]

    def terminate_swarm(self, swarm_id: str) -> bool:
        """终止Swarm"""
        if swarm_id in self._swarms:
            self._swarms[swarm_id]["status"] = "terminated"
            return True
        return False