# engine/models/phase.py
"""Task Phase - Modern Corporate Governance Terms"""

from enum import Enum
from typing import Set


class TaskPhase(Enum):
    """
    Task execution phases using modern corporate governance terminology.

    Replaces historical terms:
    - 太子接旨 → INTAKE
    - 中书起草 → DRAFT
    - 门下审议 → REVIEW
    - 尚书派发 → DISPATCH
    - 六部执行 → EXECUTE
    - 汇总审核 → QA
    """

    INTAKE = "intake"  # 任务接收、分拣、优先级初判
    DRAFT = "draft"  # 方案起草、设计、文档编写
    REVIEW = "review"  # 方案评审、风险评估、审批
    DISPATCH = "dispatch"  # 任务派发、部门分配
    EXECUTE = "execute"  # 部门执行、落地实施
    QA = "qa"  # 质量审查、验收测试

    # Terminal states
    DONE = "done"  # 完成归档
    CANCELLED = "cancelled"  # 取消
    FAILED = "failed"  # 执行失败
    TIMEOUT = "timeout"  # 超时


# Legal state transitions
TRANSITION_RULES: dict[TaskPhase, Set[TaskPhase]] = {
    TaskPhase.INTAKE: {TaskPhase.DRAFT, TaskPhase.CANCELLED},
    TaskPhase.DRAFT: {TaskPhase.REVIEW, TaskPhase.CANCELLED},
    TaskPhase.REVIEW: {TaskPhase.DISPATCH, TaskPhase.DRAFT, TaskPhase.CANCELLED},
    TaskPhase.DISPATCH: {TaskPhase.EXECUTE, TaskPhase.CANCELLED},
    TaskPhase.EXECUTE: {TaskPhase.QA, TaskPhase.FAILED, TaskPhase.TIMEOUT, TaskPhase.CANCELLED},
    TaskPhase.QA: {TaskPhase.DONE, TaskPhase.EXECUTE, TaskPhase.CANCELLED},
    TaskPhase.DONE: set(),  # Terminal
    TaskPhase.CANCELLED: set(),  # Terminal
    TaskPhase.FAILED: set(),  # Terminal
    TaskPhase.TIMEOUT: set(),  # Terminal
}


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass
