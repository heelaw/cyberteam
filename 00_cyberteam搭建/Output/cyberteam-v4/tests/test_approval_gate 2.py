"""
CyberTeam V4 - ApprovalGate 审批门控测试

测试范围：
- ApprovalLevel: 枚举值正确
- ApprovalStatus: 枚举值正确
- ApprovalRule: 规则创建
- ApprovalRequest: 请求创建和状态转换
- ApprovalGate: 核心功能
  - register_rule: 注册新规则
  - get_required_level: 获取审批级别
  - request_approval: 发起审批
  - approve: 审批通过
  - reject: 审批拒绝
  - bypass: CEO bypass
  - get_pending: 获取待审批
  - is_action_blocked: 检查操作是否被阻止
  - get_history: 获取历史
- 自动通过逻辑
- 四级审批流
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root))

from backend.app.engine.approval_gate import (
    ApprovalLevel,
    ApprovalStatus,
    ApprovalRule,
    ApprovalRequest,
    ApprovalGate,
    get_approval_gate,
)


class TestApprovalLevel:
    """ApprovalLevel 枚举测试"""

    def test_auto_exists(self):
        assert ApprovalLevel.AUTO.value == 0

    def test_low_exists(self):
        assert ApprovalLevel.LOW.value == 1

    def test_medium_exists(self):
        assert ApprovalLevel.MEDIUM.value == 2

    def test_high_exists(self):
        assert ApprovalLevel.HIGH.value == 3


class TestApprovalStatus:
    """ApprovalStatus 枚举测试"""

    def test_pending_exists(self):
        assert ApprovalStatus.PENDING.value == "pending"

    def test_approved_exists(self):
        assert ApprovalStatus.APPROVED.value == "approved"

    def test_rejected_exists(self):
        assert ApprovalStatus.REJECTED.value == "rejected"

    def test_bypassed_exists(self):
        assert ApprovalStatus.BYPASSED.value == "bypassed"


class TestApprovalRule:
    """ApprovalRule 规则测试"""

    def test_create_rule(self):
        rule = ApprovalRule(
            action_pattern=r"DELETE.*",
            level=ApprovalLevel.MEDIUM,
            description="删除操作需 COO 审批"
        )
        assert rule.action_pattern == r"DELETE.*"
        assert rule.level == ApprovalLevel.MEDIUM
        assert rule.description == "删除操作需 COO 审批"


class TestApprovalRequest:
    """ApprovalRequest 请求测试"""

    def test_create_pending_request(self):
        req = ApprovalRequest(
            approval_id="test-001",
            action="DELETE_PROJECT",
            level=ApprovalLevel.HIGH,
            context={"project_id": "p-123"},
            requester="user-001"
        )
        assert req.approval_id == "test-001"
        assert req.action == "DELETE_PROJECT"
        assert req.level == ApprovalLevel.HIGH
        assert req.context == {"project_id": "p-123"}
        assert req.status == ApprovalStatus.PENDING
        assert req.requester == "user-001"
        assert req.approver is None

    def test_to_dict(self):
        req = ApprovalRequest(
            approval_id="test-002",
            action="EXECUTE_SQL",
            level=ApprovalLevel.HIGH,
            context={},
            requester="system",
            status=ApprovalStatus.APPROVED,
            approver="AUTO"
        )
        d = req.to_dict()
        assert d["approval_id"] == "test-002"
        assert d["action"] == "EXECUTE_SQL"
        assert d["level"] == "HIGH"
        assert d["status"] == "approved"
        assert d["approver"] == "AUTO"


class TestApprovalGateDefaultRules:
    """ApprovalGate 默认规则测试"""

    def test_six_default_rules(self):
        gate = ApprovalGate()
        assert len(gate._rules) == 6

    def test_delete_rule_medium(self):
        gate = ApprovalGate()
        assert gate.get_required_level("DELETE_USER") == ApprovalLevel.MEDIUM
        assert gate.get_required_level("DELETE_ACCOUNT") == ApprovalLevel.MEDIUM

    def test_execute_sql_rule_high(self):
        gate = ApprovalGate()
        assert gate.get_required_level("EXECUTE_SQL") == ApprovalLevel.HIGH

    def test_send_external_rule_medium(self):
        gate = ApprovalGate()
        assert gate.get_required_level("SEND_EXTERNAL") == ApprovalLevel.MEDIUM

    def test_modify_budget_rule_high(self):
        gate = ApprovalGate()
        assert gate.get_required_level("MODIFY_BUDGET") == ApprovalLevel.HIGH

    def test_deploy_production_rule_medium(self):
        gate = ApprovalGate()
        assert gate.get_required_level("DEPLOY_PRODUCTION") == ApprovalLevel.MEDIUM

    def test_delete_project_rule_high(self):
        gate = ApprovalGate()
        assert gate.get_required_level("DELETE_PROJECT") == ApprovalLevel.HIGH

    def test_unknown_action_auto(self):
        gate = ApprovalGate()
        assert gate.get_required_level("UNKNOWN_ACTION") == ApprovalLevel.AUTO


class TestApprovalGateRuleRegistration:
    """审批规则注册测试"""

    def test_register_new_rule(self):
        gate = ApprovalGate()
        initial_count = len(gate._rules)
        gate.register_rule(r"NEW_ACTION.*", ApprovalLevel.LOW, "新操作规则")
        assert len(gate._rules) == initial_count + 1
        assert gate.get_required_level("NEW_ACTION_TEST") == ApprovalLevel.LOW

    def test_register_rule_override(self):
        """注册同名模式规则，后者优先级更高（按注册顺序）"""
        gate = ApprovalGate()
        # DELETE.* 默认是 MEDIUM，现在注册一个更高级别
        gate.register_rule(r"DELETE.*", ApprovalLevel.HIGH, "更高优先级的删除规则")
        # 因为是按顺序匹配，第一个匹配到的是 MEDIUM
        assert gate.get_required_level("DELETE_USER") == ApprovalLevel.MEDIUM


class TestApprovalGateAutoApproval:
    """自动通过逻辑测试"""

    @pytest.mark.asyncio
    async def test_auto_approve_safe_action(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="SAFE_ACTION",
            context={},
            requester="system"
        )
        assert req.status == ApprovalStatus.APPROVED
        assert req.approver == "AUTO"
        assert req.decided_at is not None

    @pytest.mark.asyncio
    async def test_auto_approve_creates_history(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="SAFE_ACTION",
            context={},
            requester="system"
        )
        history = gate.get_history()
        assert len(history) == 1
        assert history[0].approval_id == req.approval_id


class TestApprovalGatePending:
    """待审批请求测试"""

    @pytest.mark.asyncio
    async def test_high_risk_action_pending(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="DELETE_PROJECT",
            context={"project_id": "p-123"},
            requester="user-001"
        )
        assert req.status == ApprovalStatus.PENDING
        assert req.level == ApprovalLevel.HIGH
        assert req.approval_id is not None

    @pytest.mark.asyncio
    async def test_pending_request_in_pending_list(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="DELETE_PROJECT",
            context={},
            requester="user-001"
        )
        pending = gate.get_pending()
        assert len(pending) == 1
        assert pending[0].approval_id == req.approval_id

    @pytest.mark.asyncio
    async def test_get_pending_filter_by_level(self):
        gate = ApprovalGate()
        # DELETE_PROJECT = HIGH, DEPLOY_PRODUCTION = MEDIUM
        req1 = await gate.request_approval(action="DELETE_PROJECT", context={})
        req2 = await gate.request_approval(action="DEPLOY_PRODUCTION", context={})

        pending_high = gate.get_pending(min_level=ApprovalLevel.HIGH)
        assert len(pending_high) == 1
        assert pending_high[0].action == "DELETE_PROJECT"

        pending_medium = gate.get_pending(min_level=ApprovalLevel.MEDIUM)
        assert len(pending_medium) == 2


class TestApprovalGateApprove:
    """审批通过测试"""

    @pytest.mark.asyncio
    async def test_approve_pending_request(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="DELETE_PROJECT",
            context={},
            requester="user-001"
        )
        approval_id = req.approval_id

        success = await gate.approve(approval_id, "COO")
        assert success is True

        # 不在 pending 中了
        pending = gate.get_pending()
        assert len(pending) == 0

        # 历史中状态是 APPROVED
        history = gate.get_history()
        approved = [r for r in history if r.approval_id == approval_id][0]
        assert approved.status == ApprovalStatus.APPROVED
        assert approved.approver == "COO"

    @pytest.mark.asyncio
    async def test_approve_nonexistent_returns_false(self):
        gate = ApprovalGate()
        success = await gate.approve("nonexistent-id", "COO")
        assert success is False


class TestApprovalGateReject:
    """审批拒绝测试"""

    @pytest.mark.asyncio
    async def test_reject_pending_request(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="DELETE_PROJECT",
            context={},
            requester="user-001"
        )
        approval_id = req.approval_id

        success = await gate.reject(approval_id, "CEO", "风险太高")
        assert success is True

        pending = gate.get_pending()
        assert len(pending) == 0

        history = gate.get_history()
        rejected = [r for r in history if r.approval_id == approval_id][0]
        assert rejected.status == ApprovalStatus.REJECTED
        assert rejected.approver == "CEO"
        assert rejected.reason == "风险太高"

    @pytest.mark.asyncio
    async def test_reject_nonexistent_returns_false(self):
        gate = ApprovalGate()
        success = await gate.reject("nonexistent-id", "CEO", "reason")
        assert success is False


class TestApprovalGateBypass:
    """CEO bypass 测试"""

    @pytest.mark.asyncio
    async def test_bypass_pending_request(self):
        gate = ApprovalGate()
        req = await gate.request_approval(
            action="DELETE_PROJECT",
            context={},
            requester="user-001"
        )
        approval_id = req.approval_id

        success = await gate.bypass(approval_id, "CEO_WANG", "紧急情况")
        assert success is True

        pending = gate.get_pending()
        assert len(pending) == 0

        history = gate.get_history()
        bypassed = [r for r in history if r.approval_id == approval_id][0]
        assert bypassed.status == ApprovalStatus.BYPASSED
        assert bypassed.approver == "CEO_WANG"
        assert "[BYPASS] 紧急情况" in bypassed.reason

    @pytest.mark.asyncio
    async def test_bypass_nonexistent_returns_false(self):
        gate = ApprovalGate()
        success = await gate.bypass("nonexistent-id", "CEO", "reason")
        assert success is False


class TestApprovalGateBlocked:
    """操作阻止检查测试"""

    @pytest.mark.asyncio
    async def test_safe_action_not_blocked(self):
        gate = ApprovalGate()
        assert gate.is_action_blocked("SAFE_ACTION") is False

    @pytest.mark.asyncio
    async def test_high_risk_action_blocked(self):
        gate = ApprovalGate()
        assert gate.is_action_blocked("DELETE_PROJECT") is False  # 未发起审批

        await gate.request_approval(action="DELETE_PROJECT", context={})
        assert gate.is_action_blocked("DELETE_PROJECT") is True

    @pytest.mark.asyncio
    async def test_after_approval_not_blocked(self):
        gate = ApprovalGate()
        req = await gate.request_approval(action="DELETE_PROJECT", context={})
        await gate.approve(req.approval_id, "COO")
        assert gate.is_action_blocked("DELETE_PROJECT") is False


class TestApprovalGateSingleton:
    """单例模式测试"""

    def test_get_approval_gate_returns_singleton(self):
        gate1 = get_approval_gate()
        gate2 = get_approval_gate()
        assert gate1 is gate2
