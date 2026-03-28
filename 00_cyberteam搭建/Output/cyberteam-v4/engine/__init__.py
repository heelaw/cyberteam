"""
CyberTeam V4 Engine - 核心引擎

包含：
- CEO 路由引擎
- COO 协调引擎
- 项目管理
- 部门调度
- 策略设计
- 辩论引擎
- 思维注入
- Heartbeat 心跳保障
- Review 审核引擎
- Context 分层上下文
- Goal 目标追踪
"""

from .ceo import CEORouter, Complexity, Intent, RoutingTarget, RoutingResult
from .coo import COOCoordinator, DialogueLayer, DiscussionTopic, WorkflowState
from .coo import ExpertInvitation, DiscussionSession, COOSummary
from .coo import COOWorkflow
from .pm import PMCoordinator
from .department import DepartmentExecutor
from .strategy import StrategyEngine
from .debate import DebateEngine
from .thinking import ThinkingInjector, ThinkingRouter, ThinkingLoader

# 新增增强模块
try:
    from .heartbeat import HeartbeatEngine, HEARTBEAT
except ImportError:
    HeartbeatEngine = None
    HEARTBEAT = None

try:
    from .review import ReviewEngine, REVIEW
except ImportError:
    ReviewEngine = None
    REVIEW = None

try:
    from .context import ContextManager, CONTEXT
except ImportError:
    ContextManager = None
    CONTEXT = None

try:
    from .goal import GoalTracker, GOAL
except ImportError:
    GoalTracker = None
    GOAL = None

# 状态机模块
try:
    from .state_machine import (
        EdictState,
        CyberTeamNode,
        TransitionReason,
        StateTransition,
        TaskState,
        StateMachine,
        StateMachineError,
        InvalidTransitionError,
        create_task_state,
        create_state_machine,
        STATE_TRANSITIONS,
        STATE_METADATA,
        EDICT_TO_CYBERTEAM_NODE_MAP,
        CYBERTEAM_NODE_ORDER,
    )
except ImportError as e:
    StateMachine = None
    EdictState = None
    CyberTeamNode = None
    StateTransition = None
    TaskState = None
    StateMachineError = None
    InvalidTransitionError = None
    create_task_state = None
    create_state_machine = None
    STATE_TRANSITIONS = {}
    STATE_METADATA = {}
    EDICT_TO_CYBERTEAM_NODE_MAP = {}
    CYBERTEAM_NODE_ORDER = []

# RBAC 权限矩阵模块 (基于 Edict allowAgents)
try:
    from .rbac import (
        RBACMatrix,
        AgentLayer,
        AgentInfo,
        PermissionResult,
        check_permission,
        check_dispatch,
        get_rbac,
    )
except ImportError:
    RBACMatrix = None
    AgentLayer = None
    AgentInfo = None
    PermissionResult = None
    check_permission = None
    check_dispatch = None
    get_rbac = None

__all__ = [
    # CEO 路由引擎
    "CEORouter",
    "Complexity",
    "Intent",
    "RoutingTarget",
    "RoutingResult",
    # COO 协调引擎
    "COOCoordinator",
    "DialogueLayer",
    "DiscussionTopic",
    "WorkflowState",
    "ExpertInvitation",
    "DiscussionSession",
    "COOSummary",
    "COOWorkflow",
    # 其他引擎
    "PMCoordinator",
    "DepartmentExecutor",
    "StrategyEngine",
    "DebateEngine",
    "ThinkingInjector",
    "ThinkingRouter",
    "ThinkingLoader",
    # 新增增强模块
    "HeartbeatEngine",
    "HEARTBEAT",
    "ReviewEngine",
    "REVIEW",
    "ContextManager",
    "CONTEXT",
    "GoalTracker",
    "GOAL",
    # 状态机
    "EdictState",
    "CyberTeamNode",
    "TransitionReason",
    "StateTransition",
    "TaskState",
    "StateMachine",
    "StateMachineError",
    "InvalidTransitionError",
    "create_task_state",
    "create_state_machine",
    "STATE_TRANSITIONS",
    "STATE_METADATA",
    "EDICT_TO_CYBERTEAM_NODE_MAP",
    "CYBERTEAM_NODE_ORDER",
    # RBAC 权限矩阵
    "RBACMatrix",
    "AgentLayer",
    "AgentInfo",
    "PermissionResult",
    "check_permission",
    "check_dispatch",
    "get_rbac",
]
