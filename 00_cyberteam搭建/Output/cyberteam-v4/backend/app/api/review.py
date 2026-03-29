"""Review API — 封驳审核接口。

提供 RESTful API 用于内容审核，支持：
- 关键词过滤
- 长度限制
- 格式校验
- 审核状态管理（待审核/批准/驳回/需修改）
"""

import re
import uuid
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..db import get_db
from ..models import SealRejection, ReviewStatus

log = logging.getLogger("cyberteam.api.review")
router = APIRouter()


# ── Schemas ──


class ReviewCreate(BaseModel):
    """创建审核请求。"""
    task_id: Optional[str] = Field(None, description="关联任务ID")
    content: str = Field(..., description="待审核内容")
    reviewer_agent: str = Field(default="system", description="审核Agent")
    check_keywords: Optional[List[str]] = Field(None, description="需检查的关键词列表")
    min_length: int = Field(default=0, ge=0, description="最小长度限制")
    max_length: int = Field(default=0, ge=0, description="最大长度限制")


class ReviewUpdate(BaseModel):
    """更新审核请求。"""
    rejection_reason: str = Field(..., description="驳回/修改原因")
    reviewer_agent: Optional[str] = Field(None, description="审核Agent")


class ReviewOut(BaseModel):
    """审核记录输出。"""
    id: str
    task_id: Optional[str]
    content: str
    rejection_reason: Optional[str]
    reviewer_agent: str
    status: str
    check_keywords: List[str] = []
    min_length: int
    max_length: int
    auto_passed: bool
    violations: List[str] = []
    created_at: Optional[str]
    updated_at: Optional[str]
    reviewed_at: Optional[str]

    class Config:
        from_attributes = True


class ReviewListOut(BaseModel):
    """审核列表输出。"""
    reviews: List[ReviewOut]
    count: int
    limit: int
    offset: int


class AutoCheckOut(BaseModel):
    """自动检查结果输出。"""
    passed: bool
    violations: List[str]
    content_length: int


# ── 辅助函数 ──


def _auto_review(content: str, check_keywords: Optional[List[str]], min_length: int, max_length: int) -> tuple:
    """执行自动合规检查。

    Returns:
        (passed: bool, violations: List[str])
    """
    violations = []
    content_len = len(content)

    # 长度检查
    if min_length > 0 and content_len < min_length:
        violations.append(f"内容过短（{content_len} < {min_length}字符）")
    if max_length > 0 and content_len > max_length:
        violations.append(f"内容过长（{content_len} > {max_length}字符）")

    # 关键词检查
    if check_keywords:
        for keyword in check_keywords:
            if keyword.strip() and re.search(re.escape(keyword), content, re.IGNORECASE):
                violations.append(f"命中违禁关键词：{keyword}")

    return len(violations) == 0, violations


# ── Endpoints ──


@router.get("", response_model=ReviewListOut)
async def list_reviews(
    status: Optional[str] = Query(None, description="按状态过滤"),
    task_id: Optional[str] = Query(None, description="按任务ID过滤"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """获取审核记录列表。"""
    stmt = select(SealRejection)

    if status:
        stmt = stmt.filter(SealRejection.status == status)
    if task_id:
        stmt = stmt.filter(SealRejection.task_id == task_id)

    # 总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # 分页
    stmt = stmt.order_by(SealRejection.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    reviews = result.scalars().all()

    return ReviewListOut(
        reviews=[ReviewOut(**r.to_dict()) for r in reviews],
        count=total,
        limit=limit,
        offset=offset,
    )


@router.post("", status_code=201, response_model=ReviewOut)
async def create_review(
    body: ReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建审核任务（含自动合规检查）。"""
    auto_passed, violations = _auto_review(
        body.content, body.check_keywords, body.min_length, body.max_length
    )

    review = SealRejection(
        id=str(uuid.uuid4()),
        task_id=body.task_id,
        content=body.content,
        reviewer_agent=body.reviewer_agent,
        check_keywords=body.check_keywords or [],
        min_length=body.min_length,
        max_length=body.max_length,
        auto_passed=auto_passed,
        violations=violations,
        status=ReviewStatus.PENDING,
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)

    log.info(f"Review created: {review.id}, auto_passed={auto_passed}")
    return ReviewOut(**review.to_dict())


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单条审核记录。"""
    stmt = select(SealRejection).filter(SealRejection.id == review_id)
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return ReviewOut(**review.to_dict())


@router.post("/{review_id}/approve", response_model=ReviewOut)
async def approve_review(
    review_id: str,
    body: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    """批准审核（封）。"""
    stmt = select(SealRejection).filter(SealRejection.id == review_id)
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.status != ReviewStatus.PENDING:
        raise HTTPException(status_code=400, detail="Not pending review")

    review.status = ReviewStatus.APPROVED
    review.rejection_reason = body.rejection_reason
    if body.reviewer_agent:
        review.reviewer_agent = body.reviewer_agent
    review.reviewed_at = datetime.utcnow()
    review.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    log.info(f"Review approved: {review_id}")
    return ReviewOut(**review.to_dict())


@router.post("/{review_id}/reject", response_model=ReviewOut)
async def reject_review(
    review_id: str,
    body: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    """驳回审核（驳）。"""
    stmt = select(SealRejection).filter(SealRejection.id == review_id)
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.status != ReviewStatus.PENDING:
        raise HTTPException(status_code=400, detail="Not pending review")

    review.status = ReviewStatus.REJECTED
    review.rejection_reason = body.rejection_reason
    if body.reviewer_agent:
        review.reviewer_agent = body.reviewer_agent
    review.reviewed_at = datetime.utcnow()
    review.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    log.info(f"Review rejected: {review_id}, reason={body.rejection_reason}")
    return ReviewOut(**review.to_dict())


@router.post("/{review_id}/revision", response_model=ReviewOut)
async def request_revision(
    review_id: str,
    body: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    """请求修改（发回重做）。"""
    stmt = select(SealRejection).filter(SealRejection.id == review_id)
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.status != ReviewStatus.PENDING:
        raise HTTPException(status_code=400, detail="Not pending review")

    review.status = ReviewStatus.REVISION
    review.rejection_reason = body.rejection_reason
    if body.reviewer_agent:
        review.reviewer_agent = body.reviewer_agent
    review.reviewed_at = datetime.utcnow()
    review.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    log.info(f"Review revision requested: {review_id}")
    return ReviewOut(**review.to_dict())


@router.post("/auto-check", response_model=AutoCheckOut)
async def auto_check(
    body: ReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    """仅执行自动检查，不创建记录。"""
    passed, violations = _auto_review(
        body.content, body.check_keywords, body.min_length, body.max_length
    )

    return AutoCheckOut(
        passed=passed,
        violations=violations,
        content_length=len(body.content),
    )
