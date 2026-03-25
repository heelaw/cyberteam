#!/usr/bin/env python3
"""
CyberTeam V4 - PM 协调引擎 (L2-执行层)

职责：
1. 接收并验证方案
2. 任务调度到 L3
3. 进度监控 (心跳机制)
4. 结果汇总
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ExecutionMode(Enum):
    SERIAL = "串行"
    PARALLEL = "并行"
    PIPELINE = "流水线"


@dataclass
class Task:
    """任务"""
    task_id: str
    title: str
    description: str
    department: str
    skills: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class DeptResult:
    """部门执行结果"""
    department: str
    status: str
    output: str = ""
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ExecutionResult:
    """执行结果"""
    status: str
    task_id: str
    outputs: Dict[str, DeptResult] = field(default_factory=dict)
    metrics: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration: float = 0.0


@dataclass
class HeartBeat:
    """心跳"""
    task_id: str
    timestamp: datetime
    status: str
    progress: float


class PMCoordinator:
    """PM 任务调度和进度监控引擎"""

    # 部门映射
    DEPARTMENT_EXECUTORS = {
        "数据分析部": "execute_data_analytics",
        "内容运营部": "execute_content_ops",
        "技术研发部": "execute_engineering",
        "安全合规部": "execute_security",
        "运维部署部": "execute_devops",
        "人力资源部": "execute_hr",
        "设计创意部": "execute_design",
        "商务拓展部": "execute_business",
        "战略规划部": "execute_strategy",
        "项目管理部": "execute_pm",
        "质量审核部": "execute_qa",
        "运营支持部": "execute_operations"
    }

    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.active_tasks: Dict[str, Task] = {}
        self.heartbeats: Dict[str, HeartBeat] = {}
        self.execution_history: List[ExecutionResult] = []

    def validate_plan(self, plan: dict) -> tuple[bool, Optional[str]]:
        """验证执行方案"""

        # 检查必要字段
        required_fields = ["task_id", "intent", "complexity"]
        for field in required_fields:
            if field not in plan:
                return False, f"缺少必要字段: {field}"

        # 检查资源
        if "resources" not in plan:
            return False, "缺少资源定义"

        return True, None

    def decompose_tasks(self, plan: dict) -> List[Task]:
        """将方案分解为可执行任务"""

        tasks = []
        departments = plan.get("resources", {}).get("departments", [])

        for i, dept in enumerate(departments):
            task = Task(
                task_id=f"{plan['task_id']}-D{i+1}",
                title=f"{plan['title']} - {dept}执行",
                description=plan.get("intent", ""),
                department=dept,
                skills=plan.get("resources", {}).get("skills", []),
                context=plan.get("context", {})
            )
            tasks.append(task)

        return tasks

    def schedule_tasks(
        self,
        tasks: List[Task],
        mode: ExecutionMode = ExecutionMode.PARALLEL
    ) -> List[dict]:
        """任务调度"""

        schedule = []

        if mode == ExecutionMode.PARALLEL:
            # 所有任务并行
            schedule.append({
                "phase": "并行执行",
                "tasks": [t.task_id for t in tasks],
                "departments": [t.department for t in tasks]
            })

        elif mode == ExecutionMode.SERIAL:
            # 串行执行
            for i, task in enumerate(tasks):
                schedule.append({
                    "phase": f"步骤 {i+1}",
                    "tasks": [task.task_id],
                    "departments": [task.department]
                })

        elif mode == ExecutionMode.PIPELINE:
            # 流水线模式 (按部门类型分组)
            phase_map = {}
            for task in tasks:
                if task.department not in phase_map:
                    phase_map[task.department] = []
                phase_map[task.department].append(task.task_id)

            for phase_name, task_ids in phase_map.items():
                schedule.append({
                    "phase": phase_name,
                    "tasks": task_ids,
                    "departments": [phase_name]
                })

        return schedule

    def monitor_heartbeat(self, task_id: str) -> HeartBeat:
        """监控心跳"""
        return self.heartbeats.get(task_id)

    def update_heartbeat(self, task_id: str, status: str, progress: float):
        """更新心跳"""
        self.heartbeats[task_id] = HeartBeat(
            task_id=task_id,
            timestamp=datetime.now(),
            status=status,
            progress=progress
        )

    def check_timeout(self, task_id: str) -> bool:
        """检查是否超时"""
        if task_id not in self.heartbeats:
            return False

        heartbeat = self.heartbeats[task_id]
        elapsed = (datetime.now() - heartbeat.timestamp).total_seconds()

        return elapsed > self.timeout

    async def execute_task(self, task: Task) -> DeptResult:
        """执行单个任务"""

        # 更新状态
        task.status = TaskStatus.IN_PROGRESS
        self.update_heartbeat(task.task_id, "执行中", 0.5)

        # 获取执行方法
        executor_method = self.DEPARTMENT_EXECUTORS.get(task.department)

        if not executor_method:
            return DeptResult(
                department=task.department,
                status="failure",
                errors=[f"未知部门: {task.department}"]
            )

        try:
            # 调用执行方法 (TODO: 实际执行)
            result = await self._dispatch_execution(task)

            # 更新状态
            task.status = TaskStatus.COMPLETED
            task.result = result
            self.update_heartbeat(task.task_id, "完成", 1.0)

            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.errors.append(str(e))

            return DeptResult(
                department=task.department,
                status="failure",
                errors=[str(e)]
            )

    async def _dispatch_execution(self, task: Task) -> DeptResult:
        """分发执行"""

        # TODO: 实际调用部门执行器或 Gstack/Agent
        # 这里模拟执行

        return DeptResult(
            department=task.department,
            status="success",
            output=f"{task.department} 执行完成",
            artifacts=[],
            metrics={
                "duration": 120,
                "token_usage": 5000
            }
        )

    async def execute_plan(self, plan: dict) -> ExecutionResult:
        """执行完整方案"""

        start_time = datetime.now()

        # 验证方案
        valid, error = self.validate_plan(plan)
        if not valid:
            return ExecutionResult(
                status="failure",
                task_id=plan.get("task_id", "unknown"),
                errors=[error]
            )

        # 分解任务
        tasks = self.decompose_tasks(plan)

        # 调度任务
        mode = ExecutionMode.PARALLEL if plan.get("complexity") == "高" else ExecutionMode.SERIAL
        schedule = self.schedule_tasks(tasks, mode)

        # 执行任务
        outputs = {}
        all_errors = []

        for phase in schedule:
            # 执行该阶段的所有任务
            phase_tasks = [t for t in tasks if t.task_id in phase["tasks"]]

            for task in phase_tasks:
                result = await self.execute_task(task)
                outputs[task.task_id] = result

                if result.status == "failure":
                    all_errors.extend(result.errors)

        # 计算耗时
        duration = (datetime.now() - start_time).total_seconds()

        # 构建结果
        execution_result = ExecutionResult(
            status="failure" if all_errors else "success",
            task_id=plan.get("task_id", "unknown"),
            outputs=outputs,
            metrics={
                "duration": duration,
                "task_count": len(tasks),
                "success_count": sum(1 for r in outputs.values() if r.status == "success"),
                "error_count": len(all_errors)
            },
            errors=all_errors,
            duration=duration
        )

        # 记录历史
        self.execution_history.append(execution_result)

        return execution_result

    def aggregate_results(self, results: Dict[str, DeptResult]) -> dict:
        """聚合结果"""

        aggregated = {
            "summary": {
                "total": len(results),
                "success": sum(1 for r in results.values() if r.status == "success"),
                "failed": sum(1 for r in results.values() if r.status == "failure")
            },
            "outputs": {},
            "artifacts": [],
            "metrics": {
                "total_duration": 0,
                "total_tokens": 0
            }
        }

        for task_id, result in results.items():
            aggregated["outputs"][result.department] = result.output
            aggregated["artifacts"].extend(result.artifacts)
            aggregated["metrics"]["total_duration"] += result.metrics.get("duration", 0)
            aggregated["metrics"]["total_tokens"] += result.metrics.get("token_usage", 0)

        return aggregated


def main():
    """CLI 测试"""
    import sys

    coordinator = PMCoordinator()

    # 测试数据
    plan = {
        "task_id": "TEST-001",
        "title": "测试任务",
        "intent": "数据分析",
        "complexity": "高",
        "resources": {
            "departments": ["数据分析部", "内容运营部"],
            "skills": ["/aarrr-growth-model"],
            "agents": ["gsd-executor"]
        }
    }

    print("\n" + "=" * 50)
    print("PM 协调引擎")
    print("=" * 50)

    # 验证方案
    valid, error = coordinator.validate_plan(plan)
    print(f"\n方案验证: {'通过' if valid else f'失败 - {error}'}")

    # 分解任务
    tasks = coordinator.decompose_tasks(plan)
    print(f"\n任务分解: {len(tasks)} 个任务")
    for task in tasks:
        print(f"  - {task.task_id}: {task.department}")

    # 调度任务
    schedule = coordinator.schedule_tasks(tasks, ExecutionMode.PARALLEL)
    print(f"\n执行调度:")
    for phase in schedule:
        print(f"  【{phase['phase']}】")
        print(f"    部门: {phase['departments']}")


if __name__ == "__main__":
    main()
