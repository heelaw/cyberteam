"""跨部门协作链路引擎 - 部门间任务流转与结果汇总。

CEO智能路由 + 多部门协作 + Handoff协议 + 结果汇总
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .ceo_metadata import CEORouter, DEPARTMENT_METADATA


class TaskStatus(str, Enum):
    """任务状态机。"""
    PENDING = "pending"           # 待分配
    ROUTING = "routing"          # 路由中
    EXECUTING = "executing"       # 执行中
    WAITING_HANDOVER = "waiting_handover"  # 等待交接
    COLLABORATING = "collaborating"  # 协作中
    REVIEWING = "reviewing"       # 审核中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"            # 失败


class HandoffStatus(str, Enum):
    """Handoff状态。"""
    PENDING = "pending"           # 待移交
    IN_PROGRESS = "in_progress"   # 移交中
    ACCEPTED = "accepted"        # 已接收
    REJECTED = "rejected"        # 已拒绝
    COMPLETED = "completed"      # 协作完成


@dataclass
class HandoffRecord:
    """Handoff记录 - 部门间任务移交凭证。"""
    handoff_id: str
    task_id: str
    from_department: str          # 移交部门
    to_department: str            # 接收部门
    status: HandoffStatus
    context: Dict[str, Any]       # 上下文传递
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None  # 协作结果


@dataclass
class CollaborationTask:
    """协作任务 - 跨部门任务的完整生命周期。"""
    task_id: str
    original_task: str            # 原始任务描述
    status: TaskStatus

    # 路由结果
    primary_department: Optional[str] = None
    collaborating_departments: List[str] = field(default_factory=list)
    match_scores: Dict[str, float] = field(default_factory=dict)

    # 执行链路
    execution_chain: List[HandoffRecord] = field(default_factory=list)

    # 结果汇总
    results: Dict[str, Any] = field(default_factory=dict)  # {dept_id: result}
    final_output: Optional[Dict[str, Any]] = None

    # 元数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class CollaborationEngine:
    """跨部门协作引擎。

    负责：
    1. 智能识别需要多部门协作的任务
    2. 生成协作链路（主部门 + 协作部门）
    3. 管理Handoff流程
    4. 汇总各部门的执行结果
    """

    def __init__(self):
        self.router = CEORouter()
        self.active_tasks: Dict[str, CollaborationTask] = {}

    def plan_collaboration(self, task: str, context: Optional[Dict[str, Any]] = None) -> CollaborationTask:
        """规划协作链路。

        Args:
            task: 原始任务描述
            context: 上下文信息

        Returns:
            CollaborationTask: 包含完整协作链路规划的任务对象
        """
        # Step 1: 智能路由，获取匹配分数
        route_result = self.router.route(task, context)
        primary_dept = route_result["target_department"]
        alternatives = route_result.get("alternative_departments", [])

        # Step 2: 判断是否需要多部门协作
        collaborating_depts = self._detect_collaboration_need(
            task, primary_dept, alternatives, context
        )

        # Step 3: 构建协作任务
        task_id = f"collab_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        collab_task = CollaborationTask(
            task_id=task_id,
            original_task=task,
            status=TaskStatus.ROUTING,
            primary_department=primary_dept,
            collaborating_departments=collaborating_depts,
            match_scores={primary_dept: route_result["match_score"]}
        )

        # 添加匹配分数
        for alt in alternatives:
            collab_task.match_scores[alt["department_id"]] = alt["score"]

        # Step 4: 生成Handoff链路
        if collaborating_depts:
            collab_task.execution_chain = self._build_execution_chain(
                task_id, primary_dept, collaborating_depts, context or {}
            )

        collab_task.status = TaskStatus.PENDING
        self.active_tasks[task_id] = collab_task

        return collab_task

    def _detect_collaboration_need(
        self,
        task: str,
        primary_dept: str,
        alternatives: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
    ) -> List[str]:
        """检测是否需要多部门协作。

        协作场景：
        1. 主部门分数接近次优（<0.3差距）→ 需要协作
        2. 任务包含多类型关键词（产品+技术+运营）→ 需要多部门
        3. 显式指定多部门（context中注明）
        """
        # 场景1: 主部门与次优差距小于0.3
        if alternatives:
            top_score = alternatives[0]["score"] if alternatives else 0
            second_score = alternatives[1]["score"] if len(alternatives) > 1 else 0
            if top_score - second_score < 0.3 and second_score > 0.5:
                return [alt["department_id"] for alt in alternatives[:2]]

        # 场景2: 任务包含多类型关键词
        task_keywords = self._extract_task_keywords(task)
        multi_domain = self._check_multi_domain(task_keywords)

        # 场景3: context显式指定
        if context and context.get("collaborate_with"):
            return context["collaborate_with"]

        return []

    def _extract_task_keywords(self, task: str) -> List[str]:
        """从任务中提取关键词。"""
        # 简单分词 + 停用词过滤
        stop_words = {"的", "了", "和", "与", "或", "一个", "做", "制定", "分析"}
        words = [w for w in task if len(w) >= 2 and w not in stop_words]
        return words

    def _check_multi_domain(self, keywords: List[str]) -> bool:
        """检查是否涉及多领域。"""
        domains = set()
        for dept_id, metadata in DEPARTMENT_METADATA.items():
            for rule in metadata.routing_rules:
                for kw in rule.keywords:
                    if kw in keywords:
                        domains.add(dept_id)
        return len(domains) >= 2

    def _build_execution_chain(
        self,
        task_id: str,
        primary_dept: str,
        collaborating_depts: List[str],
        context: Dict[str, Any],
    ) -> List[HandoffRecord]:
        """构建执行链路。"""
        chain = []

        # 主部门先执行
        all_depts = [primary_dept] + collaborating_depts
        for i, dept_id in enumerate(all_depts):
            prev_dept = all_depts[i - 1] if i > 0 else None
            next_dept = all_depts[i + 1] if i < len(all_depts) - 1 else None

            handoff = HandoffRecord(
                handoff_id=f"{task_id}_h{i}",
                task_id=task_id,
                from_department=prev_dept or "ceo",
                to_department=dept_id,
                status=HandoffStatus.PENDING,
                context={
                    "input": context.get("input"),
                    "previous_results": {},  # 会在执行时填充
                    "expected_output": self._get_department_expected_output(dept_id),
                    "next_department": next_dept,
                },
            )
            chain.append(handoff)

        return chain

    def _get_department_expected_output(self, department_id: str) -> str:
        """获取部门期望输出描述。"""
        metadata = DEPARTMENT_METADATA.get(department_id)
        if metadata:
            return f"提供{metadata.responsibility}相关的产出"
        return "提供专业产出"

    def execute_handoff(self, handoff_id: str, result: Dict[str, Any]) -> HandoffRecord:
        """执行Handoff - 部门完成后移交到下一部门。"""
        # 找到对应的handoff记录
        for task in self.active_tasks.values():
            for handoff in task.execution_chain:
                if handoff.handoff_id == handoff_id:
                    handoff.status = HandoffStatus.ACCEPTED
                    handoff.result = result
                    handoff.updated_at = datetime.utcnow()

                    # 更新task的results
                    task.results[handoff.to_department] = result

                    # 如果还有下一部门，更新状态
                    next_idx = None
                    for i, h in enumerate(task.execution_chain):
                        if h.handoff_id == handoff_id:
                            next_idx = i + 1
                            break

                    if next_idx and next_idx < len(task.execution_chain):
                        task.status = TaskStatus.COLLABORATING
                        next_handoff = task.execution_chain[next_idx]
                        next_handoff.status = HandoffStatus.IN_PROGRESS
                        next_handoff.context["previous_results"] = result

                    return handoff

        raise ValueError(f"Handoff {handoff_id} not found")

    def aggregate_results(self, task_id: str) -> Dict[str, Any]:
        """汇总所有部门的执行结果。"""
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # 按执行顺序排列结果
        ordered_results = []
        for handoff in task.execution_chain:
            if handoff.result:
                ordered_results.append({
                    "department": handoff.to_department,
                    "output": handoff.result,
                    "timestamp": handoff.updated_at.isoformat(),
                })

        # 生成最终汇总
        task.final_output = {
            "task_id": task_id,
            "original_task": task.original_task,
            "collaboration_summary": {
                "departments_involved": [h.to_department for h in task.execution_chain],
                "total_departments": len(task.execution_chain),
                "results_count": len(ordered_results),
            },
            "execution_chain": ordered_results,
            "primary_department": task.primary_department,
            "final_recommendation": self._generate_recommendation(ordered_results),
        }

        task.status = TaskStatus.COMPLETED
        return task.final_output

    def _generate_recommendation(self, ordered_results: List[Dict[str, Any]]) -> str:
        """生成最终建议。"""
        if not ordered_results:
            return "无执行结果"

        # 综合各部门的产出，生成综合建议
        primary_output = ordered_results[0]["output"] if ordered_results else {}

        return f"基于{len(ordered_results)}个部门的协作产出，综合分析后给出建议"

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态。"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "primary_department": task.primary_department,
            "collaborating_departments": task.collaborating_departments,
            "execution_progress": f"{len([h for h in task.execution_chain if h.status == HandoffStatus.ACCEPTED])}/{len(task.execution_chain)}",
            "created_at": task.created_at.isoformat(),
        }


# 全局协作引擎实例
collaboration_engine = CollaborationEngine()
