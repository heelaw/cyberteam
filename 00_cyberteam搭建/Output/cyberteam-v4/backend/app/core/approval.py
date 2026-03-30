"""高危操作审批服务 - 抄 Magic。

设计理念：
- 高危操作必须经过人工审批才能执行
- Agent 发起审批请求后暂停等待
- 支持通过 WebSocket 实时推送到前端
- 审批结果记录到数据库

高危操作类型：
- delete_data: 删除数据
- send_email: 发送邮件
- publish_content: 发布内容
- budget_exceed: 超出预算
- external_api_call: 调用外部 API
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
import uuid
import logging

log = logging.getLogger("cyberteam.approval")


class ApprovalStatus(str, Enum):
    """审批状态枚举。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """审批请求对象。"""

    id: str
    task_id: str
    agent_name: str
    action_type: str
    action_detail: dict
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer_id: Optional[str] = None
    reviewer_comment: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed_at: Optional[str] = None

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "action_type": self.action_type,
            "action_detail": self.action_detail,
            "status": self.status.value,
            "reviewer_id": self.reviewer_id,
            "reviewer_comment": self.reviewer_comment,
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
        }


class ApprovalService:
    """高危操作审批服务。

    用法:
        service = ApprovalService()

        # 检查是否需要审批
        if service.is_high_risk("publish_content"):
            # 发起审批
            req = await service.request_approval(
                task_id="xxx",
                agent_name="marketing_director",
                action_type="publish_content",
                detail={"content": "...", "channel": "xiaohongshu"}
            )
            # 等待审批...
    """

    HIGH_RISK_ACTIONS = [
        "delete_data",
        "send_email",
        "publish_content",
        "budget_exceed",
        "external_api_call",
    ]

    # 审批超时时间（秒）
    DEFAULT_TIMEOUT = 300  # 5 分钟

    def __init__(self, db=None):
        """初始化审批服务。

        Args:
            db: 数据库会话（可选）
        """
        self.db = db
        self._pending: Dict[str, ApprovalRequest] = {}
        self._history: List[ApprovalRequest] = []
        self._max_history = 500

    def is_high_risk(self, action_type: str) -> bool:
        """检查操作是否为高危操作。"""
        return action_type in self.HIGH_RISK_ACTIONS

    async def request_approval(
        self,
        task_id: str,
        agent_name: str,
        action_type: str,
        detail: dict,
    ) -> ApprovalRequest:
        """发起审批请求。

        Args:
            task_id: 关联的任务ID
            agent_name: 发起审批的 Agent 名称
            action_type: 操作类型
            detail: 操作详情

        Returns:
            ApprovalRequest 审批请求对象
        """
        req = ApprovalRequest(
            id=str(uuid.uuid4()),
            task_id=task_id,
            agent_name=agent_name,
            action_type=action_type,
            action_detail=detail,
        )

        self._pending[req.id] = req
        log.info(
            f"Approval requested: {req.id} | "
            f"agent={agent_name} action={action_type} task={task_id}"
        )

        # 如果有数据库，持久化
        if self.db:
            await self._persist_request(req)

        # 通过事件总线通知
        try:
            from .events import event_bus, Event
            await event_bus.emit(Event(
                type="approval.requested",
                data=req.to_dict(),
                source="approval_service",
            ))
        except ImportError:
            pass

        return req

    async def approve(
        self,
        request_id: str,
        reviewer_id: str = "",
        comment: str = "",
    ) -> bool:
        """批准审批请求。

        Returns:
            True 表示成功，False 表示请求不存在
        """
        req = self._pending.get(request_id)
        if not req:
            log.warning(f"Approval not found: {request_id}")
            return False

        req.status = ApprovalStatus.APPROVED
        req.reviewer_id = reviewer_id
        req.reviewer_comment = comment
        req.reviewed_at = datetime.now().isoformat()

        self._move_to_history(req)
        log.info(f"Approval approved: {request_id} by {reviewer_id}")

        if self.db:
            await self._update_request(req)

        # 事件通知
        try:
            from .events import event_bus, Event
            await event_bus.emit(Event(
                type="approval.approved",
                data=req.to_dict(),
                source="approval_service",
            ))
        except ImportError:
            pass

        return True

    async def reject(
        self,
        request_id: str,
        reviewer_id: str = "",
        comment: str = "",
    ) -> bool:
        """拒绝审批请求。

        Returns:
            True 表示成功，False 表示请求不存在
        """
        req = self._pending.get(request_id)
        if not req:
            log.warning(f"Approval not found: {request_id}")
            return False

        req.status = ApprovalStatus.REJECTED
        req.reviewer_id = reviewer_id
        req.reviewer_comment = comment
        req.reviewed_at = datetime.now().isoformat()

        self._move_to_history(req)
        log.info(f"Approval rejected: {request_id} by {reviewer_id}")

        if self.db:
            await self._update_request(req)

        # 事件通知
        try:
            from .events import event_bus, Event
            await event_bus.emit(Event(
                type="approval.rejected",
                data=req.to_dict(),
                source="approval_service",
            ))
        except ImportError:
            pass

        return True

    def get_pending(self) -> List[ApprovalRequest]:
        """获取所有待审批请求。"""
        return list(self._pending.values())

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """获取指定审批请求。"""
        return self._pending.get(request_id) or self._find_in_history(request_id)

    def get_history(self, limit: int = 50) -> List[ApprovalRequest]:
        """获取审批历史。"""
        return self._history[-limit:]

    def _move_to_history(self, req: ApprovalRequest) -> None:
        """将请求从待审批移到历史记录。"""
        self._pending.pop(req.id, None)
        self._history.append(req)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def _find_in_history(self, request_id: str) -> Optional[ApprovalRequest]:
        """在历史记录中查找请求。"""
        for req in self._history:
            if req.id == request_id:
                return req
        return None

    async def _persist_request(self, req: ApprovalRequest) -> None:
        """持久化审批请求到数据库。"""
        try:
            from ..models import Approval
            record = Approval(
                id=req.id,
                task_id=req.task_id,
                agent_name=req.agent_name,
                action_type=req.action_type,
                action_detail=req.action_detail,
                status=req.status.value,
            )
            self.db.add(record)
            await self.db.commit()
        except Exception as e:
            log.error(f"Failed to persist approval request: {e}")
            if self.db:
                await self.db.rollback()

    async def _update_request(self, req: ApprovalRequest) -> None:
        """更新审批请求状态。"""
        try:
            from sqlalchemy import select
            from ..models import Approval

            stmt = select(Approval).where(Approval.id == req.id)
            result = await self.db.execute(stmt)
            record = result.scalar_one_or_none()

            if record:
                record.status = req.status.value
                record.reviewer_id = req.reviewer_id
                record.review_comment = req.reviewer_comment
                record.reviewed_at = datetime.utcnow()
                await self.db.commit()
        except Exception as e:
            log.error(f"Failed to update approval request: {e}")
            if self.db:
                await self.db.rollback()
