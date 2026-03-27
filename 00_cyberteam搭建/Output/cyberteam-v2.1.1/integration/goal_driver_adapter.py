# CyberTeam v2 - Goal-Driven 目标驱动适配器

"""
Goal-Driven 目标循环执行适配器
基于 goal-driven-main 的 Master-Agent 评估循环

核心机制：
1. Master Agent 接收子 Agent 输出
2. 评估是否满足成功标准
3. 如果不满足，提供反馈并要求重试
4. 持续循环直到达成目标或达到最大迭代
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EvaluationResult(Enum):
    """评估结果"""
    SUCCESS = "success"
    NEEDS_REVISION = "needs_revision"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class GoalState:
    """目标状态"""
    goal_id: str
    description: str
    success_criteria: List[str]
    max_iterations: int = 10
    current_iteration: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed, blocked


@dataclass
class Evaluation:
    """评估结果"""
    result: EvaluationResult
    score: float  # 0-100
    feedback: str
    suggestions: List[str] = field(default_factory=list)
    criteria_scores: Dict[str, float] = field(default_factory=dict)


class CriteriaEvaluator:
    """成功标准评估器"""

    def __init__(self, criteria: List[str]):
        self.criteria = criteria

    def evaluate(self, output: Any, context: Dict[str, Any] = None) -> Evaluation:
        """评估输出是否满足标准"""

        context = context or {}
        criteria_scores = {}
        total_score = 0.0

        feedback_parts = []
        suggestions = []

        for criterion in self.criteria:
            score = self._evaluate_single_criterion(criterion, output, context)
            criteria_scores[criterion] = score
            total_score += score

            if score < 60:
                feedback_parts.append(f"❌ {criterion} 需要改进（{score:.0f}分）")
                suggestions.append(f"请重点改进：{criterion}")
            elif score < 80:
                feedback_parts.append(f"⚠️ {criterion} 基本达标（{score:.0f}分）")
            else:
                feedback_parts.append(f"✅ {criterion} 优秀（{score:.0f}分）")

        avg_score = total_score / len(self.criteria) if self.criteria else 0

        # 判断结果
        if avg_score >= 80:
            result = EvaluationResult.SUCCESS
        elif avg_score >= 50:
            result = EvaluationResult.NEEDS_REVISION
        else:
            result = EvaluationResult.FAILED

        return Evaluation(
            result=result,
            score=avg_score,
            feedback="\n".join(feedback_parts),
            suggestions=suggestions,
            criteria_scores=criteria_scores
        )

    def _evaluate_single_criterion(
        self,
        criterion: str,
        output: Any,
        context: Dict[str, Any]
    ) -> float:
        """评估单个标准"""

        output_str = str(output).lower()

        # 关键词匹配评估
        criterion_lower = criterion.lower()

        # 完整性检查
        if "完整" in criterion or "completeness" in criterion_lower:
            if isinstance(output, dict):
                required_keys = context.get("required_keys", [])
                if required_keys:
                    present = sum(1 for k in required_keys if k in output)
                    return (present / len(required_keys)) * 100
            return 70  # 默认

        # 专业性检查
        if "专业" in criterion or "professional" in criterion_lower:
            professional_keywords = ["分析", "建议", "方案", "策略", "方法论"]
            matches = sum(1 for kw in professional_keywords if kw in output_str)
            return min(40 + matches * 15, 100)

        # 可执行性检查
        if "可执行" in criterion or "actionable" in criterion_lower:
            action_keywords = ["步骤", "计划", "执行", "立即", "下一步", "action"]
            matches = sum(1 for kw in action_keywords if kw in output_str)
            return min(30 + matches * 17, 100)

        # 逻辑性检查
        if "逻辑" in criterion or "logic" in criterion_lower:
            if "因为" in output_str and "所以" in output_str:
                return 80
            if "首先" in output_str or "其次" in output_str:
                return 70
            return 50

        # 创新性检查
        if "创新" in criterion or "innovation" in criterion_lower:
            innovation_keywords = ["突破", "颠覆", "首创", "创新", "突破性"]
            matches = sum(1 for kw in innovation_keywords if kw in output_str)
            return min(30 + matches * 20, 100)

        # 默认评分
        if output and str(output).strip():
            return 65  # 有内容给基础分

        return 0  # 空内容零分


class GoalDriverAdapter:
    """Goal-Driven 目标驱动适配器"""

    def __init__(
        self,
        max_iterations: int = 10,
        min_success_score: float = 75.0
    ):
        self.max_iterations = max_iterations
        self.min_success_score = min_success_score
        self.active_goals: Dict[str, GoalState] = {}

    def create_goal(
        self,
        goal_id: str,
        description: str,
        success_criteria: List[str],
        max_iterations: int = None
    ) -> GoalState:
        """创建目标"""

        state = GoalState(
            goal_id=goal_id,
            description=description,
            success_criteria=success_criteria,
            max_iterations=max_iterations or self.max_iterations,
            status="pending"
        )

        self.active_goals[goal_id] = state
        logger.info(f"Goal created: {goal_id} - {description}")

        return state

    def evaluate(
        self,
        goal_id: str,
        output: Any,
        context: Dict[str, Any] = None
    ) -> Evaluation:
        """评估子 Agent 输出"""

        if goal_id not in self.active_goals:
            logger.warning(f"Goal not found: {goal_id}")
            return Evaluation(
                result=EvaluationResult.FAILED,
                score=0,
                feedback="目标不存在"
            )

        state = self.active_goals[goal_id]
        state.current_iteration += 1

        evaluator = CriteriaEvaluator(state.success_criteria)
        evaluation = evaluator.evaluate(output, context)

        # 记录历史
        state.history.append({
            "iteration": state.current_iteration,
            "timestamp": datetime.now().isoformat(),
            "output_preview": str(output)[:200],
            "evaluation": {
                "result": evaluation.result.value,
                "score": evaluation.score,
                "feedback": evaluation.feedback
            }
        })

        # 更新状态
        if evaluation.result == EvaluationResult.SUCCESS:
            state.status = "completed"
        elif evaluation.result == EvaluationResult.FAILED:
            state.status = "failed"
        elif state.current_iteration >= state.max_iterations:
            state.status = "failed"
            evaluation.result = EvaluationResult.FAILED
            evaluation.feedback += f"\n已达到最大迭代次数：{state.max_iterations}"

        logger.info(
            f"Goal {goal_id} iteration {state.current_iteration}: "
            f"{evaluation.result.value} ({evaluation.score:.1f}分)"
        )

        return evaluation

    def get_goal_state(self, goal_id: str) -> Optional[GoalState]:
        """获取目标状态"""
        return self.active_goals.get(goal_id)

    def generate_revision_prompt(
        self,
        goal_id: str,
        evaluation: Evaluation,
        original_task: str
    ) -> str:
        """生成修订提示词"""

        state = self.active_goals.get(goal_id)
        if not state:
            return original_task

        iterations_left = state.max_iterations - state.current_iteration

        prompt = f"""
