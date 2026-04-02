#!/usr/bin/env python3
"""
CyberTeam V4 - PM 执行器模块 (L2-执行层)

职责：
1. TaskDecomposer - 任务拆解
2. ProgressTracker - 进度跟踪
3. ResultAcceptor - 结果验收
4. PMExecutor - PM执行器主类
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Callable, Any
from datetime import datetime
import uuid
import threading
import time


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


class Priority(Enum):
    """优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    title: str
    description: str
    assigned_to: Optional[str] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    result: Optional[dict] = None
    feedback: Optional[str] = None


class TaskDecomposer:
    """任务拆解器"""

    # 复杂度系数
    COMPLEXITY_FACTORS = {
        "simple": 1.0,
        "medium": 2.5,
        "complex": 5.0,
        "very_complex": 10.0
    }

    # 部门技能映射
    DEPARTMENT_SKILLS = {
        "数据分析部": ["data_analysis", "statistics", "visualization"],
        "内容运营部": ["content_creation", "copywriting", "social_media"],
        "技术研发部": ["coding", "architecture", "testing"],
        "安全合规部": ["security_audit", "compliance", "risk_assessment"],
        "运维部署部": ["devops", "monitoring", "infrastructure"],
        "人力资源部": ["recruitment", "training", "performance"],
        "设计创意部": ["ui_design", "ux_research", "branding"],
        "商务拓展部": ["sales", "partnerships", "negotiation"],
        "战略规划部": ["strategy", "planning", "analysis"],
        "项目管理部": ["project_management", "coordination", "reporting"],
        "质量审核部": ["qa", "testing", "validation"],
        "运营支持部": ["operations", "support", "process"]
    }

    def decompose(self, task: dict) -> list[SubTask]:
        """
        将任务拆解为子任务

        Args:
            task: 原始任务字典，包含:
                - title: 任务标题
                - description: 任务描述
                - department: 负责部门
                - complexity: 复杂度 (simple/medium/complex/very_complex)
                - constraints: 约束条件 (可选)

        Returns:
            子任务列表
        """
        subtasks = []
        task_id = task.get("task_id", str(uuid.uuid4())[:8])
        title = task.get("title", "未命名任务")
        description = task.get("description", "")
        department = task.get("department", "技术研发部")
        complexity = task.get("complexity", "medium")

        # 根据复杂度决定拆解深度
        depth = self.COMPLEXITY_FACTORS.get(complexity, 2.5)

        # 基础子任务
        subtask_specs = self._generate_subtask_specs(
            task_id, title, description, department, complexity
        )

        for spec in subtask_specs:
            subtask = SubTask(
                task_id=spec["task_id"],
                title=spec["title"],
                description=spec["description"],
                estimated_hours=spec.get("estimated_hours", depth),
                dependencies=spec.get("dependencies", [])
            )
            subtasks.append(subtask)

        return subtasks

    def _generate_subtask_specs(
        self,
        task_id: str,
        title: str,
        description: str,
        department: str,
        complexity: str
    ) -> list[dict]:
        """生成子任务规格"""

        specs = []

        # 阶段1: 分析规划
        specs.append({
            "task_id": f"{task_id}-P1",
            "title": f"{title} - 需求分析",
            "description": f"分析任务需求，制定执行方案: {description}",
            "estimated_hours": 1.0,
            "dependencies": []
        })

        # 阶段2: 执行实施
        if complexity in ["complex", "very_complex"]:
            # 复杂任务拆分为多个执行子任务
            specs.append({
                "task_id": f"{task_id}-P2A",
                "title": f"{title} - 核心实现",
                "description": f"执行核心功能: {description}",
                "estimated_hours": 4.0,
                "dependencies": [f"{task_id}-P1"]
            })
            specs.append({
                "task_id": f"{task_id}-P2B",
                "title": f"{title} - 辅助模块",
                "description": f"实现辅助模块: {description}",
                "estimated_hours": 2.0,
                "dependencies": [f"{task_id}-P1"]
            })
        else:
            specs.append({
                "task_id": f"{task_id}-P2",
                "title": f"{title} - 执行实施",
                "description": f"执行任务: {description}",
                "estimated_hours": 2.0 * self.COMPLEXITY_FACTORS.get(complexity, 2.5),
                "dependencies": [f"{task_id}-P1"]
            })

        # 阶段3: 验证测试
        specs.append({
            "task_id": f"{task_id}-P3",
            "title": f"{title} - 质量验证",
            "description": "验证执行结果，确保符合预期",
            "estimated_hours": 1.0,
            "dependencies": [f"{task_id}-P2"] if complexity in ["simple", "medium"]
                           else [f"{task_id}-P2A", f"{task_id}-P2B"]
        })

        # 阶段4: 交付部署
        specs.append({
            "task_id": f"{task_id}-P4",
            "title": f"{title} - 交付完成",
            "description": "整理产出，交付最终成果",
            "estimated_hours": 0.5,
            "dependencies": [f"{task_id}-P3"]
        })

        return specs

    def estimate_effort(self, subtask: dict) -> float:
        """
        估算子任务工作量

        Args:
            subtask: 子任务字典

        Returns:
            估算小时数
        """
        base_hours = subtask.get("estimated_hours", 2.0)

        # 技能匹配度调整
        department = subtask.get("department", "")
        required_skills = subtask.get("required_skills", [])
        available_skills = self.DEPARTMENT_SKILLS.get(department, [])

        skill_match = len(set(required_skills) & set(available_skills))
        skill_factor = 0.5 + (skill_match * 0.25)  # 0.5 ~ 1.25

        # 依赖调整
        dependency_factor = 1.0 + (len(subtask.get("dependencies", [])) * 0.1)

        # 优先级调整
        priority = subtask.get("priority", Priority.MEDIUM.name)
        priority_factor = {
            Priority.LOW.name: 0.8,
            Priority.MEDIUM.name: 1.0,
            Priority.HIGH.name: 1.2,
            Priority.CRITICAL.name: 1.5
        }.get(priority, 1.0)

        total_hours = base_hours * skill_factor * dependency_factor * priority_factor

        return round(total_hours, 2)

    def identify_dependencies(self, tasks: list[dict]) -> dict[str, list[str]]:
        """
        识别任务间的依赖关系

        Args:
            tasks: 任务列表

        Returns:
            依赖图字典 {task_id: [依赖的task_id列表]}
        """
        dependency_graph = {}

        for task in tasks:
            task_id = task.get("task_id")
            if not task_id:
                continue

            # 显式依赖
            explicit_deps = task.get("dependencies", [])

            # 隐式依赖检测（基于任务描述和类型）
            implicit_deps = self._detect_implicit_dependencies(task, tasks)

            # 合并依赖
            all_deps = list(set(explicit_deps + implicit_deps))
            dependency_graph[task_id] = all_deps

        return dependency_graph

    def _detect_implicit_dependencies(
        self,
        task: dict,
        all_tasks: list
    ) -> list[str]:
        """检测隐式依赖"""

        implicit_deps = []
        task_type = task.get("type", "")
        task_department = task.get("department", "")

        # 前置阶段依赖
        if "P2" in task.get("task_id", ""):
            # P2任务依赖P1
            base_id = task.get("task_id", "").split("-")[0]
            implicit_deps.append(f"{base_id}-P1")

        if "P3" in task.get("task_id", ""):
            # P3依赖P2
            base_id = task.get("task_id", "").split("-")[0]
            if task.get("complexity") in ["complex", "very_complex"]:
                implicit_deps.extend([f"{base_id}-P2A", f"{base_id}-P2B"])
            else:
                implicit_deps.append(f"{base_id}-P2")

        # 部门间隐式依赖
        department_order = [
            "战略规划部", "数据分析部", "技术研发部",
            "设计创意部", "内容运营部", "运维部署部"
        ]

        try:
            current_idx = department_order.index(task_department)
            for dept in department_order[:current_idx]:
                # 查找同任务的其他部门前置任务
                for other_task in all_tasks:
                    if other_task.get("department") == dept and other_task.get("task_id"):
                        implicit_deps.append(other_task.get("task_id"))
        except ValueError:
            pass

        return implicit_deps


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self):
        self._lock = threading.Lock()
        self._task_progress: dict[str, dict[str, Any]] = {}
        self._global_metrics: dict[str, Any] = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "blocked_tasks": 0,
            "in_progress_tasks": 0,
            "total_effort_hours": 0.0,
            "actual_effort_hours": 0.0
        }
        self._subscribers: list[Callable] = []

    def track(self, task_id: str, progress: float, metadata: Optional[dict] = None):
        """
        跟踪任务进度

        Args:
            task_id: 任务ID
            progress: 进度百分比 (0.0 ~ 1.0)
            metadata: 额外元数据
        """
        with self._lock:
            if task_id not in self._task_progress:
                self._task_progress[task_id] = {
                    "task_id": task_id,
                    "progress": 0.0,
                    "status": "pending",
                    "started_at": None,
                    "updated_at": None,
                    "history": []
                }
                self._global_metrics["total_tasks"] += 1

            entry = self._task_progress[task_id]
            old_progress = entry["progress"]

            # 更新进度
            entry["progress"] = max(0.0, min(1.0, progress))
            entry["updated_at"] = datetime.now()

            # 更新状态
            if progress >= 1.0:
                entry["status"] = "completed"
            elif progress > 0:
                if entry["status"] == "pending":
                    entry["status"] = "in_progress"
                    entry["started_at"] = datetime.now()
            elif progress < 0:
                entry["status"] = "blocked"

            # 记录历史
            entry["history"].append({
                "timestamp": datetime.now(),
                "progress": progress,
                "delta": progress - old_progress
            })

            # 合并元数据
            if metadata:
                entry.update(metadata)

            # 更新全局指标
            self._recalculate_metrics()

            # 通知订阅者
            self._notify_subscribers(task_id, entry)

    def _recalculate_metrics(self):
        """重新计算全局指标"""
        metrics = self._global_metrics

        metrics["completed_tasks"] = sum(
            1 for t in self._task_progress.values()
            if t["status"] == "completed"
        )
        metrics["failed_tasks"] = sum(
            1 for t in self._task_progress.values()
            if t["status"] == "failed"
        )
        metrics["blocked_tasks"] = sum(
            1 for t in self._task_progress.values()
            if t["status"] == "blocked"
        )
        metrics["in_progress_tasks"] = sum(
            1 for t in self._task_progress.values()
            if t["status"] == "in_progress"
        )

        metrics["actual_effort_hours"] = sum(
            t.get("effort_hours", 0.0)
            for t in self._task_progress.values()
        )

    def get_status(self, task_id: str) -> dict:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态字典
        """
        with self._lock:
            if task_id not in self._task_progress:
                return {
                    "task_id": task_id,
                    "status": "unknown",
                    "progress": 0.0,
                    "error": "任务未找到"
                }

            entry = self._task_progress[task_id].copy()

            # 计算趋势
            history = entry.get("history", [])
            if len(history) >= 2:
                recent = history[-3:]
                avg_delta = sum(h["delta"] for h in recent) / len(recent)
                entry["trend"] = "accelerating" if avg_delta > 0.01 else "stable"
                if avg_delta < 0:
                    entry["trend"] = "decelerating"
            else:
                entry["trend"] = "unknown"

            return entry

    def get_global_view(self) -> dict:
        """
        获取全局视图

        Returns:
            全局状态字典
        """
        with self._lock:
            completion_rate = 0.0
            if self._global_metrics["total_tasks"] > 0:
                completion_rate = (
                    self._global_metrics["completed_tasks"] /
                    self._global_metrics["total_tasks"]
                )

            return {
                "global_progress": completion_rate,
                "metrics": self._global_metrics.copy(),
                "tasks": {
                    task_id: {
                        "progress": t["progress"],
                        "status": t["status"]
                    }
                    for task_id, t in self._task_progress.items()
                },
                "timestamp": datetime.now().isoformat()
            }

    def subscribe(self, callback: Callable):
        """订阅进度更新"""
        self._subscribers.append(callback)

    def _notify_subscribers(self, task_id: str, entry: dict):
        """通知订阅者"""
        for callback in self._subscribers:
            try:
                callback(task_id, entry)
            except Exception:
                pass


class ResultAcceptor:
    """结果验收器"""

    def __init__(self):
        self._lock = threading.Lock()
        self._results: dict[str, dict] = {}
        self._revisions: dict[str, list[dict]] = {}

    def accept(self, task_id: str, result: dict) -> bool:
        """
        验收通过

        Args:
            task_id: 任务ID
            result: 结果字典，包含:
                - output: 输出内容
                - artifacts: 产出物列表
                - metrics: 指标数据

        Returns:
            是否验收通过
        """
        with self._lock:
            # 验证结果格式
            if not self._validate_result(result):
                return False

            self._results[task_id] = {
                "task_id": task_id,
                "status": "accepted",
                "result": result,
                "accepted_at": datetime.now(),
                "revisions": self._revisions.get(task_id, [])
            }

            return True

    def _validate_result(self, result: dict) -> bool:
        """验证结果格式"""
        required_fields = ["output"]

        for field in required_fields:
            if field not in result:
                return False

        return True

    def reject(self, task_id: str, reason: str):
        """
        验收拒绝

        Args:
            task_id: 任务ID
            reason: 拒绝原因
        """
        with self._lock:
            if task_id not in self._results:
                self._results[task_id] = {
                    "task_id": task_id,
                    "status": "pending",
                    "result": None
                }

            self._results[task_id]["status"] = "rejected"
            self._results[task_id]["rejected_reason"] = reason
            self._results[task_id]["rejected_at"] = datetime.now()

    def request_revision(
        self,
        task_id: str,
        feedback: str,
        required_changes: Optional[list[str]] = None
    ):
        """
        请求修订

        Args:
            task_id: 任务ID
            feedback: 反馈意见
            required_changes: 必需修改项列表
        """
        with self._lock:
            revision = {
                "feedback": feedback,
                "required_changes": required_changes or [],
                "requested_at": datetime.now(),
                "revision_number": len(self._revisions.get(task_id, [])) + 1
            }

            if task_id not in self._revisions:
                self._revisions[task_id] = []

            self._revisions[task_id].append(revision)

            # 更新结果状态
            if task_id in self._results:
                self._results[task_id]["status"] = "revision_requested"
                self._results[task_id]["current_revision"] = revision
            else:
                self._results[task_id] = {
                    "task_id": task_id,
                    "status": "revision_requested",
                    "current_revision": revision
                }

    def get_acceptance_status(self, task_id: str) -> dict:
        """
        获取验收状态

        Args:
            task_id: 任务ID

        Returns:
            验收状态字典
        """
        with self._lock:
            if task_id not in self._results:
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "结果尚未提交"
                }

            return self._results[task_id].copy()

    def get_revision_history(self, task_id: str) -> list[dict]:
        """
        获取修订历史

        Args:
            task_id: 任务ID

        Returns:
            修订历史列表
        """
        with self._lock:
            return self._revisions.get(task_id, []).copy()


class PMExecutor:
    """PM执行器主类"""

    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.decomposer = TaskDecomposer()
        self.tracker = ProgressTracker()
        self.acceptor = ResultAcceptor()

        self._active_executions: dict[str, dict] = {}
        self._lock = threading.Lock()

    def execute_task(self, task: dict) -> dict:
        """
        执行任务

        Args:
            task: 任务字典，包含:
                - title: 任务标题
                - description: 任务描述
                - department: 负责部门
                - complexity: 复杂度
                - validation_criteria: 验收标准

        Returns:
            执行结果
        """
        execution_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()

        with self._lock:
            self._active_executions[execution_id] = {
                "execution_id": execution_id,
                "task": task,
                "status": "initialized",
                "started_at": start_time
            }

        try:
            # 步骤1: 任务拆解
            subtasks = self.decomposer.decompose(task)
            self.tracker.track(f"{execution_id}-decompose", 0.2)

            # 步骤2: 依赖分析
            task_dicts = [
                {
                    "task_id": st.task_id,
                    "type": st.title,
                    "department": task.get("department", ""),
                    "complexity": task.get("complexity", "medium"),
                    "dependencies": st.dependencies
                }
                for st in subtasks
            ]
            dependency_graph = self.decomposer.identify_dependencies(task_dicts)
            self.tracker.track(f"{execution_id}-dependencies", 0.3)

            # 步骤3: 估算工作量
            total_effort = 0.0
            for st in subtasks:
                st_dict = {
                    "task_id": st.task_id,
                    "department": task.get("department", ""),
                    "dependencies": st.dependencies
                }
                estimated = self.decomposer.estimate_effort(st_dict)
                st.estimated_hours = estimated
                total_effort += estimated

            self.tracker.track(f"{execution_id}-estimation", 0.4)

            # 步骤4: 模拟执行子任务
            results = {}
            for i, subtask in enumerate(subtasks):
                # 更新整体进度
                progress = 0.5 + (0.4 * (i / len(subtasks)))
                self.tracker.track(subtask.task_id, progress, {
                    "effort_hours": subtask.estimated_hours
                })

                # 模拟执行
                result = self._execute_subtask(subtask, task)
                results[subtask.task_id] = result

                # 结果验收
                acceptance = self._accept_result(subtask.task_id, result)
                results[subtask.task_id]["acceptance"] = acceptance

            self.tracker.track(f"{execution_id}-execution", 0.9)

            # 步骤5: 汇总结果
            final_result = self._aggregate_results(task, subtasks, results)

            # 更新执行状态
            with self._lock:
                self._active_executions[execution_id]["status"] = "completed"
                self._active_executions[execution_id]["completed_at"] = datetime.now()
                self._active_executions[execution_id]["result"] = final_result

            self.tracker.track(f"{execution_id}-final", 1.0)

            return {
                "execution_id": execution_id,
                "status": "success",
                "task_id": task.get("task_id", "unknown"),
                "subtasks": len(subtasks),
                "total_effort_hours": total_effort,
                "results": final_result,
                "duration": (datetime.now() - start_time).total_seconds()
            }

        except Exception as e:
            with self._lock:
                self._active_executions[execution_id]["status"] = "failed"
                self._active_executions[execution_id]["error"] = str(e)

            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }

    def _execute_subtask(self, subtask: SubTask, parent_task: dict) -> dict:
        """执行子任务"""
        # 模拟执行（实际场景会调用真正的执行器）
        return {
            "output": f"完成: {subtask.title}",
            "artifacts": [],
            "metrics": {
                "duration": subtask.estimated_hours * 3600,  # 秒
                "token_usage": int(subtask.estimated_hours * 1000)
            }
        }

    def _accept_result(self, task_id: str, result: dict) -> dict:
        """验收结果"""
        accepted = self.acceptor.accept(task_id, result)

        return {
            "accepted": accepted,
            "status": self.acceptor.get_acceptance_status(task_id)
        }

    def _aggregate_results(
        self,
        task: dict,
        subtasks: list[SubTask],
        results: dict[str, dict]
    ) -> dict:
        """汇总结果"""
        return {
            "task_title": task.get("title", ""),
            "department": task.get("department", ""),
            "subtask_count": len(subtasks),
            "completed_subtasks": sum(
                1 for r in results.values()
                if r.get("acceptance", {}).get("accepted", False)
            ),
            "subtask_results": {
                st.task_id: {
                    "title": st.title,
                    "status": "completed",
                    "result": results.get(st.task_id, {})
                }
                for st in subtasks
            }
        }

    def monitor_and_adjust(self, execution_id: str) -> dict:
        """
        监控并调整执行

        Args:
            execution_id: 执行ID

        Returns:
            调整建议
        """
        with self._lock:
            if execution_id not in self._active_executions:
                return {"error": "执行不存在"}

            execution = self._active_executions[execution_id]

        # 获取全局视图
        global_view = self.tracker.get_global_view()

        # 分析状态
        suggestions = []

        # 检查阻塞任务
        for task_id, task_status in global_view["tasks"].items():
            if task_status["status"] == "blocked":
                suggestions.append({
                    "type": "unblock",
                    "task_id": task_id,
                    "message": f"任务 {task_id} 被阻塞，需要处理"
                })

        # 检查进度落后
        for task_id, task_status in global_view["tasks"].items():
            if task_status["status"] == "in_progress":
                status = self.tracker.get_status(task_id)
                if status.get("trend") == "decelerating":
                    suggestions.append({
                        "type": "accelerate",
                        "task_id": task_id,
                        "message": f"任务 {task_id} 进度落后，需要加速"
                    })

        # 检查超时风险
        if execution.get("started_at"):
            elapsed = (datetime.now() - execution["started_at"]).total_seconds()
            if elapsed > self.timeout * 0.8:
                suggestions.append({
                    "type": "timeout_warning",
                    "execution_id": execution_id,
                    "message": f"执行即将超时 (已用 {elapsed:.0f}s / {self.timeout}s)"
                })

        return {
            "execution_id": execution_id,
            "status": execution["status"],
            "global_view": global_view,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI 测试"""
    print("\n" + "=" * 50)
    print("PM 执行器模块")
    print("=" * 50)

    executor = PMExecutor()

    # 测试数据
    task = {
        "task_id": "TEST-PM-001",
        "title": "用户增长活动策划",
        "description": "策划Q2用户增长活动，包含拉新、促活、留存三个环节",
        "department": "内容运营部",
        "complexity": "complex"
    }

    print(f"\n任务: {task['title']}")
    print(f"复杂度: {task['complexity']}")

    # 1. 测试任务拆解
    decomposer = TaskDecomposer()
    subtasks = decomposer.decompose(task)
    print(f"\n【任务拆解】共 {len(subtasks)} 个子任务:")
    for st in subtasks:
        print(f"  - {st.task_id}: {st.title} (预估 {st.estimated_hours}h)")

    # 2. 测试依赖分析
    task_dicts = [
        {"task_id": st.task_id, "type": st.title, "department": task["department"],
         "complexity": task["complexity"], "dependencies": st.dependencies}
        for st in subtasks
    ]
    deps = decomposer.identify_dependencies(task_dicts)
    print(f"\n【依赖分析】:")
    for task_id, task_deps in deps.items():
        if task_deps:
            print(f"  {task_id} ← {task_deps}")

    # 3. 测试执行
    print(f"\n【执行测试】:")
    result = executor.execute_task(task)
    print(f"  执行ID: {result['execution_id']}")
    print(f"  状态: {result['status']}")
    print(f"  耗时: {result['duration']:.2f}s")

    # 4. 测试监控
    print(f"\n【监控视图】:")
    monitor_result = executor.monitor_and_adjust(result['execution_id'])
    print(f"  全局进度: {monitor_result['global_view']['global_progress']:.1%}")
    print(f"  建议数: {len(monitor_result['suggestions'])}")


if __name__ == "__main__":
    main()
