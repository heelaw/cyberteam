#!/usr/bin/env python3
"""
CyberTeam V4 - 状态机模块 (State Machine)

融合 Edict 状态定义与 CyberTeam 八节点流程，设计 CyberTeam 专用状态机。

Modern Governance 状态流:
    Intake(任务接收) → Draft(方案起草) → Review(评审审议) → Dispatch(调度派发)
    → Execute(部门执行) → QA(质量审查) → Done(完成)

CyberTeam 八节点:
    CEO路由 → 策略设计 → PM协调 → 部门执行 → 辩论审议 → 评分把关 → 质量门禁 → Swarm编排

融合后的状态机统一状态:
    PENDING → INTAKE → DRAFT → REVIEW → DISPATCH → EXECUTE → QA → DONE
                                        ↓
                                    CANCELLED / FAILED / TIMEOUT

注意: EdictState 枚举已废弃，请使用 CyberTeamState 或 engine.models.TaskPhase。
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional, Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)


class EdictState(Enum):
    """
    Edict 核心状态枚举 (向后兼容 - 已废弃)

    警告: 此枚举保留用于向后兼容，新代码应使用 CyberTeamState 或 engine.models.TaskPhase。
    现代公司治理映射:
    - TAIZI → INTAKE (任务接收)
    - ZHONGSHU → DRAFT (方案起草)
    - MENXIA → REVIEW (评审审议)
    - ASSIGNED → DISPATCH (调度派发)
    - DOING → EXECUTE (部门执行)
    - REVIEW → QA (质量审查)
    - DONE → DONE (完成)
    """

    # 核心流转状态 (已废弃，请使用 CyberTeamState)
    TAIZI = "taizi"           # INTAKE (废弃)
    ZHONGSHU = "zhongshu"     # DRAFT (废弃)
    MENXIA = "menxia"         # REVIEW (废弃)
    ASSIGNED = "assigned"      # DISPATCH (废弃)
    DOING = "doing"           # EXECUTE (废弃)
    REVIEW = "review"         # QA (废弃)
    DONE = "done"             # DONE

    # 终态
    CANCELLED = "cancelled"   # 取消
    FAILED = "failed"         # 失败
    TIMEOUT = "timeout"       # 超时

    # 初始状态
    PENDING = "pending"       # 等待接旨


class CyberTeamState(Enum):
    """
    CyberTeam 公司化状态枚举 (新标准)

    公司化术语替换古代官制:
    - CEO_ROUTE: CEO路由分拣
    - COO_COORDINATION: COO协调规划
    - CEO_REVIEW: CEO质量审核
    - PM_DISPATCH: PM任务派发
    - DEPT_ASSIGNMENT: 部门分配
    - DEPT_EXECUTION: 部门执行中
    - CEO_APPROVAL: CEO最终审批
    - DONE: 回奏完成
    """

    # 核心流转状态 (公司化)
    CEO_ROUTE = "ceo_route"           # CEO路由分拣 (原TAIZI)
    COO_COORDINATION = "coo_coordination"  # COO协调规划 (原ZHONGSHU)
    CEO_REVIEW = "ceo_review"         # CEO质量审核 (原MENXIA)
    PM_DISPATCH = "pm_dispatch"       # PM任务派发 (原ASSIGNED)
    DEPT_ASSIGNMENT = "dept_assignment"  # 部门分配 (原ASSIGNED，同PM_DISPATCH)
    DEPT_EXECUTION = "dept_execution" # 部门执行中 (原DOING)
    CEO_APPROVAL = "ceo_approval"     # CEO最终审批 (原REVIEW)
    DONE = "done"                     # 回奏完成

    # 终态
    CANCELLED = "cancelled"   # 取消
    FAILED = "failed"         # 失败
    TIMEOUT = "timeout"       # 超时

    # 初始状态
    PENDING = "pending"       # 等待接旨

    @classmethod
    def from_edict_state(cls, edict_state: EdictState) -> CyberTeamState:
        """从 EdictState 转换为 CyberTeamState"""
        mapping = {
            EdictState.TAIZI: cls.CEO_ROUTE,
            EdictState.ZHONGSHU: cls.COO_COORDINATION,
            EdictState.MENXIA: cls.CEO_REVIEW,
            EdictState.ASSIGNED: cls.DEPT_ASSIGNMENT,
            EdictState.DOING: cls.DEPT_EXECUTION,
            EdictState.REVIEW: cls.CEO_APPROVAL,
            EdictState.DONE: cls.DONE,
            EdictState.CANCELLED: cls.CANCELLED,
            EdictState.FAILED: cls.FAILED,
            EdictState.TIMEOUT: cls.TIMEOUT,
            EdictState.PENDING: cls.PENDING,
        }
        return mapping.get(edict_state, cls.PENDING)


class CyberTeamNode(Enum):
    """
    CyberTeam 八节点枚举

    每个节点代表工作流中的一个核心处理阶段。
    """

    CEO_ROUTER = "ceo_router"       # CEO路由: 意图识别、复杂度评估
    STRATEGY = "strategy"            # 策略设计: 方案框架、资源规划
    PM_COORD = "pm_coord"            # PM协调: 任务拆解、进度跟踪
    DEPT_EXEC = "dept_exec"          # 部门执行
    DEBATE = "debate"                # 辩论审议: 多专家辩论收敛
    SCORING = "scoring"              # 评分把关: 六维评分
    QUALITY_GATE = "quality_gate"    # 质量门禁: 五级审核
    SWARM = "swarm"                  # Swarm编排: 群体智能协作


class TransitionReason(Enum):
    """状态转换原因 (公司化术语)"""

    # 正常流转
    DIVINE_ORDER = "divine_order"          # 皇上下旨
    CEO_ROUTE_RECEIVED = "ceo_route_received"     # CEO接单 (原PRINCE_RECEIVED)
    COO_PLAN_DRAFTED = "coo_plan_drafted"           # COO方案完成 (原MEMO_DRAFTED)
    COO_PLAN_APPROVED = "coo_plan_approved"         # COO方案批准 (原MEMO_APPROVED)
    COO_PLAN_REJECTED = "coo_plan_rejected"         # COO方案驳回 (原MEMO_REJECTED)
    TASK_ASSIGNED = "task_assigned"          # 任务派发
    EXECUTION_COMPLETE = "execution_complete"  # 执行完成
    CEO_APPROVAL_COMPLETE = "ceo_approval_complete"      # CEO审批完成 (原REVIEW_COMPLETE)
    CEO_APPROVAL = "ceo_approval"  # CEO最终批准 (原IMPERIAL_APPROVAL)

    # 异常终态
    CANCELLED = "cancelled"             # 取消
    FAILED = "failed"                   # 失败
    TIMEOUT = "timeout"                 # 超时

    # 向后兼容别名
    PRINCE_RECEIVED = "prince_received"     # 废弃，请使用 CEO_ROUTE_RECEIVED
    MEMO_DRAFTED = "memo_drafted"           # 废弃，请使用 COO_PLAN_DRAFTED
    MEMO_APPROVED = "memo_approved"         # 废弃，请使用 COO_PLAN_APPROVED
    MEMO_REJECTED = "memo_rejected"         # 废弃，请使用 COO_PLAN_REJECTED
    IMPERIAL_APPROVAL = "imperial_approval"  # 废弃，请使用 CEO_APPROVAL
    REVIEW_COMPLETE = "review_complete"      # 废弃，请使用 CEO_APPROVAL_COMPLETE


# Edict → CyberTeam 八节点映射 (向后兼容 - 已废弃)
EDICT_TO_CYBERTEAM_NODE_MAP = {
    EdictState.TAIZI: CyberTeamNode.CEO_ROUTER,
    EdictState.ZHONGSHU: CyberTeamNode.STRATEGY,
    EdictState.MENXIA: CyberTeamNode.PM_COORD,
    EdictState.ASSIGNED: CyberTeamNode.DEPT_EXEC,
    EdictState.DOING: CyberTeamNode.DEPT_EXEC,
    EdictState.REVIEW: CyberTeamNode.SCORING,
    EdictState.DONE: CyberTeamNode.QUALITY_GATE,
}

# CyberTeamState → CyberTeam 八节点映射 (新标准)
CYBERTEAM_STATE_TO_NODE_MAP = {
    CyberTeamState.CEO_ROUTE: CyberTeamNode.CEO_ROUTER,
    CyberTeamState.COO_COORDINATION: CyberTeamNode.STRATEGY,
    CyberTeamState.CEO_REVIEW: CyberTeamNode.PM_COORD,
    CyberTeamState.PM_DISPATCH: CyberTeamNode.DEPT_EXEC,
    CyberTeamState.DEPT_ASSIGNMENT: CyberTeamNode.DEPT_EXEC,
    CyberTeamState.DEPT_EXECUTION: CyberTeamNode.DEPT_EXEC,
    CyberTeamState.CEO_APPROVAL: CyberTeamNode.SCORING,
    CyberTeamState.DONE: CyberTeamNode.QUALITY_GATE,
}

# 合法的状态转换规则
STATE_TRANSITIONS = {
    # 核心流转
    EdictState.PENDING: {EdictState.TAIZI},
    EdictState.TAIZI: {EdictState.ZHONGSHU, EdictState.CANCELLED},
    EdictState.ZHONGSHU: {EdictState.MENXIA, EdictState.TAIZI},  # 可退回重分
    EdictState.MENXIA: {
        EdictState.ASSIGNED,    # 准奏
        EdictState.ZHONGSHU,    # 封驳
        EdictState.CANCELLED,   # 直接取消
    },
    EdictState.ASSIGNED: {EdictState.DOING, EdictState.CANCELLED},
    EdictState.DOING: {EdictState.REVIEW, EdictState.FAILED, EdictState.TIMEOUT, EdictState.CANCELLED},
    EdictState.REVIEW: {
        EdictState.DONE,        # 通过
        EdictState.MENXIA,      # 退回修改
        EdictState.DOING,       # 重做
        EdictState.CANCELLED,   # 取消
    },
    EdictState.DONE: set(),  # 终态

    # 终态
    EdictState.CANCELLED: set(),   # 终态
    EdictState.FAILED: set(),      # 终态
    EdictState.TIMEOUT: set(),     # 终态
}

# CyberTeam 八节点处理顺序
CYBERTEAM_NODE_ORDER = [
    CyberTeamNode.CEO_ROUTER,      # 1. CEO路由
    CyberTeamNode.STRATEGY,         # 2. 策略设计
    CyberTeamNode.PM_COORD,        # 3. PM协调
    CyberTeamNode.DEPT_EXEC,        # 4. 部门执行
    CyberTeamNode.DEBATE,           # 5. 辩论审议
    CyberTeamNode.SCORING,         # 6. 评分把关
    CyberTeamNode.QUALITY_GATE,    # 7. 质量门禁
    CyberTeamNode.SWARM,           # 8. Swarm编排
]

# 状态元数据
STATE_METADATA = {
    EdictState.PENDING: {
        "name": "待接旨",
        "department": "CEO",
        "description": "等待CEO下达指令",
        "can_auto_progress": True,
        "timeout_minutes": 0,
    },
    EdictState.TAIZI: {
        "name": "任务接收",
        "department": "Intake",
        "description": "Intake接收并分拣任务，判断是闲聊还是正式任务",
        "can_auto_progress": False,
        "timeout_minutes": 5,
    },
    EdictState.ZHONGSHU: {
        "name": "方案起草",
        "department": "Draft",
        "description": "Draft分析任务，起草执行方案",
        "can_auto_progress": False,
        "timeout_minutes": 60,
    },
    EdictState.MENXIA: {
        "name": "评审审议",
        "department": "Review",
        "description": "Review审议方案，可批准或退回",
        "can_auto_progress": False,
        "timeout_minutes": 30,
    },
    EdictState.ASSIGNED: {
        "name": "调度派发",
        "department": "Dispatch",
        "description": "Dispatch接收批准方案，派发给部门执行",
        "can_auto_progress": False,
        "timeout_minutes": 10,
    },
    EdictState.DOING: {
        "name": "部门执行",
        "department": "Execute",
        "description": "部门并行执行任务",
        "can_auto_progress": False,
        "timeout_minutes": 480,  # 8小时
    },
    EdictState.REVIEW: {
        "name": "质量审查",
        "department": "QA",
        "description": "QA汇总结果，进行质量审核",
        "can_auto_progress": False,
        "timeout_minutes": 60,
    },
    EdictState.DONE: {
        "name": "完成",
        "department": "Done",
        "description": "任务完成",
        "can_auto_progress": False,
        "timeout_minutes": 0,
    },
    EdictState.CANCELLED: {
        "name": "已取消",
        "department": "CEO",
        "description": "CEO取消任务",
        "can_auto_progress": False,
        "timeout_minutes": 0,
    },
    EdictState.FAILED: {
        "name": "执行失败",
        "department": "执行部门",
        "description": "任务执行失败",
        "can_auto_progress": False,
        "timeout_minutes": 0,
    },
    EdictState.TIMEOUT: {
        "name": "执行超时",
        "department": "执行部门",
        "description": "任务执行超时",
        "can_auto_progress": False,
        "timeout_minutes": 0,
    },
}


@dataclass
class StateTransition:
    """状态转换记录"""

    from_state: EdictState
    to_state: EdictState
    reason: TransitionReason
    triggered_by: str  # Agent ID 或 "system"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "reason": self.reason.value,
            "triggered_by": self.triggered_by,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class TaskState:
    """
    任务状态机上下文

    包含任务的完整状态信息、历史转换记录、当前处理的CyberTeam节点等。
    """

    task_id: str
    trace_id: str
    state: EdictState = EdictState.PENDING
    current_node: Optional[CyberTeamNode] = None

    # 部门相关 (Legacy - 已废弃)
    prince_agent: Optional[str] = None          # Intake Agent ID (废弃)
    zhongshu_agent: Optional[str] = None         # Draft Agent ID (废弃)
    menxia_agent: Optional[str] = None          # Review Agent ID (废弃)
    shangshu_agent: Optional[str] = None        # Dispatch Agent ID (废弃)
    six_ministries: Dict[str, str] = field(default_factory=dict)  # 部门Agent映射 (废弃)

    # CyberTeam八节点相关
    completed_nodes: List[CyberTeamNode] = field(default_factory=list)
    active_node: Optional[CyberTeamNode] = None
    node_results: Dict[CyberTeamNode, dict] = field(default_factory=dict)

    # 质量评分
    score: Optional[float] = None
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    # 转换历史
    transitions: List[StateTransition] = field(default_factory=list)

    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # 元数据
    title: str = ""
    description: str = ""
    user_input: str = ""
    priority: str = "中"
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())[:8]
        if not self.trace_id:
            self.trace_id = f"trace-{self.task_id}"

    def get_metadata(self, state: EdictState) -> dict:
        """获取状态元数据"""
        return STATE_METADATA.get(state, {})

    def get_current_department(self) -> str:
        """获取当前负责部门"""
        meta = self.get_metadata(self.state)
        return meta.get("department", "未知")

    def is_terminal_state(self) -> bool:
        """检查是否为终态"""
        return self.state in {
            EdictState.DONE,
            EdictState.CANCELLED,
            EdictState.FAILED,
            EdictState.TIMEOUT,
        }

    def can_transition_to(self, target_state: EdictState) -> bool:
        """检查是否可以转换到目标状态"""
        allowed = STATE_TRANSITIONS.get(self.state, set())
        return target_state in allowed

    def get_next_cyberteam_node(self) -> Optional[CyberTeamNode]:
        """获取下一个CyberTeam节点"""
        if not self.current_node:
            return CyberTeamNode.CEO_ROUTER

        try:
            current_idx = CYBERTEAM_NODE_ORDER.index(self.current_node)
            if current_idx + 1 < len(CYBERTEAM_NODE_ORDER):
                return CYBERTEAM_NODE_ORDER[current_idx + 1]
        except ValueError:
            pass
        return None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "state": self.state.value,
            "current_node": self.current_node.value if self.current_node else None,
            "prince_agent": self.prince_agent,
            "zhongshu_agent": self.zhongshu_agent,
            "menxia_agent": self.menxia_agent,
            "shangshu_agent": self.shangshu_agent,
            "six_ministries": self.six_ministries,
            "completed_nodes": [n.value for n in self.completed_nodes],
            "active_node": self.active_node.value if self.active_node else None,
            "score": self.score,
            "score_breakdown": self.score_breakdown,
            "transitions": [t.to_dict() for t in self.transitions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "title": self.title,
            "description": self.description,
            "user_input": self.user_input,
            "priority": self.priority,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class StateMachineError(Exception):
    """状态机异常"""

    pass


class InvalidTransitionError(StateMachineError):
    """无效转换异常"""

    pass


class StateMachine:
    """
    CyberTeam V4 状态机

    融合 Edict 状态定义与 CyberTeam 八节点流程，
    提供统一的任务状态管理。

    注意: 推荐使用 engine.models.TaskPhase 代替此模块。

    Features:
    - 严格的状态转换验证
    - 完整的转换历史记录
    - CyberTeam节点进度跟踪
    - 质量评分集成
    - 回调钩子支持
    - 异步事件支持
    """

    def __init__(
        self,
        initial_state: TaskState | None = None,
        on_transition: Callable[[StateTransition], None] | None = None,
        on_state_change: Callable[[TaskState, EdictState], None] | None = None,
    ):
        """
        初始化状态机

        Args:
            initial_state: 初始任务状态
            on_transition: 状态转换回调 (transition: StateTransition) -> None
            on_state_change: 状态变更回调 (state: TaskState, new_state: EdictState) -> None
        """
        self._state = initial_state or TaskState(task_id=str(uuid.uuid4())[:8], trace_id="")
        self._on_transition = on_transition
        self._on_state_change = on_state_change
        self._lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None

    def sync_init(self):
        """同步初始化锁 (用于非异步场景)"""
        if self._lock is None:
            self._lock = asyncio.Lock()

    @property
    def state(self) -> TaskState:
        """获取当前状态"""
        return self._state

    def get_state(self) -> EdictState:
        """获取当前状态值"""
        return self._state.state

    def get_node(self) -> Optional[CyberTeamNode]:
        """获取当前处理的CyberTeam节点"""
        return self._state.current_node

    def transition(
        self,
        to_state: EdictState,
        reason: TransitionReason,
        triggered_by: str = "system",
        metadata: dict | None = None,
    ) -> StateTransition:
        """
        执行状态转换

        Args:
            to_state: 目标状态
            reason: 转换原因
            triggered_by: 触发者 (Agent ID)
            metadata: 额外元数据

        Returns:
            StateTransition: 转换记录

        Raises:
            InvalidTransitionError: 无效转换
        """
        if not self._state.can_transition_to(to_state):
            raise InvalidTransitionError(
                f"Invalid transition from {self._state.state.value} to {to_state.value}. "
                f"Allowed: {[s.value for s in STATE_TRANSITIONS.get(self._state.state, set())]}"
            )

        from_state = self._state.state

        # 创建转换记录
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            reason=reason,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )

        # 更新状态
        self._state.state = to_state
        self._state.updated_at = datetime.now()

        # 更新当前节点映射
        if to_state in EDICT_TO_CYBERTEAM_NODE_MAP:
            new_node = EDICT_TO_CYBERTEAM_NODE_MAP[to_state]
            if self._state.current_node != new_node:
                if self._state.current_node:
                    self._state.completed_nodes.append(self._state.current_node)
                self._state.current_node = new_node
                self._state.active_node = new_node

        # 记录转换
        self._state.transitions.append(transition)

        # 处理终态
        if self._state.is_terminal_state():
            self._state.completed_at = datetime.now()
            self._state.active_node = None

        logger.info(
            f"Task {self._state.task_id}: {from_state.value} -> {to_state.value} "
            f"(reason: {reason.value}, by: {triggered_by})"
        )

        # 触发回调
        if self._on_transition:
            self._on_transition(transition)
        if self._on_state_change:
            self._on_state_change(self._state, to_state)

        return transition

    def assign_agent(self, role: str, agent_id: str) -> None:
        """
        分配Agent到特定角色 (Legacy - 已废弃)

        Args:
            role: 角色名 (intake/draft/review/dispatch 或部门名)
            agent_id: Agent ID
        """
        if role == "prince":
            self._state.prince_agent = agent_id
        elif role == "zhongshu":
            self._state.zhongshu_agent = agent_id
        elif role == "menxia":
            self._state.menxia_agent = agent_id
        elif role == "shangshu":
            self._state.shangshu_agent = agent_id
        elif role in ["libu", "hubu", "bingbu", "xingbu", "gongbu", "libu_hr"]:
            self._state.six_ministries[role] = agent_id
        else:
            logger.warning(f"Unknown role: {role}")

    def record_node_result(self, node: CyberTeamNode, result: dict) -> None:
        """
        记录CyberTeam节点处理结果

        Args:
            node: 节点
            result: 处理结果
        """
        self._state.node_results[node] = result

    def set_score(self, total: float, breakdown: Dict[str, float]) -> None:
        """
        设置质量评分

        Args:
            total: 总分
            breakdown: 分项得分
        """
        self._state.score = total
        self._state.score_breakdown = breakdown

    def get_progress(self) -> dict:
        """
        获取任务进度

        Returns:
            dict: 进度信息
        """
        completed_count = len(self._state.completed_nodes)
        total_count = len(CYBERTEAM_NODE_ORDER)

        return {
            "task_id": self._state.task_id,
            "state": self._state.state.value,
            "state_name": STATE_METADATA.get(self._state.state, {}).get("name", ""),
            "current_node": self._state.current_node.value if self._state.current_node else None,
            "completed_nodes": completed_count,
            "total_nodes": total_count,
            "progress_percent": (completed_count / total_count * 100) if total_count > 0 else 0,
            "is_terminal": self._state.is_terminal_state(),
            "score": self._state.score,
        }

    def get_flow_summary(self) -> list[dict]:
        """
        获取流程摘要

        Returns:
            list[dict]: 转换历史摘要
        """
        return [
            {
                "from": t.from_state.value,
                "to": t.to_state.value,
                "reason": t.reason.value,
                "at": t.timestamp.strftime("%H:%M:%S"),
            }
            for t in self._state.transitions
        ]

    def to_dict(self) -> dict:
        """转换为字典"""
        return self._state.to_dict()


# 便捷函数

def create_task_state(
    task_id: Optional[str] = None,
    title: str = "",
    description: str = "",
    user_input: str = "",
    priority: str = "中",
) -> TaskState:
    """
    创建任务状态

    Args:
        task_id: 任务ID
        title: 标题
        description: 描述
        user_input: 用户输入
        priority: 优先级

    Returns:
        TaskState: 任务状态
    """
    return TaskState(
        task_id=task_id or str(uuid.uuid4())[:8],
        trace_id=f"trace-{task_id or str(uuid.uuid4())[:8]}",
        title=title,
        description=description,
        user_input=user_input,
        priority=priority,
    )


def create_state_machine(
    task_id: Optional[str] = None,
    title: str = "",
    description: str = "",
    user_input: str = "",
    priority: str = "中",
) -> StateMachine:
    """
    创建状态机

    Args:
        task_id: 任务ID
        title: 标题
        description: 描述
        user_input: 用户输入
        priority: 优先级

    Returns:
        StateMachine: 状态机实例
    """
    task_state = create_task_state(task_id, title, description, user_input, priority)
    return StateMachine(initial_state=task_state)


# 导出
__all__ = [
    # 枚举
    "EdictState",
    "CyberTeamNode",
    "TransitionReason",
    # 数据类
    "StateTransition",
    "TaskState",
    # 异常
    "StateMachineError",
    "InvalidTransitionError",
    # 主类
    "StateMachine",
    # 工具函数
    "create_task_state",
    "create_state_machine",
    # 常量
    "STATE_TRANSITIONS",
    "STATE_METADATA",
    "EDICT_TO_CYBERTEAM_NODE_MAP",
    "CYBERTEAM_NODE_ORDER",
]
