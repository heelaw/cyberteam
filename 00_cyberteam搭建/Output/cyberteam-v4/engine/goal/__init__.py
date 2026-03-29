"""
Goal Tracker - 目标驱动循环引擎
来源: Goal-Driven/
功能: 使命必达，目标追踪，迭代直到达成
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GoalStatus(Enum):
    """目标状态"""
    PENDING = "pending"       # 待执行
    IN_PROGRESS = "in_progress"  # 执行中
    BLOCKED = "blocked"       # 阻塞
    COMPLETED = "completed"   # 完成
    FAILED = "failed"        # 失败
    ITERATING = "iterating"   # 迭代中


class IterationStrategy(Enum):
    """迭代策略"""
    FIXED = "fixed"          # 固定迭代
    EXPONENTIAL = "exponential"  # 指数退避
    ADAPTIVE = "adaptive"    # 自适应


@dataclass
class GoalCriteria:
    """目标标准"""
    metric: str              # 指标名称
    target: Any              # 目标值
    current: Any             # 当前值
    weight: float = 1.0       # 权重


@dataclass
class Goal:
    """目标"""
    id: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    criteria: List[GoalCriteria] = field(default_factory=list)
    sub_goals: List["Goal"] = field(default_factory=list)
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    iterations: int = 0
    max_iterations: int = 10
    assigned_to: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class GoalTracker:
    """
    目标追踪引擎 - Goal-Driven实现

    功能:
    1. 目标分解
    2. 迭代执行
    3. 标准验证
    4. 使命必达

    使用示例:
    >>> tracker = GoalTracker()
    >>> goal = tracker.create_goal("完成618营销方案", criteria=[...])
    >>> tracker.track(goal)
    >>> while not tracker.is_achieved(goal):
    ...     tracker.iterate(goal)
    """

    def __init__(
        self,
        max_iterations: int = 10,
        strategy: IterationStrategy = IterationStrategy.ADAPTIVE
    ):
        """
        初始化GoalTracker

        Args:
            max_iterations: 最大迭代次数
            strategy: 迭代策略
        """
        self._goals: Dict[str, Goal] = {}
        self._max_iterations = max_iterations
        self._strategy = strategy
        self._iteration_delay = 1  # 秒

        logger.info(f"GoalTracker 初始化完成 (max_iterations={max_iterations})")

    def create_goal(
        self,
        description: str,
        criteria: Optional[List[Dict]] = None,
        parent_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        **kwargs
    ) -> Goal:
        """
        创建目标

        Args:
            description: 目标描述
            criteria: 验收标准列表
            parent_id: 父目标ID
            assigned_to: 分配给谁
            **kwargs: 额外参数

        Returns:
            Goal: 创建的目标
        """
        goal_id = self._generate_id(description)

        goal_criteria = []
        if criteria:
            for c in criteria:
                goal_criteria.append(GoalCriteria(
                    metric=c.get("metric", "unknown"),
                    target=c.get("target", 0),
                    current=c.get("current", 0),
                    weight=c.get("weight", 1.0)
                ))

        goal = Goal(
            id=goal_id,
            description=description,
            criteria=goal_criteria,
            parent_id=parent_id,
            assigned_to=assigned_to,
            max_iterations=kwargs.get("max_iterations", self._max_iterations),
            metadata=kwargs
        )

        self._goals[goal_id] = goal

        logger.info(f"目标创建: {goal_id} - {description}")
        return goal

    def decompose(self, goal: Goal, sub_descriptions: List[str]) -> List[Goal]:
        """
        分解目标

        Args:
            goal: 父目标
            sub_descriptions: 子目标描述列表

        Returns:
            List[Goal]: 子目标列表
        """
        sub_goals = []
        for desc in sub_descriptions:
            sub = self.create_goal(
                description=desc,
                parent_id=goal.id,
                assigned_to=goal.assigned_to
            )
            sub_goals.append(sub)
            goal.sub_goals.append(sub)

        logger.info(f"目标分解: {goal.id} -> {len(sub_goals)}个子目标")
        return sub_goals

    def track(self, goal: Goal) -> bool:
        """
        开始追踪目标

        Args:
            goal: 目标

        Returns:
            bool: 是否成功
        """
        if goal.status != GoalStatus.PENDING:
            logger.warning(f"目标 {goal.id} 状态不是PENDING")

        goal.status = GoalStatus.IN_PROGRESS
        goal.updated_at = datetime.now()

        logger.info(f"目标开始追踪: {goal.id}")
        return True

    def is_achieved(self, goal: Goal) -> bool:
        """
        检查目标是否达成

        Args:
            goal: 目标

        Returns:
            bool: 是否达成
        """
        if not goal.criteria:
            # 没有明确标准，只要完成就算达成
            return goal.status == GoalStatus.COMPLETED

        # 检查所有标准
        all_achieved = True
        for criterion in goal.criteria:
            if criterion.current < criterion.target:
                all_achieved = False
                break

        return all_achieved

    def update_criteria(self, goal: Goal, metric: str, value: Any):
        """
        更新指标值

        Args:
            goal: 目标
            metric: 指标名称
            value: 新值
        """
        for criterion in goal.criteria:
            if criterion.metric == metric:
                criterion.current = value
                goal.updated_at = datetime.now()
                logger.debug(f"指标更新: {goal.id}/{metric} = {value}")
                return

        logger.warning(f"指标未找到: {goal.id}/{metric}")

    def iterate(self, goal: Goal) -> bool:
        """
        迭代目标执行

        Args:
            goal: 目标

        Returns:
            bool: 是否继续迭代
        """
        goal.iterations += 1
        goal.status = GoalStatus.ITERATING
        goal.updated_at = datetime.now()

        if goal.iterations >= goal.max_iterations:
            goal.status = GoalStatus.FAILED
            goal.error = f"超过最大迭代次数 ({goal.max_iterations})"
            logger.error(f"目标 {goal.id} 迭代失败: {goal.error}")
            return False

        logger.info(f"目标 {goal.id} 迭代 {goal.iterations}/{goal.max_iterations}")

        # 根据策略调整延迟
        if self._strategy == IterationStrategy.EXPONENTIAL:
            delay = self._iteration_delay * (2 ** (goal.iterations - 1))
            time.sleep(min(delay, 60))  # 最多等60秒
        elif self._strategy == IterationStrategy.ADAPTIVE:
            # 自适应：每次迭代缩短延迟
            delay = max(0.1, self._iteration_delay / goal.iterations)
            time.sleep(delay)

        return True

    def complete(self, goal: Goal, result: Any = None):
        """
        标记目标完成

        Args:
            goal: 目标
            result: 结果
        """
        goal.status = GoalStatus.COMPLETED
        goal.result = result
        goal.updated_at = datetime.now()

        logger.info(f"目标完成: {goal.id}")

        # 检查父目标
        if goal.parent_id and goal.parent_id in self._goals:
            parent = self._goals[goal.parent_id]
            # 检查是否所有子目标都完成
            if all(s.status == GoalStatus.COMPLETED for s in parent.sub_goals):
                self.complete(parent)

    def fail(self, goal: Goal, error: str):
        """
        标记目标失败

        Args:
            goal: 目标
            error: 错误信息
        """
        goal.status = GoalStatus.FAILED
        goal.error = error
        goal.updated_at = datetime.now()

        logger.error(f"目标失败: {goal.id} - {error}")

        # 父目标也标记为失败
        if goal.parent_id and goal.parent_id in self._goals:
            parent = self._goals[goal.parent_id]
            self.fail(parent, f"子目标失败: {goal.id}")

    def block(self, goal: Goal, reason: str):
        """
        阻塞目标

        Args:
            goal: 目标
            reason: 阻塞原因
        """
        goal.status = GoalStatus.BLOCKED
        goal.error = reason
        goal.updated_at = datetime.now()

        logger.warning(f"目标阻塞: {goal.id} - {reason}")

    def get_status(self, goal_id: str) -> Optional[Dict]:
        """
        获取目标状态

        Args:
            goal_id: 目标ID

        Returns:
            Dict: 状态信息
        """
        if goal_id not in self._goals:
            return None

        goal = self._goals[goal_id]
        return {
            "id": goal.id,
            "description": goal.description,
            "status": goal.status.value,
            "iterations": goal.iterations,
            "max_iterations": goal.max_iterations,
            "criteria": [
                {
                    "metric": c.metric,
                    "current": c.current,
                    "target": c.target,
                    "progress": c.current / c.target if c.target else 0
                }
                for c in goal.criteria
            ],
            "sub_goals": [s.id for s in goal.sub_goals],
            "parent_id": goal.parent_id,
            "result": goal.result,
            "error": goal.error,
            "created_at": goal.created_at.isoformat(),
            "updated_at": goal.updated_at.isoformat()
        }

    def list_goals(
        self,
        status: Optional[GoalStatus] = None,
        assigned_to: Optional[str] = None
    ) -> List[Goal]:
        """
        列出目标

        Args:
            status: 状态过滤
            assigned_to: 分配过滤

        Returns:
            List[Goal]: 目标列表
        """
        result = list(self._goals.values())

        if status:
            result = [g for g in result if g.status == status]

        if assigned_to:
            result = [g for g in result if g.assigned_to == assigned_to]

        return result

    def execute_until_complete(
        self,
        goal: Goal,
        execute_fn: Callable,
        check_fn: Optional[Callable] = None,
        max_time: Optional[int] = None
    ) -> bool:
        """
        执行直到完成

        Args:
            goal: 目标
            execute_fn: 执行函数 (goal) -> bool
            check_fn: 检查函数 (goal) -> bool, None表示使用is_achieved
            max_time: 最大时间（秒）

        Returns:
            bool: 是否成功完成
        """
        start_time = time.time()
        self.track(goal)

        while True:
            # 检查超时
            if max_time and (time.time() - start_time) > max_time:
                self.fail(goal, f"超时 ({max_time}秒)")
                return False

            # 执行
            try:
                success = execute_fn(goal)
                if not success:
                    self.fail(goal, "执行函数返回失败")
                    return False
            except Exception as e:
                self.fail(goal, f"执行异常: {str(e)}")
                return False

            # 更新标准
            if check_fn:
                check_fn(goal)
            else:
                self.is_achieved(goal)

            # 检查是否完成
            if self.is_achieved(goal):
                self.complete(goal)
                return True

            # 迭代
            if not self.iterate(goal):
                return False

        return False

    def _generate_id(self, description: str) -> str:
        """生成目标ID"""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        raw = f"{description}_{timestamp}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]


# 全局实例
GOAL = GoalTracker()