## 目标未达成 - 需要修订

**任务**：{original_task}

**评估结果**：{evaluation.feedback}

**具体建议**：
"""

        for i, suggestion in enumerate(evaluation.suggestions, 1):
            prompt += f"\n{i}. {suggestion}"

        prompt += f"""

**剩余迭代次数**：{iterations_left}
**请根据上述反馈，重新完成任务。**
"""

        return prompt


class MasterAgent:
    """Master Agent - 目标循环执行主控"""

    def __init__(self, goal_driver: GoalDriverAdapter = None):
        self.goal_driver = goal_driver or GoalDriverAdapter()

    def execute_until_complete(
        self,
        goal_id: str,
        task: str,
        executor_fn: Callable[[str], Any],
        success_criteria: List[str],
        max_iterations: int = None
    ) -> Dict[str, Any]:
        """
        持续执行直到达成目标

        Args:
            goal_id: 目标ID
            task: 任务描述
            executor_fn: 执行器函数，接收任务字符串，返回输出
            success_criteria: 成功标准列表
            max_iterations: 最大迭代次数

        Returns:
            最终结果和评估历史
        """

        # 创建目标
        state = self.goal_driver.create_goal(
            goal_id=goal_id,
            description=task,
            success_criteria=success_criteria,
            max_iterations=max_iterations
        )
        state.status = "running"

        current_task = task
        final_result = None
        evaluations = []

        while state.status == "running":
            # 执行任务
            logger.info(f"Executing iteration {state.current_iteration + 1}")
            output = executor_fn(current_task)

            # 评估输出
            evaluation = self.goal_driver.evaluate(goal_id, output)
            evaluations.append(evaluation)

            if evaluation.result == EvaluationResult.SUCCESS:
                final_result = output
                break
            elif evaluation.result == EvaluationResult.FAILED:
                if state.current_iteration >= state.max_iterations:
                    break

            # 生成修订提示
            current_task = self.goal_driver.generate_revision_prompt(
                goal_id, evaluation, task
            )

        return {
            "goal_id": goal_id,
            "status": state.status,
            "total_iterations": state.current_iteration,
            "final_result": final_result,
            "final_score": evaluations[-1].score if evaluations else 0,
            "evaluations": evaluations,
            "history": state.history
        }


# 预定义成功标准模板
SUCCESS_CRITERIA_TEMPLATES = {
    "analysis": [
        "分析完整性 - 涵盖所有关键维度",
        "逻辑严谨性 - 因果关系清晰",
        "专业深度 - 展示领域专业知识",
        "可执行建议 - 给出具体行动方案"
    ],
    "design": [
        "设计完整性 - 覆盖所有用户场景",
        "用户体验 - 交互流畅直观",
        "视觉一致性 - 符合设计规范",
        "技术可行性 - 可实现且性能良好"
    ],
    "code": [
        "功能完整性 - 实现所有需求",
        "代码质量 - 可读性、可维护性",
        "性能达标 - 符合性能要求",
        "测试覆盖 - 核心路径有测试"
    ],
    "strategy": [
        "战略清晰性 - 方向明确",
        "竞争优势 - 差异化明显",
        "可执行性 - 可落地执行",
        "风险可控 - 已识别并有对策"
    ]
}


if __name__ == "__main__":
    # 测试
    goal_driver = GoalDriverAdapter()
    master = MasterAgent(goal_driver)

    # 模拟执行器
    call_count = [0]

    def mock_executor(task: str) -> str:
        call_count[0] += 1
        if call_count[0] < 3:
            return f"第{call_count[0]}次输出：不完整的方案"
        return "完整的专业方案，包含详细分析和可执行建议"

    # 执行
    result = master.execute_until_complete(
        goal_id="test-001",
        task="分析如何提升DAU 10%",
        executor_fn=mock_executor,
        success_criteria=SUCCESS_CRITERIA_TEMPLATES["analysis"]
    )

    print(f"最终状态：{result['status']}")
    print(f"迭代次数：{result['total_iterations']}")
    print(f"最终得分：{result['final_score']:.1f}")
