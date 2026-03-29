"""
Progress View - 全局进度视图
提供跨Agent的任务进度可视化和瓶颈识别
"""

from typing import List, Dict, Optional
from datetime import datetime


class TaskState:
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressView:
    """全局进度视图"""

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}

    def generate(self, all_tasks: List[Dict]) -> Dict:
        """
        生成全局进度视图

        Args:
            all_tasks: 所有任务列表

        Returns:
            Dict - 进度视图数据
        """
        if not all_tasks:
            return {
                "total_tasks": 0,
                "overall_progress": 0.0,
                "by_state": {},
                "by_agent": {},
                "timeline": []
            }

        # 统计各状态任务数
        by_state = {}
        for task in all_tasks:
            state = task.get("state", TaskState.PENDING)
            by_state[state] = by_state.get(state, 0) + 1

        # 统计各Agent任务数
        by_agent = {}
        for task in all_tasks:
            agent = task.get("assigned_agent", "unassigned")
            if agent not in by_agent:
                by_agent[agent] = {"total": 0, "completed": 0, "in_progress": 0, "blocked": 0}
            by_agent[agent]["total"] += 1
            state = task.get("state", TaskState.PENDING)
            if state == TaskState.COMPLETED:
                by_agent[agent]["completed"] += 1
            elif state == TaskState.IN_PROGRESS:
                by_agent[agent]["in_progress"] += 1
            elif state == TaskState.BLOCKED:
                by_agent[agent]["blocked"] += 1

        # 计算总体进度
        completed = by_state.get(TaskState.COMPLETED, 0)
        total = len(all_tasks)
        overall_progress = (completed / total * 100) if total > 0 else 0.0

        # 生成时间线
        timeline = self._generate_timeline(all_tasks)

        return {
            "total_tasks": total,
            "overall_progress": round(overall_progress, 2),
            "by_state": by_state,
            "by_agent": by_agent,
            "timeline": timeline,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_timeline(self, tasks: List[Dict]) -> List[Dict]:
        """生成任务时间线"""
        timeline = []
        for task in tasks:
            timeline.append({
                "task_id": task.get("id"),
                "name": task.get("name", "Unknown"),
                "state": task.get("state", TaskState.PENDING),
                "start_time": task.get("start_time"),
                "end_time": task.get("end_time"),
                "duration": task.get("duration_seconds")
            })
        return timeline

    def identify_bottlenecks(self, tasks: List[Dict]) -> List[Dict]:
        """
        识别瓶颈任务

        Args:
            tasks: 任务列表

        Returns:
            List[Dict] - 瓶颈列表
        """
        bottlenecks = []

        # 识别阻塞任务
        blocked_tasks = [t for t in tasks if t.get("state") == TaskState.BLOCKED]
        for task in blocked_tasks:
            bottlenecks.append({
                "type": "blocked_task",
                "task_id": task.get("id"),
                "task_name": task.get("name"),
                "reason": task.get("block_reason", "unknown"),
                "waiting_for": task.get("waiting_for"),
                "severity": "high"
            })

        # 识别长期运行任务
        long_running_threshold = 300  # 5分钟
        now = datetime.now()
        for task in tasks:
            if task.get("state") == TaskState.IN_PROGRESS:
                start_time = task.get("start_time")
                if start_time:
                    try:
                        if isinstance(start_time, str):
                            start = datetime.fromisoformat(start_time)
                        else:
                            start = start_time
                        duration = (now - start).total_seconds()
                        if duration > long_running_threshold:
                            bottlenecks.append({
                                "type": "long_running",
                                "task_id": task.get("id"),
                                "task_name": task.get("name"),
                                "duration_seconds": duration,
                                "severity": "medium" if duration < 600 else "high"
                            })
                    except (ValueError, TypeError):
                        pass

        # 识别重复失败任务
        failed_tasks = [t for t in tasks if t.get("state") == TaskState.FAILED]
        failure_count = {}
        for task in failed_tasks:
            error = task.get("error", "unknown")
            failure_count[error] = failure_count.get(error, 0) + 1

        for error, count in failure_count.items():
            if count >= 3:
                bottlenecks.append({
                    "type": "repeated_failures",
                    "error": error,
                    "failure_count": count,
                    "severity": "high" if count >= 5 else "medium"
                })

        # 识别资源紧张（任务过多）
        agent_load = {}
        for task in tasks:
            if task.get("state") in [TaskState.IN_PROGRESS, TaskState.PENDING]:
                agent = task.get("assigned_agent", "unassigned")
                agent_load[agent] = agent_load.get(agent, 0) + 1

        for agent, load in agent_load.items():
            if load >= 5:
                bottlenecks.append({
                    "type": "agent_overload",
                    "agent": agent,
                    "pending_tasks": load,
                    "severity": "high" if load >= 8 else "medium"
                })

        return bottlenecks

    def calculate_eta(self, tasks: List[Dict]) -> Optional[float]:
        """
        计算预计完成时间（小时）

        Args:
            tasks: 任务列表

        Returns:
            Optional[float] - 预计完成时间（小时），如果无法计算则返回None
        """
        pending = [t for t in tasks if t.get("state") in [TaskState.PENDING, TaskState.IN_PROGRESS]]
        completed = [t for t in tasks if t.get("state") == TaskState.COMPLETED]

        if not pending:
            return 0.0 if completed else None

        # 计算已完成任务的平均耗时
        completed_with_duration = [t for t in completed if t.get("duration_seconds")]
        if not completed_with_duration:
            return None

        avg_duration = sum(t["duration_seconds"] for t in completed_with_duration) / len(completed_with_duration)

        # 估算剩余任务时间
        remaining_tasks = len(pending)
        estimated_remaining_hours = (avg_duration * remaining_tasks) / 3600

        return round(estimated_remaining_hours, 2)