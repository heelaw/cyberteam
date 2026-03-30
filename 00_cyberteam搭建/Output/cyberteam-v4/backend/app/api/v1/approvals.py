"""审批 API v1 - Human-in-the-loop 审批门控

核心功能：
- 发起审批请求
- 获取待审批列表
- 审批通过/拒绝
- CEO bypass（紧急情况直接通过）

API 路由：
- POST /api/approvals - 发起审批请求
- GET /api/approvals/pending - 获取待审批列表
- GET /api/approvals/{approval_id} - 获取审批详情
- POST /api/approvals/{approval_id}/approve - 审批通过
- POST /api/approvals/{approval_id}/reject - 审批拒绝
- POST /api/approvals/{approval_id}/bypass - CEO bypass
- GET /api/approvals/history - 获取审批历史
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...engine.approval_gate import (
    ApprovalGate,
    ApprovalLevel,
    ApprovalStatus,
    ApprovalRequest,
    get_approval_gate,
)

router = APIRouter(prefix="/approvals", tags=["approvals v1"])


# === Request/Response Models ===

class ApprovalRequestModel(BaseModel):
    """发起审批请求模型"""
    action: str = Field(..., description="操作类型，如 DELETE_PROJECT")
    context: dict = Field(default_factory=dict, description="操作上下文信息")
    requester: str = Field(default="system", description="请求者")


class ApprovalResponse(BaseModel):
    """审批响应模型"""
    approval_id: str
    action: str
    level: str
    context: dict
    status: str
    requester: str
    approver: Optional[str] = None
    created_at: str
    decided_at: Optional[str] = None
    reason: Optional[str] = None


class ApproveRequest(BaseModel):
    """审批通过请求模型"""
    approver: str = Field(..., description="审批人")


class RejectRequest(BaseModel):
    """审批拒绝请求模型"""
    approver: str = Field(..., description="审批人")
    reason: str = Field(..., description="拒绝原因")


class BypassRequest(BaseModel):
    """CEO bypass 请求模型"""
    ceo_user: str = Field(..., description="CEO 用户名")
    reason: str = Field(..., description="Bypass 原因（紧急情况）")


# === Routes ===

def _gate() -> ApprovalGate:
    """获取审批门控单例"""
    return get_approval_gate()


@router.post("", response_model=ApprovalResponse)
async def create_approval_request(
    request: ApprovalRequestModel,
):
    """发起审批请求

    根据操作类型自动判断需要的审批级别：
    - AUTO (0): 自动通过
    - LOW (1): 部门总监审批
    - MEDIUM (2): COO 审批
    - HIGH (3): CEO 审批
    """
    gate = _gate()
    result = await gate.request_approval(
        action=request.action,
        context=request.context,
        requester=request.requester,
    )

    return ApprovalResponse(
        approval_id=result.approval_id,
        action=result.action,
        level=result.level.name,
        context=result.context,
        status=result.status.value,
        requester=result.requester,
        approver=result.approver,
        created_at=result.created_at.isoformat() if result.created_at else "",
        decided_at=result.decided_at.isoformat() if result.decided_at else None,
        reason=result.reason,
    )


@router.get("/pending", response_model=List[ApprovalResponse])
async def list_pending_approvals(
    min_level: Optional[str] = None,
):
    """获取待审批列表

    Args:
        min_level: 最小审批级别过滤（如 "MEDIUM" 只显示 MEDIUM 及以上）
    """
    gate = _gate()

    level = None
    if min_level:
        try:
            level = ApprovalLevel[min_level.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid min_level: {min_level}. Valid values: AUTO, LOW, MEDIUM, HIGH"
            )

    pending = gate.get_pending(min_level=level)

    return [
        ApprovalResponse(
            approval_id=req.approval_id,
            action=req.action,
            level=req.level.name,
            context=req.context,
            status=req.status.value,
            requester=req.requester,
            approver=req.approver,
            created_at=req.created_at.isoformat() if req.created_at else "",
            decided_at=req.decided_at.isoformat() if req.decided_at else None,
            reason=req.reason,
        )
        for req in pending
    ]


@router.get("/history", response_model=List[ApprovalResponse])
async def get_approval_history(
    limit: int = 100,
):
    """获取审批历史"""
    gate = _gate()
    history = gate.get_history()[-limit:]

    return [
        ApprovalResponse(
            approval_id=req.approval_id,
            action=req.action,
            level=req.level.name,
            context=req.context,
            status=req.status.value,
            requester=req.requester,
            approver=req.approver,
            created_at=req.created_at.isoformat() if req.created_at else "",
            decided_at=req.decided_at.isoformat() if req.decided_at else None,
            reason=req.reason,
        )
        for req in history
    ]


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: str,
):
    """获取审批详情"""
    gate = _gate()

    # 先检查 pending
    for req in gate.get_pending():
        if req.approval_id == approval_id:
            return ApprovalResponse(
                approval_id=req.approval_id,
                action=req.action,
                level=req.level.name,
                context=req.context,
                status=req.status.value,
                requester=req.requester,
                approver=req.approver,
                created_at=req.created_at.isoformat() if req.created_at else "",
                decided_at=req.decided_at.isoformat() if req.decided_at else None,
                reason=req.reason,
            )

    # 再检查 history
    for req in gate.get_history():
        if req.approval_id == approval_id:
            return ApprovalResponse(
                approval_id=req.approval_id,
                action=req.action,
                level=req.level.name,
                context=req.context,
                status=req.status.value,
                requester=req.requester,
                approver=req.approver,
                created_at=req.created_at.isoformat() if req.created_at else "",
                decided_at=req.decided_at.isoformat() if req.decided_at else None,
                reason=req.reason,
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Approval not found: {approval_id}"
    )


@router.post("/{approval_id}/approve", response_model=dict)
async def approve_request(
    approval_id: str,
    request: ApproveRequest,
):
    """审批通过"""
    gate = _gate()
    success = await gate.approve(approval_id, request.approver)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending approval not found: {approval_id}"
        )

    return {"status": "ok", "approval_id": approval_id, "decision": "approved"}


@router.post("/{approval_id}/reject", response_model=dict)
async def reject_request(
    approval_id: str,
    request: RejectRequest,
):
    """审批拒绝"""
    gate = _gate()
    success = await gate.reject(approval_id, request.approver, request.reason)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending approval not found: {approval_id}"
        )

    return {"status": "ok", "approval_id": approval_id, "decision": "rejected", "reason": request.reason}


@router.post("/{approval_id}/bypass", response_model=dict)
async def bypass_request(
    approval_id: str,
    request: BypassRequest,
):
    """CEO bypass（紧急情况直接通过）

    仅 CEO 可以执行 bypass，跳过正常审批流程直接通过。
    """
    gate = _gate()
    success = await gate.bypass(approval_id, request.ceo_user, request.reason)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending approval not found: {approval_id}"
        )

    return {
        "status": "ok",
        "approval_id": approval_id,
        "decision": "bypassed",
        "reason": f"[BYPASS] {request.reason}"
    }
