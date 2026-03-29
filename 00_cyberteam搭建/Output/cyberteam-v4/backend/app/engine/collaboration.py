"""跨部门协作链路引擎 - 部门间任务流转与结果汇总。

CEO智能路由 + 多部门协作 + Handoff协议 + 结果汇总 + 执行器抽象
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

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
class ExecutionResult:
    """标准化执行结果 - 所有部门执行后统一格式。"""
    department_id: str
    output: Any                   # 执行产出
    status: str                  # success/failed
    metrics: Dict[str, Any] = field(default_factory=dict)  # 指标
    artifacts: List[str] = field(default_factory=list)     # 产出物
    suggestions: List[str] = field(default_factory=list)   # 建议
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "department_id": self.department_id,
            "output": self.output,
            "status": self.status,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
        }


class AgentExecutor(ABC):
    """Agent执行器抽象 - 各部门执行器的基类。"""

    def __init__(self, department_id: str):
        self.department_id = department_id

    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        """执行任务。"""
        pass

    def get_supported_skills(self) -> List[str]:
        """获取支持的技能列表。"""
        metadata = DEPARTMENT_METADATA.get(self.department_id)
        if metadata:
            return [s.name for s in metadata.skills]
        return []


class MarketingAgentExecutor(AgentExecutor):
    """市场部Agent执行器。"""

    def __init__(self):
        super().__init__("marketing")

    async def execute(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        # 实际实现：调用市场Agent
        output = {
            "task": task,
            "brand_strategy": "品牌定位与建设方案",
            "channel_plan": "渠道推广策略",
            "budget_allocation": "预算分配建议",
            "timeline": "执行时间表",
        }
        return ExecutionResult(
            department_id=self.department_id,
            output=output,
            status="success",
            metrics={"confidence": 0.9, "depth": "comprehensive"},
        )


class OperationsAgentExecutor(AgentExecutor):
    """运营部Agent执行器。"""

    def __init__(self):
        super().__init__("operations")

    async def execute(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        # 整合前置部门结果
        integrated = context.get("previous_results", {})
        output = {
            "task": task,
            "growth_strategy": "用户增长策略",
            "content_plan": "内容运营规划",
            "activity_design": "活动策划方案",
            "metrics": "关键指标定义",
            "integrated_from": integrated.get("department_id") if integrated else None,
        }
        return ExecutionResult(
            department_id=self.department_id,
            output=output,
            status="success",
            metrics={"confidence": 0.85, "synergy": "high"},
        )


class DesignAgentExecutor(AgentExecutor):
    """设计部Agent执行器。"""

    def __init__(self):
        super().__init__("design")

    async def execute(self, task: str, context: Dict[str, Any]) -> ExecutionResult:
        integrated = context.get("previous_results", {})
        output = {
            "task": task,
            "ui_design": "UI设计方案",
            "visual_spec": "视觉规范",
            "prototype": "原型链接",
            "brand_elements": "品牌元素整合",
            "integrated_from": integrated.get("department_id") if integrated else None,
        }
        return ExecutionResult(
            department_id=self.department_id,
            output=output,
            status="success",
            metrics={"confidence": 0.88, "revision_rounds": 2},
        )


# 部门执行器注册表
DEPARTMENT_EXECUTORS: Dict[str, type] = {
    "marketing": MarketingAgentExecutor,
    "operations": OperationsAgentExecutor,
    "design": DesignAgentExecutor,
    "product": AgentExecutor,  # 占位，后续实现
    "engineering": AgentExecutor,
    "hr": AgentExecutor,
    "finance": AgentExecutor,
    "ceo": AgentExecutor,
}


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

    def simulate_execution(self, task_id: str) -> Dict[str, Any]:
        """模拟执行完整协作链路 - 用于演示和测试。

        各部门执行结果通过HandoffRecord流转，最终汇总。
        """
        task = self.active_tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # 模拟执行链路
        for i, handoff in enumerate(task.execution_chain):
            # 模拟部门执行
            dept_result = self._simulate_department_execution(
                handoff.to_department,
                task.original_task,
                handoff.context.get("previous_results"),
            )

            # 执行handoff
            handoff.status = HandoffStatus.ACCEPTED
            handoff.result = dept_result.to_dict()
            handoff.updated_at = datetime.utcnow()

            # 更新task结果
            task.results[handoff.to_department] = dept_result.to_dict()

            # 更新下一handoff状态
            if i + 1 < len(task.execution_chain):
                task.status = TaskStatus.COLLABORATING
                task.execution_chain[i + 1].status = HandoffStatus.IN_PROGRESS
                task.execution_chain[i + 1].context["previous_results"] = dept_result.to_dict()

        # 最终汇总
        task.status = TaskStatus.COMPLETED
        return self.aggregate_results(task_id)

    def _simulate_department_execution(
        self,
        department_id: str,
        task: str,
        previous_results: Optional[Dict[str, Any]],
    ) -> ExecutionResult:
        """模拟部门执行 - 生成标准化执行结果。"""
        metadata = DEPARTMENT_METADATA.get(department_id)

        # 模拟产出
        output = {
            "analysis": f"{metadata.name}对任务的分析" if metadata else "分析结果",
            "recommendations": [
                f"基于{metadata.responsibility if metadata else '专业判断'}的建议"
            ] if metadata else ["建议1", "建议2"],
            "contribution": f"{department_id}部门的专业产出",
        }

        # 如果有前置结果，整合
        if previous_results and isinstance(previous_results, dict):
            # previous_results可能是ExecutionResult.to_dict()或HandoffRecord.result
            if "department_id" in previous_results:
                output["integrated_from"] = [previous_results["department_id"]]
            elif "to_department" in previous_results:
                output["integrated_from"] = [previous_results["to_department"]]

        return ExecutionResult(
            department_id=department_id,
            output=output,
            status="success",
            metrics={
                "execution_time_ms": 100,
                "confidence": 0.85,
            },
            artifacts=[],
            suggestions=[
                f"建议{metadata.name if metadata else '该部门'}重点关注输出质量" if metadata else "建议关注质量"
            ],
            metadata={
                "executed_at": datetime.utcnow().isoformat(),
                "task": task,
            },
        )

    def execute_full_collaboration(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """一键执行完整协作链路 - 规划+执行+汇总。"""
        # Step 1: 规划
        collab_task = self.plan_collaboration(task, context)

        # Step 2: 执行
        if collab_task.execution_chain:
            return self.simulate_execution(collab_task.task_id)
        else:
            # 单一部门直接执行
            result = self._simulate_department_execution(
                collab_task.primary_department, task, None
            )
            return {
                "task_id": collab_task.task_id,
                "original_task": task,
                "collaboration_summary": {
                    "departments_involved": [collab_task.primary_department],
                    "total_departments": 1,
                    "results_count": 1,
                },
                "execution_chain": [{
                    "department": collab_task.primary_department,
                    "output": result.to_dict(),
                    "timestamp": datetime.utcnow().isoformat(),
                }],
                "primary_department": collab_task.primary_department,
                "final_recommendation": "基于单一部门产出给出建议",
            }

    async def execute_with_real_agents(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """使用真实Agent执行器执行协作链路。"""
        import asyncio

        # Step 1: 规划
        collab_task = self.plan_collaboration(task, context)

        if not collab_task.execution_chain:
            # 单一部门
            executor_cls = DEPARTMENT_EXECUTORS.get(collab_task.primary_department)
            if executor_cls and executor_cls != AgentExecutor:
                executor = executor_cls()
                result = await executor.execute(task, context or {})
                return {
                    "task_id": collab_task.task_id,
                    "original_task": task,
                    "collaboration_summary": {
                        "departments_involved": [collab_task.primary_department],
                        "total_departments": 1,
                        "results_count": 1,
                    },
                    "execution_chain": [{
                        "department": collab_task.primary_department,
                        "output": result.to_dict(),
                        "timestamp": datetime.utcnow().isoformat(),
                    }],
                    "primary_department": collab_task.primary_department,
                    "final_recommendation": "单一部门执行完成",
                }
            return self.execute_full_collaboration(task, context)

        # Step 2: 按链路执行
        ordered_results = []
        previous_result = None

        for handoff in collab_task.execution_chain:
            dept_id = handoff.to_department
            executor_cls = DEPARTMENT_EXECUTORS.get(dept_id)

            # 构建执行上下文
            exec_context = {"previous_results": previous_result}

            if executor_cls and executor_cls != AgentExecutor:
                # 使用真实执行器
                executor = executor_cls()
                result = await executor.execute(task, exec_context)
                handoff.result = result.to_dict()
            else:
                # 回退到模拟执行
                result = self._simulate_department_execution(dept_id, task, previous_result)
                handoff.result = result.to_dict()

            handoff.status = HandoffStatus.ACCEPTED
            handoff.updated_at = datetime.utcnow()

            ordered_results.append({
                "department": dept_id,
                "output": handoff.result,
                "timestamp": handoff.updated_at.isoformat(),
            })

            previous_result = handoff.result
            collab_task.results[dept_id] = handoff.result

        # Step 3: 汇总
        collab_task.final_output = {
            "task_id": collab_task.task_id,
            "original_task": task,
            "collaboration_summary": {
                "departments_involved": [h.to_department for h in collab_task.execution_chain],
                "total_departments": len(collab_task.execution_chain),
                "results_count": len(ordered_results),
            },
            "execution_chain": ordered_results,
            "primary_department": collab_task.primary_department,
            "final_recommendation": self._generate_recommendation(ordered_results),
        }
        collab_task.status = TaskStatus.COMPLETED

        return collab_task.final_output


# 全局协作引擎实例
collaboration_engine = CollaborationEngine()
