"""
CyberTeam V4 - Handoff 协议测试
覆盖: engine/department/handoff.py

测试范围：
- HandoffStateMachine: 状态转换、终态判断、历史记录
- HandoffValidator: 上下文验证（需要 task_title + task_description）
- HandoffManager: initiate / accept / complete / fail 生命周期
- HandoffMessage: 序列化
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))

from engine.department.handoff import (
    HandoffState,
    HandoffMessage,
    HandoffValidator,
    HandoffStateMachine,
    HandoffManager,
)


class TestHandoffStateMachine:
    """HandoffStateMachine 状态机测试"""

    def test_initial_state_is_idle(self):
        sm = HandoffStateMachine()
        assert sm.state == HandoffState.IDLE
        assert not sm.is_terminal()

    def test_transition_to_pending(self):
        sm = HandoffStateMachine()
        assert sm.can_transition(HandoffState.PENDING) is True
        assert sm.transition(HandoffState.PENDING) is True
        assert sm.state == HandoffState.PENDING
        assert len(sm.history) == 1  # initial (appended on transition)

    def test_transition_to_active_from_pending(self):
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        assert sm.can_transition(HandoffState.ACTIVE) is True
        assert sm.transition(HandoffState.ACTIVE) is True
        assert sm.state == HandoffState.ACTIVE

    def test_transition_to_completed_from_active(self):
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        sm.transition(HandoffState.ACTIVE)
        assert sm.can_transition(HandoffState.COMPLETED) is True
        assert sm.transition(HandoffState.COMPLETED) is True
        assert sm.state == HandoffState.COMPLETED
        assert sm.is_terminal()

    def test_transition_to_failed_from_active(self):
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        sm.transition(HandoffState.ACTIVE)
        assert sm.transition(HandoffState.FAILED) is True
        assert sm.state == HandoffState.FAILED
        assert sm.is_terminal()

    def test_cancelled_is_terminal(self):
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        assert sm.transition(HandoffState.CANCELLED) is True
        assert sm.is_terminal()

    def test_invalid_transition_returns_false(self):
        sm = HandoffStateMachine()
        # Cannot go IDLE -> COMPLETED directly
        assert sm.can_transition(HandoffState.COMPLETED) is False
        assert sm.transition(HandoffState.COMPLETED) is False
        assert sm.state == HandoffState.IDLE

    def test_idle_cannot_go_to_active_directly(self):
        sm = HandoffStateMachine()
        assert sm.can_transition(HandoffState.ACTIVE) is False
        assert sm.transition(HandoffState.ACTIVE) is False

    def test_reset_to_idle(self):
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        sm.transition(HandoffState.ACTIVE)
        sm.reset()
        assert sm.state == HandoffState.IDLE
        assert sm.is_terminal() is False

    def test_history_appends_on_transition(self):
        sm = HandoffStateMachine()
        sm.transition(HandoffState.PENDING)
        sm.transition(HandoffState.ACTIVE)
        # history contains previous states
        assert HandoffState.IDLE in sm.history
        assert HandoffState.PENDING in sm.history
        assert len(sm.history) == 2


class TestHandoffMessage:
    """HandoffMessage 序列化测试"""

    def test_to_dict_basic(self):
        msg = HandoffMessage(
            handoff_id="hd-001",
            from_agent="CEO",
            to_agent="COO",
            task_id="task-001",
            context={"task_title": "测试", "task_description": "测试任务"},
        )
        d = msg.to_dict()
        assert d["handoff_id"] == "hd-001"
        assert d["from_agent"] == "CEO"
        assert d["to_agent"] == "COO"
        assert d["task_id"] == "task-001"
        assert "created_at" in d
        assert "updated_at" in d
        assert "state" in d

    def test_auto_timestamps(self):
        msg = HandoffMessage(
            handoff_id="hd-002",
            from_agent="CEO",
            to_agent="COO",
            task_id="task-002",
        )
        assert msg.created_at != ""
        assert msg.updated_at != ""


class TestHandoffValidator:
    """HandoffValidator 验证逻辑测试"""

    def test_validate_context_requires_task_title(self):
        validator = HandoffValidator()
        msg = HandoffMessage(
            handoff_id="hd-003",
            from_agent="CEO",
            to_agent="COO",
            task_id="task-003",
            context={"task_description": "desc"},
        )
        # Missing task_title
        assert validator.validate_context(msg) is False

    def test_validate_context_requires_task_description(self):
        validator = HandoffValidator()
        msg = HandoffMessage(
            handoff_id="hd-004",
            from_agent="CEO",
            to_agent="COO",
            task_id="task-004",
            context={"task_title": "title"},
        )
        # Missing task_description
        assert validator.validate_context(msg) is False

    def test_validate_context_with_both_required_fields(self):
        validator = HandoffValidator()
        msg = HandoffMessage(
            handoff_id="hd-005",
            from_agent="CEO",
            to_agent="COO",
            task_id="task-005",
            context={"task_title": "增长策略", "task_description": "制定Q2增长方案"},
        )
        assert validator.validate_context(msg) is True

    def test_validate_context_empty_dict(self):
        validator = HandoffValidator()
        msg = HandoffMessage(
            handoff_id="hd-006",
            from_agent="CEO",
            to_agent="COO",
            task_id="task-006",
            context={},
        )
        assert validator.validate_context(msg) is False

    def test_validate_agents_same_agent_blocked(self):
        validator = HandoffValidator()
        assert validator.validate_agents("CEO", "CEO") is False

    def test_validate_agents_different_allowed(self):
        validator = HandoffValidator()
        assert validator.validate_agents("CEO", "COO") is True
        assert validator.validate_agents("COO", "growth_director") is True

    def test_validate_agents_empty_blocked(self):
        validator = HandoffValidator()
        assert validator.validate_agents("", "COO") is False
        assert validator.validate_agents("CEO", "") is False

    def test_validate_prerequisites_returns_list(self):
        validator = HandoffValidator()
        prereqs = validator.validate_prerequisites("task-007")
        assert isinstance(prereqs, list)


class TestHandoffManager:
    """HandoffManager 生命周期测试"""

    def test_initiate_success(self):
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="CEO",
            to_agent="COO",
            task={
                "task_id": "task-008",
                "context": {
                    "task_title": "战略对齐",
                    "task_description": "CEO与COO战略对齐",
                },
            },
        )
        assert msg.handoff_id is not None
        assert msg.from_agent == "CEO"
        assert msg.to_agent == "COO"
        assert msg.task_id == "task-008"
        assert msg.state == HandoffState.PENDING

    def test_initiate_stores_handoff(self):
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="CEO",
            to_agent="COO",
            task={
                "task_id": "task-009",
                "context": {"task_title": "x", "task_description": "y"},
            },
        )
        stored = manager.get_handoff(msg.handoff_id)
        assert stored is not None
        assert stored.handoff_id == msg.handoff_id

    def test_initiate_same_agent_raises(self):
        manager = HandoffManager()
        with pytest.raises(ValueError, match="无效的Agent"):
            manager.initiate(
                from_agent="CEO",
                to_agent="CEO",
                task={"task_id": "task-010", "context": {"task_title": "x", "task_description": "y"}},
            )

    def test_initiate_missing_context_fields_raises(self):
        manager = HandoffManager()
        with pytest.raises(ValueError, match="上下文验证失败"):
            manager.initiate(
                from_agent="CEO",
                to_agent="COO",
                task={"task_id": "task-011", "context": {}},
            )

    def test_accept_pending_handoff(self):
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="COO",
            to_agent="growth_director",
            task={"task_id": "task-012", "context": {"task_title": "a", "task_description": "b"}},
        )
        result = manager.accept(msg.handoff_id)
        assert result is True
        assert manager.get_state(msg.handoff_id) == HandoffState.ACTIVE

    def test_accept_nonexistent_returns_false(self):
        manager = HandoffManager()
        assert manager.accept("nonexistent") is False

    def test_complete_handoff(self):
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="COO",
            to_agent="growth_director",
            task={"task_id": "task-013", "context": {"task_title": "a", "task_description": "b"}},
        )
        manager.accept(msg.handoff_id)
        result = manager.complete(msg.handoff_id, {"output": "done"})
        assert result is True
        assert manager.get_state(msg.handoff_id) == HandoffState.COMPLETED

    def test_complete_pending_without_accept_returns_false(self):
        """PENDING -> COMPLETED 不合法（需要先 ACCEPT -> ACTIVE）"""
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="COO",
            to_agent="ops",
            task={"task_id": "task-014", "context": {"task_title": "a", "task_description": "b"}},
        )
        result = manager.complete(msg.handoff_id)
        assert result is False

    def test_fail_handoff(self):
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="COO",
            to_agent="product_director",
            task={"task_id": "task-015", "context": {"task_title": "a", "task_description": "b"}},
        )
        manager.accept(msg.handoff_id)
        result = manager.fail(msg.handoff_id, "资源不可用")
        assert result is True
        assert manager.get_state(msg.handoff_id) == HandoffState.FAILED

    def test_fail_nonexistent_returns_false(self):
        manager = HandoffManager()
        assert manager.fail("fake-id", "err") is False

    def test_cancel_handoff(self):
        manager = HandoffManager()
        msg = manager.initiate(
            from_agent="CEO",
            to_agent="COO",
            task={"task_id": "task-016", "context": {"task_title": "a", "task_description": "b"}},
        )
        result = manager.cancel(msg.handoff_id, "优先级调整")
        assert result is True
        assert manager.get_state(msg.handoff_id) == HandoffState.CANCELLED

    def test_list_handoffs_all(self):
        manager = HandoffManager()
        manager.initiate("CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}})
        manager.initiate("COO", "ops", {"task_id": "t2", "context": {"task_title": "c", "task_description": "d"}})
        handoffs = manager.list_handoffs()
        assert len(handoffs) == 2

    def test_list_handoffs_by_from_agent(self):
        manager = HandoffManager()
        manager.initiate("CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}})
        manager.initiate("COO", "ops", {"task_id": "t2", "context": {"task_title": "c", "task_description": "d"}})
        ceo_handoffs = manager.list_handoffs(from_agent="CEO")
        assert len(ceo_handoffs) == 1
        assert ceo_handoffs[0].from_agent == "CEO"

    def test_list_handoffs_by_state(self):
        manager = HandoffManager()
        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.accept(msg.handoff_id)
        manager.initiate("COO", "ops", {"task_id": "t2", "context": {"task_title": "c", "task_description": "d"}})
        active = manager.list_handoffs(state=HandoffState.ACTIVE)
        pending = manager.list_handoffs(state=HandoffState.PENDING)
        assert len(active) == 1
        assert len(pending) == 1

    def test_get_pending_for_agent(self):
        manager = HandoffManager()
        manager.initiate("CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}})
        manager.initiate("CEO", "growth", {"task_id": "t2", "context": {"task_title": "c", "task_description": "d"}})
        coo_pending = manager.get_pending_for_agent("COO")
        assert len(coo_pending) == 1

    def test_cleanup_completed_respects_age_threshold(self):
        """cleanup_completed 只清理超过 max_age_hours 的记录"""
        manager = HandoffManager()
        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.accept(msg.handoff_id)
        manager.complete(msg.handoff_id)
        manager.initiate("COO", "ops", {"task_id": "t2", "context": {"task_title": "c", "task_description": "d"}})
        # 新创建的记录不足 24 小时，cleanup 不应删除
        cleaned = manager.cleanup_completed(max_age_hours=24)
        assert cleaned == 0
        assert len(manager.list_handoffs()) == 2


class TestHandoffEdgeCases:
    """边界条件测试"""

    def test_double_accept_returns_false(self):
        manager = HandoffManager()
        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.accept(msg.handoff_id)
        result = manager.accept(msg.handoff_id)
        assert result is False

    def test_complete_after_complete_returns_false(self):
        manager = HandoffManager()
        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.accept(msg.handoff_id)
        manager.complete(msg.handoff_id)
        result = manager.complete(msg.handoff_id)
        assert result is False

    def test_complete_terminal_state_returns_false(self):
        """终态不可再转换"""
        manager = HandoffManager()
        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.accept(msg.handoff_id)
        manager.complete(msg.handoff_id)
        assert manager.get_state(msg.handoff_id) == HandoffState.COMPLETED
        # COMPLETED is terminal - no further transitions
        assert manager.complete(msg.handoff_id) is False

    def test_callback_registration(self):
        manager = HandoffManager()
        callback_called = []
        def callback(hd_id, old, new):
            callback_called.append((hd_id, old, new))

        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.register_callback(msg.handoff_id, callback)
        manager.accept(msg.handoff_id)
        assert len(callback_called) == 1
        assert callback_called[0][2] == HandoffState.ACTIVE

    def test_callback_error_does_not_crash(self):
        """回调异常不应影响主流程"""
        manager = HandoffManager()
        def bad_callback(*args):
            raise RuntimeError("callback error")

        msg = manager.initiate(
            "CEO", "COO", {"task_id": "t1", "context": {"task_title": "a", "task_description": "b"}}
        )
        manager.register_callback(msg.handoff_id, bad_callback)
        # Should not raise
        result = manager.accept(msg.handoff_id)
        assert result is True
