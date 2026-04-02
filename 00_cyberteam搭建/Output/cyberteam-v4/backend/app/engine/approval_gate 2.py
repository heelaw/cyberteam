"""审批门控 - Human-in-the-loop

高危操作审批门控系统：
- 四级审批流（自动/部门总监/COO/CEO）
- 预置高危动作规则
- 支持 bypass（紧急情况 CEO 直接通过）
"""

import uuid
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


class ApprovalLevel(Enum):
    """审批级别"""
    AUTO = 0      # 自动通过
    LOW = 1       # 部门总监审批
    MEDIUM = 2    # COO 审批
    HIGH = 3      # CEO 审批


class ApprovalStatus(Enum):
    """审批状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BYPASSED = "bypassed"   # CEO 直接通过


@dataclass
class ApprovalRule:
    """审批规则"""
    action_pattern: str      # 正则表达式，如 "DELETE.*"
    level: ApprovalLevel
    description: str


@dataclass
class ApprovalRequest:
    """审批请求"""
    approval_id: str
    action: str
    level: ApprovalLevel
    context: dict
    status: ApprovalStatus = ApprovalStatus.PENDING
    requester: str = "system"
    approver: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "approval_id": self.approval_id,
            "action": self.action,
            "level": self.level.name,
            "context": self.context,
            "status": self.status.value,
            "requester": self.requester,
            "approver": self.approver,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "reason": self.reason,
        }


class ApprovalGate:
    """
    审批门控

    高危操作拦截，等待人工审批：
    - 四级审批流（自动/部门总监/COO/CEO）
    - 支持 bypass（紧急情况 CEO 直接通过）
    """

    # 预置高危动作规则
    # 注意：规则按优先级从高到低排列，更具体的模式放在前面
    DEFAULT_RULES = [
        ApprovalRule(r"DELETE_PROJECT", ApprovalLevel.HIGH, "删除项目需 CEO 审批"),
        ApprovalRule(r"EXECUTE_SQL", ApprovalLevel.HIGH, "SQL 执行需 CEO 审批"),
        ApprovalRule(r"MODIFY_BUDGET", ApprovalLevel.HIGH, "预算修改需 CEO 审批"),
        ApprovalRule(r"DELETE.*", ApprovalLevel.MEDIUM, "删除操作需 COO 审批"),
        ApprovalRule(r"SEND_EXTERNAL.*", ApprovalLevel.MEDIUM, "外部发送需 COO 审批"),
        ApprovalRule(r"DEPLOY_PRODUCTION.*", ApprovalLevel.MEDIUM, "生产部署需 COO 审批"),
    ]

    def __init__(self):
        self._rules: list[ApprovalRule] = list(self.DEFAULT_RULES)
        self._pending: dict[str, ApprovalRequest] = {}
        self._history: list[ApprovalRequest] = []

    def register_rule(self, action_pattern: str, level: ApprovalLevel, description: str = "") -> None:
        """注册新的审批规则"""
        rule = ApprovalRule(action_pattern, level, description)
        self._rules.append(rule)

    def get_required_level(self, action: str) -> ApprovalLevel:
        """获取操作需要的审批级别"""
        for rule in self._rules:
            if re.match(rule.action_pattern, action):
                return rule.level
        return ApprovalLevel.AUTO  # 默认自动通过

    async def request_approval(
        self,
        action: str,
        context: dict,
        requester: str = "system"
    ) -> ApprovalRequest:
        """发起审批请求"""
        level = self.get_required_level(action)

        if level == ApprovalLevel.AUTO:
            # 自动通过
            req = ApprovalRequest(
                approval_id=str(uuid.uuid4())[:8],
                action=action,
                level=level,
                context=context,
                requester=requester,
                status=ApprovalStatus.APPROVED,
                approver="AUTO",
                decided_at=datetime.utcnow()
            )
        else:
            req = ApprovalRequest(
                approval_id=str(uuid.uuid4())[:8],
                action=action,
                level=level,
                context=context,
                requester=requester,
                status=ApprovalStatus.PENDING
            )
            self._pending[req.approval_id] = req

        self._history.append(req)
        return req

    async def approve(self, approval_id: str, approver: str) -> bool:
        """审批通过"""
        req = self._pending.pop(approval_id, None)
        if not req:
            return False
        req.status = ApprovalStatus.APPROVED
        req.approver = approver
        req.decided_at = datetime.utcnow()
        return True

    async def reject(self, approval_id: str, approver: str, reason: str) -> bool:
        """审批拒绝"""
        req = self._pending.pop(approval_id, None)
        if not req:
            return False
        req.status = ApprovalStatus.REJECTED
        req.approver = approver
        req.reason = reason
        req.decided_at = datetime.utcnow()
        return True

    async def bypass(self, approval_id: str, ceo_user: str, reason: str) -> bool:
        """CEO bypass（紧急情况直接通过）"""
        req = self._pending.pop(approval_id, None)
        if not req:
            return False
        req.status = ApprovalStatus.BYPASSED
        req.approver = ceo_user
        req.reason = f"[BYPASS] {reason}"
        req.decided_at = datetime.utcnow()
        return True

    def get_pending(self, min_level: Optional[ApprovalLevel] = None) -> list[ApprovalRequest]:
        """获取待审批请求"""
        pending = list(self._pending.values())
        if min_level:
            pending = [r for r in pending if r.level.value >= min_level.value]
        return sorted(pending, key=lambda r: r.created_at)

    def is_action_blocked(self, action: str) -> bool:
        """检查操作是否被阻止（需要审批且未通过）"""
        level = self.get_required_level(action)
        if level == ApprovalLevel.AUTO:
            return False
        # 检查是否有未完成的审批请求
        for req in self._pending.values():
            if req.action == action:
                return True
        return False

    def get_history(self) -> list[ApprovalRequest]:
        """获取审批历史"""
        return list(self._history)


# 全局单例
_approval_gate: Optional[ApprovalGate] = None


def get_approval_gate() -> ApprovalGate:
    """获取审批门控单例"""
    global _approval_gate
    if _approval_gate is None:
        _approval_gate = ApprovalGate()
    return _approval_gate


__all__ = [
    "ApprovalLevel",
    "ApprovalStatus",
    "ApprovalRule",
    "ApprovalRequest",
    "ApprovalGate",
    "get_approval_gate",
]
