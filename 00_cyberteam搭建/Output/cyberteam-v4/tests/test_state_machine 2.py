"""
CyberTeam V4 - 状态机测试
覆盖: engine/state_machine.py

测试范围：
- EdictState / CyberTeamState: 枚举值正确
- StateTransition: 转换记录
- TaskState: 任务状态（state=EdictState, current_node=CyberTeamNode）
- StateMachine: transition(get_state/get_node/转换验证)
- STATE_TRANSITIONS: 合法的状态转换规则
- CYBERTEAM_NODE_ORDER: 八节点顺序
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))

from engine.state_machine import (
    EdictState,
    CyberTeamState,
    CyberTeamNode,
    TransitionReason,
    StateTransition,
    TaskState,
    StateMachine,
    InvalidTransitionError,
    STATE_TRANSITIONS,
    CYBERTEAM_NODE_ORDER,
)


class TestEdictState:
    """EdictState 枚举测试"""

    def test_pending_exists(self):
        assert EdictState.PENDING.value == "pending"

    def test_terminal_states_exist(self):
        assert EdictState.DONE.value == "done"
        assert EdictState.CANCELLED.value == "cancelled"
        assert EdictState.FAILED.value == "failed"
        assert EdictState.TIMEOUT.value == "timeout"

    def test_flow_states_exist(self):
        assert EdictState.TAIZI.value == "taizi"
        assert EdictState.ZHONGSHU.value == "zhongshu"
        assert EdictState.MENXIA.value == "menxia"
        assert EdictState.ASSIGNED.value == "assigned"
        assert EdictState.DOING.value == "doing"
        assert EdictState.REVIEW.value == "review"


class TestCyberTeamState:
    """CyberTeamState 枚举测试"""

    def test_pending_exists(self):
        assert CyberTeamState.PENDING.value == "pending"

    def test_terminal_states_exist(self):
        assert CyberTeamState.DONE.value == "done"
        assert CyberTeamState.CANCELLED.value == "cancelled"
        assert CyberTeamState.FAILED.value == "failed"
        assert CyberTeamState.TIMEOUT.value == "timeout"

    def test_ceo_route_exists(self):
        assert CyberTeamState.CEO_ROUTE.value == "ceo_route"

    def test_coo_coordination_exists(self):
        assert CyberTeamState.COO_COORDINATION.value == "coo_coordination"

    def test_from_edict_state_mapping(self):
        assert CyberTeamState.from_edict_state(EdictState.TAIZI) == CyberTeamState.CEO_ROUTE
        assert CyberTeamState.from_edict_state(EdictState.ZHONGSHU) == CyberTeamState.COO_COORDINATION
        assert CyberTeamState.from_edict_state(EdictState.DONE) == CyberTeamState.DONE


class TestCyberTeamNode:
    """CyberTeamNode 枚举测试"""

    def test_all_eight_nodes_exist(self):
        assert CyberTeamNode.CEO_ROUTER.value == "ceo_router"
        assert CyberTeamNode.STRATEGY.value == "strategy"
        assert CyberTeamNode.PM_COORD.value == "pm_coord"
        assert CyberTeamNode.DEPT_EXEC.value == "dept_exec"
        assert CyberTeamNode.DEBATE.value == "debate"
        assert CyberTeamNode.SCORING.value == "scoring"
        assert CyberTeamNode.QUALITY_GATE.value == "quality_gate"
        assert CyberTeamNode.SWARM.value == "swarm"

    def test_node_order_has_eight_items(self):
        assert len(CYBERTEAM_NODE_ORDER) == 8
        assert CYBERTEAM_NODE_ORDER[0] == CyberTeamNode.CEO_ROUTER
        assert CYBERTEAM_NODE_ORDER[-1] == CyberTeamNode.SWARM


class TestTransitionReason:
    """TransitionReason 枚举测试"""

    def test_divine_order_exists(self):
        assert TransitionReason.DIVINE_ORDER.value == "divine_order"

    def test_ceo_route_received_exists(self):
        assert TransitionReason.CEO_ROUTE_RECEIVED.value == "ceo_route_received"

    def test_terminal_reasons_exist(self):
        assert TransitionReason.CANCELLED.value == "cancelled"
        assert TransitionReason.FAILED.value == "failed"
        assert TransitionReason.TIMEOUT.value == "timeout"


class TestStateTransition:
    """StateTransition 转换记录测试"""

    def test_create_with_all_fields(self):
        t = StateTransition(
            from_state=EdictState.PENDING,
            to_state=EdictState.TAIZI,
            reason=TransitionReason.DIVINE_ORDER,
            triggered_by="user",
            metadata={"session_id": "sess-001"},
        )
        assert t.from_state == EdictState.PENDING
        assert t.to_state == EdictState.TAIZI
        assert t.reason == TransitionReason.DIVINE_ORDER
        assert t.triggered_by == "user"
        assert t.metadata["session_id"] == "sess-001"
        assert t.timestamp is not None

    def test_to_dict(self):
        t = StateTransition(
            from_state=EdictState.TAIZI,
            to_state=EdictState.ZHONGSHU,
            reason=TransitionReason.CEO_ROUTE_RECEIVED,
            triggered_by="CEO",
        )
        d = t.to_dict()
        assert d["from_state"] == "taizi"
        assert d["to_state"] == "zhongshu"
        assert d["reason"] == "ceo_route_received"
        assert d["triggered_by"] == "CEO"


class TestTaskState:
    """TaskState 任务状态测试"""

    def test_initial_state_is_pending(self):
        ts = TaskState(task_id="task-001", trace_id="trace-001")
        assert ts.state == EdictState.PENDING
        assert ts.task_id == "task-001"

    def test_auto_uuid_if_empty(self):
        ts = TaskState(task_id="", trace_id="")
        assert ts.task_id != ""
        assert ts.trace_id != ""

    def test_set_active_node(self):
        ts = TaskState(task_id="task-002", trace_id="trace-002")
        ts.active_node = CyberTeamNode.CEO_ROUTER
        assert ts.active_node == CyberTeamNode.CEO_ROUTER

    def test_add_completed_node(self):
        ts = TaskState(task_id="task-003", trace_id="trace-003")
        ts.completed_nodes = [CyberTeamNode.CEO_ROUTER]
        assert CyberTeamNode.CEO_ROUTER in ts.completed_nodes

    def test_set_score(self):
        ts = TaskState(task_id="task-004", trace_id="trace-004")
        ts.score = 0.92
        ts.score_breakdown = {"completeness": 0.9, "quality": 0.95}
        assert ts.score == 0.92
        assert ts.score_breakdown["completeness"] == 0.9

    def test_is_terminal_state(self):
        ts = TaskState(task_id="task-005", trace_id="trace-005")
        assert ts.is_terminal_state() is False
        ts.state = EdictState.DONE
        assert ts.is_terminal_state() is True
        ts.state = EdictState.FAILED
        assert ts.is_terminal_state() is True

    def test_can_transition_to(self):
        ts = TaskState(task_id="task-006", trace_id="trace-006")
        # PENDING -> TAIZI is valid
        assert ts.can_transition_to(EdictState.TAIZI) is True
        # PENDING -> DONE is invalid
        assert ts.can_transition_to(EdictState.DONE) is False

    def test_get_next_cyberteam_node(self):
        """get_next_cyberteam_node 使用 current_node（不是 active_node）"""
        ts = TaskState(task_id="task-007", trace_id="trace-007")
        ts.current_node = CyberTeamNode.CEO_ROUTER
        next_node = ts.get_next_cyberteam_node()
        assert next_node == CyberTeamNode.STRATEGY

    def test_get_next_cyberteam_node_at_end(self):
        """current_node=SWARM 时返回 None"""
        ts = TaskState(task_id="task-008", trace_id="trace-008")
        ts.current_node = CyberTeamNode.SWARM
        next_node = ts.get_next_cyberteam_node()
        assert next_node is None

    def test_to_dict(self):
        ts = TaskState(task_id="task-009", trace_id="trace-009", title="测试任务")
        ts.state = EdictState.TAIZI
        d = ts.to_dict()
        assert d["task_id"] == "task-009"
        assert d["state"] == "taizi"
        assert d["title"] == "测试任务"
        assert "transitions" in d

    def test_get_current_department(self):
        ts = TaskState(task_id="task-010", trace_id="trace-010")
        ts.state = EdictState.DOING
        dept = ts.get_current_department()
        assert dept == "Execute"


class TestStateTransitions:
    """STATE_TRANSITIONS 合法的状态转换规则测试"""

    def test_pending_can_go_to_taizi(self):
        assert EdictState.TAIZI in STATE_TRANSITIONS.get(EdictState.PENDING, set())

    def test_taizi_can_go_to_zhongshu(self):
        assert EdictState.ZHONGSHU in STATE_TRANSITIONS.get(EdictState.TAIZI, set())

    def test_taizi_can_be_cancelled(self):
        assert EdictState.CANCELLED in STATE_TRANSITIONS.get(EdictState.TAIZI, set())

    def test_doing_can_fail(self):
        assert EdictState.FAILED in STATE_TRANSITIONS.get(EdictState.DOING, set())

    def test_doing_can_timeout(self):
        assert EdictState.TIMEOUT in STATE_TRANSITIONS.get(EdictState.DOING, set())

    def test_done_is_terminal(self):
        assert len(STATE_TRANSITIONS.get(EdictState.DONE, set())) == 0

    def test_cancelled_is_terminal(self):
        assert len(STATE_TRANSITIONS.get(EdictState.CANCELLED, set())) == 0

    def test_review_can_go_to_multiple(self):
        """REVIEW 可以 → DONE(通过)、MENXIA(封驳)、DOING(重做)、CANCELLED(取消)"""
        review_targets = STATE_TRANSITIONS.get(EdictState.REVIEW, set())
        assert EdictState.DONE in review_targets  # 通过
        assert EdictState.MENXIA in review_targets  # 封驳
        assert EdictState.DOING in review_targets  # 重做


class TestStateMachine:
    """StateMachine 主状态机测试"""

    def test_initial_state_is_pending(self):
        sm = StateMachine()
        assert sm.get_state() == EdictState.PENDING

    def test_initial_node_is_none(self):
        sm = StateMachine()
        assert sm.get_node() is None

    def test_transition_to_taizi(self):
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER, triggered_by="user")
        assert sm.get_state() == EdictState.TAIZI

    def test_transition_records_in_state_transitions(self):
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.ZHONGSHU, TransitionReason.CEO_ROUTE_RECEIVED)
        # TaskState.transitions records the history
        assert len(sm.state.transitions) == 2

    def test_invalid_transition_raises(self):
        sm = StateMachine()
        # PENDING -> DONE is invalid
        with pytest.raises(InvalidTransitionError):
            sm.transition(EdictState.DONE, TransitionReason.DIVINE_ORDER)

    def test_taizi_to_zongshu_to_menxia(self):
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.ZHONGSHU, TransitionReason.CEO_ROUTE_RECEIVED)
        sm.transition(EdictState.MENXIA, TransitionReason.COO_PLAN_DRAFTED)
        assert sm.get_state() == EdictState.MENXIA

    def test_menxia_can_reject_back_to_zhongshu(self):
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.ZHONGSHU, TransitionReason.CEO_ROUTE_RECEIVED)
        sm.transition(EdictState.MENXIA, TransitionReason.COO_PLAN_DRAFTED)
        sm.transition(EdictState.ZHONGSHU, TransitionReason.COO_PLAN_REJECTED)
        assert sm.get_state() == EdictState.ZHONGSHU

    def test_assigned_to_doing(self):
        sm = StateMachine()
        for state in [EdictState.TAIZI, EdictState.ZHONGSHU, EdictState.MENXIA, EdictState.ASSIGNED]:
            sm.transition(state, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.DOING, TransitionReason.TASK_ASSIGNED)
        assert sm.get_state() == EdictState.DOING

    def test_invalid_transition_returns_false_no_raise(self):
        sm = StateMachine()
        # Try without raising (using TaskState directly)
        ts = TaskState(task_id="t1", trace_id="tr1")
        assert ts.can_transition_to(EdictState.DONE) is False

    def test_state_machine_stores_transitions_in_task_state(self):
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER, triggered_by="user")
        sm.transition(EdictState.ZHONGSHU, TransitionReason.CEO_ROUTE_RECEIVED)
        assert len(sm.state.transitions) == 2
        assert sm.state.transitions[0].from_state == EdictState.PENDING
        assert sm.state.transitions[0].to_state == EdictState.TAIZI
        assert sm.state.transitions[0].triggered_by == "user"

    def test_callback_on_transition(self):
        callback_events = []
        def on_transition(t: StateTransition):
            callback_events.append(t.to_state)

        sm = StateMachine(on_transition=on_transition)
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        assert EdictState.TAIZI in callback_events

    def test_callback_on_state_change(self):
        old_states = []
        def on_state_change(ts, new_state):
            old_states.append(new_state)

        sm = StateMachine(on_state_change=on_state_change)
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        assert EdictState.TAIZI in old_states


class TestStateMachineEdgeCases:
    """状态机边界条件测试"""

    def test_full_lifecycle_pending_to_done(self):
        """完整的正常流程: PENDING → TAIZI → ZHONGSHU → MENXIA → ASSIGNED → DOING → REVIEW → DONE"""
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.ZHONGSHU, TransitionReason.CEO_ROUTE_RECEIVED)
        sm.transition(EdictState.MENXIA, TransitionReason.COO_PLAN_DRAFTED)
        sm.transition(EdictState.ASSIGNED, TransitionReason.COO_PLAN_APPROVED)
        sm.transition(EdictState.DOING, TransitionReason.TASK_ASSIGNED)
        sm.transition(EdictState.REVIEW, TransitionReason.EXECUTION_COMPLETE)
        sm.transition(EdictState.DONE, TransitionReason.CEO_APPROVAL_COMPLETE)
        assert sm.get_state() == EdictState.DONE

    def test_cancelled_at_any_stage(self):
        """TAIZI 阶段可以被取消"""
        sm = StateMachine()
        sm.transition(EdictState.TAIZI, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.CANCELLED, TransitionReason.CANCELLED)
        assert sm.get_state() == EdictState.CANCELLED

    def test_failed_during_execution(self):
        """DOING 阶段可能失败"""
        sm = StateMachine()
        for s in [EdictState.TAIZI, EdictState.ZHONGSHU, EdictState.MENXIA,
                  EdictState.ASSIGNED, EdictState.DOING]:
            sm.transition(s, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.FAILED, TransitionReason.FAILED)
        assert sm.get_state() == EdictState.FAILED

    def test_timeout_during_execution(self):
        """DOING 阶段可能超时"""
        sm = StateMachine()
        for s in [EdictState.TAIZI, EdictState.ZHONGSHU, EdictState.MENXIA,
                  EdictState.ASSIGNED, EdictState.DOING]:
            sm.transition(s, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.TIMEOUT, TransitionReason.TIMEOUT)
        assert sm.get_state() == EdictState.TIMEOUT

    def test_review_can_return_to_doing(self):
        """REVIEW 阶段可以退回重做"""
        sm = StateMachine()
        for s in [EdictState.TAIZI, EdictState.ZHONGSHU, EdictState.MENXIA,
                  EdictState.ASSIGNED, EdictState.DOING, EdictState.REVIEW]:
            sm.transition(s, TransitionReason.DIVINE_ORDER)
        sm.transition(EdictState.DOING, TransitionReason.REVIEW_COMPLETE)
        assert sm.get_state() == EdictState.DOING

    def test_custom_task_state_initial(self):
        """StateMachine 接受自定义 TaskState 作为初始状态"""
        ts = TaskState(
            task_id="custom-task",
            trace_id="custom-trace",
            title="自定义任务",
            description="测试描述",
        )
        ts.state = EdictState.TAIZI
        ts.current_node = CyberTeamNode.STRATEGY
        sm = StateMachine(initial_state=ts)
        assert sm.get_state() == EdictState.TAIZI
        assert sm.get_node() == CyberTeamNode.STRATEGY
