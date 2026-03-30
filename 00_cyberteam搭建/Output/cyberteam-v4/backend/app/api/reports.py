"""Reports API — 最终报告管理。

提供 RESTful API 用于报告生成、查询、管理。
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from ..db import get_db
from ..models import FinalReport, Task, TaskState

log = logging.getLogger("cyberteam.api.reports")
router = APIRouter()


# ── Schemas ──

class ReportCreate(BaseModel):
    """创建报告请求。"""
    task_id: str = Field(..., description="任务ID")
    title: str = Field(..., description="报告标题")
    summary: str = Field(..., description="执行摘要")
    recommendations: Optional[str] = Field(None, description="建议")
    risks: Optional[str] = Field(None, description="风险")


class ReportUpdate(BaseModel):
    """更新报告请求。"""
    title: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    risks: Optional[str] = None
    final_score: Optional[float] = None


class ReportOut(BaseModel):
    """报告响应。"""
    id: int
    task_id: str
    title: str
    summary: str
    recommendations: Optional[str]
    risks: Optional[str]
    final_score: Optional[float]
    created_at: str


class ReportListResponse(BaseModel):
    """报告列表响应。"""
    reports: List[ReportOut]
    total: int
    limit: int
    offset: int


class ReportGenerateRequest(BaseModel):
    """生成报告请求。"""
    task_id: str = Field(..., description="任务ID")
    include_recommendations: bool = Field(default=True, description="是否包含建议")
    include_risks: bool = Field(default=True, description="是否包含风险")


# ── Helper Functions ──


# ── Endpoints ──

@router.get("", response_model=ReportListResponse)
async def list_reports(
    task_id: Optional[str] = Query(None, description="按任务ID筛选"),
    limit: int = Query(default=50, ge=1, le=200, description="每页数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
):
    """获取报告列表。

    支持按任务ID筛选。
    """
    stmt = select(FinalReport)

    # 应用筛选条件
    if task_id:
        stmt = stmt.filter(FinalReport.task_id == task_id)

    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()

    # 分页和排序
    stmt = stmt.order_by(FinalReport.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    reports = result.scalars().all()

    report_list = []
    for report in reports:
        report_list.append({
            "id": report.id,
            "task_id": report.task_id,
            "title": report.title,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "risks": report.risks,
            "final_score": report.final_score,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        })

    return ReportListResponse(
        reports=report_list,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReportOut)
async def create_report(
    body: ReportCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新报告。"""
    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {body.task_id}"
        )

    # 创建报告
    report = FinalReport(
        task_id=body.task_id,
        title=body.title,
        summary=body.summary,
        recommendations=body.recommendations,
        risks=body.risks,
        final_score=task.score,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    log.info(f"Report created: task_id={body.task_id}, report_id={report.id}")

    return ReportOut(
        id=report.id,
        task_id=report.task_id,
        title=report.title,
        summary=report.summary,
        recommendations=report.recommendations,
        risks=report.risks,
        final_score=report.final_score,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取单个报告详情。"""
    stmt = select(FinalReport).filter(FinalReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found: {report_id}"
        )

    return ReportOut(
        id=report.id,
        task_id=report.task_id,
        title=report.title,
        summary=report.summary,
        recommendations=report.recommendations,
        risks=report.risks,
        final_score=report.final_score,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )


@router.get("/task/{task_id}")
async def get_report_by_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """根据任务ID获取报告。"""
    stmt = select(FinalReport).filter(FinalReport.task_id == task_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found for task: {task_id}"
        )

    return {
        "id": report.id,
        "task_id": report.task_id,
        "title": report.title,
        "summary": report.summary,
        "recommendations": report.recommendations,
        "risks": report.risks,
        "final_score": report.final_score,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


@router.patch("/{report_id}", response_model=ReportOut)
async def update_report(
    report_id: int,
    body: ReportUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新报告。

    支持部分更新，只更新提供的字段。
    """
    stmt = select(FinalReport).filter(FinalReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found: {report_id}"
        )

    # 更新字段
    if body.title is not None:
        report.title = body.title
    if body.summary is not None:
        report.summary = body.summary
    if body.recommendations is not None:
        report.recommendations = body.recommendations
    if body.risks is not None:
        report.risks = body.risks
    if body.final_score is not None:
        report.final_score = body.final_score

    await db.commit()
    await db.refresh(report)

    log.info(f"Report updated: report_id={report_id}")

    return ReportOut(
        id=report.id,
        task_id=report.task_id,
        title=report.title,
        summary=report.summary,
        recommendations=report.recommendations,
        risks=report.risks,
        final_score=report.final_score,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除报告。"""
    stmt = select(FinalReport).filter(FinalReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found: {report_id}"
        )

    await db.delete(report)
    await db.commit()

    log.info(f"Report deleted: report_id={report_id}")

    return None


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_report(
    body: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """自动生成最终报告。

    基于任务的专家输出、辩论结果、部门执行情况生成报告。
    """
    # 获取任务信息
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {body.task_id}"
        )

    # 获取专家输出
    from ..models import ExpertOutput
    stmt = select(ExpertOutput).filter(ExpertOutput.task_id == body.task_id)
    result = await db.execute(stmt)
    expert_outputs = result.scalars().all()

    # 获取部门输出
    from ..models import DepartmentOutput
    stmt = select(DepartmentOutput).filter(DepartmentOutput.task_id == body.task_id)
    result = await db.execute(stmt)
    dept_outputs = result.scalars().all()

    # 生成报告内容
    summary_parts = [f"## 任务概述\n\n{task.title}\n\n{task.description or ''}"]

    if expert_outputs:
        summary_parts.append("\n## 专家分析\n\n")
        for output in expert_outputs:
            summary_parts.append(f"### {output.expert_name}\n\n")
            if output.analysis:
                summary_parts.append(f"{output.analysis}\n\n")
            if output.suggestions:
                summary_parts.append(f"**建议**: {output.suggestions}\n\n")

    if dept_outputs:
        summary_parts.append("\n## 部门执行\n\n")
        for output in dept_outputs:
            dept_name = {
                "product": "产品部",
                "engineering": "技术部",
                "design": "设计部",
                "operations": "运营部",
                "finance": "财务部",
                "hr": "人力部",
            }.get(output.department, output.department)
            summary_parts.append(f"### {dept_name}\n\n{output.output}\n\n")

    summary = "\n".join(summary_parts)

    # 生成建议
    recommendations = ""
    if body.include_recommendations:
        rec_parts = ["## 建议\n\n"]
        for output in expert_outputs:
            if output.suggestions:
                rec_parts.append(f"- {output.expert_name}: {output.suggestions}\n")
        recommendations = "\n".join(rec_parts) if len(rec_parts) > 1 else ""

    # 生成风险
    risks = ""
    if body.include_risks:
        risk_parts = ["## 风险评估\n\n"]
        for output in expert_outputs:
            if output.risks:
                risk_parts.append(f"- {output.expert_name}: {output.risks}\n")
        risks = "\n".join(risk_parts) if len(risk_parts) > 1 else ""

    # 创建报告
    report = FinalReport(
        task_id=body.task_id,
        title=f"报告 - {task.title}",
        summary=summary,
        recommendations=recommendations or None,
        risks=risks or None,
        final_score=task.score,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    log.info(f"Report generated: task_id={body.task_id}, report_id={report.id}")

    return {
        "id": report.id,
        "task_id": report.task_id,
        "title": report.title,
        "summary": report.summary,
        "recommendations": report.recommendations,
        "risks": report.risks,
        "final_score": report.final_score,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


@router.get("/stats/overview")
async def get_report_stats(
    db: AsyncSession = Depends(get_db),
):
    """获取报告统计概览。"""
    # 总报告数
    total_stmt = select(func.count(FinalReport.id))
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0

    # 按分数分布
    score_ranges = {
        "excellent": 0,  # >= 90
        "good": 0,       # 75 - 89
        "fair": 0,       # 60 - 74
        "poor": 0,       # < 60
    }

    stmt = select(FinalReport.final_score)
    result = await db.execute(stmt)
    for row in result.all():
        score = row[0]
        if score is not None:
            if score >= 90:
                score_ranges["excellent"] += 1
            elif score >= 75:
                score_ranges["good"] += 1
            elif score >= 60:
                score_ranges["fair"] += 1
            else:
                score_ranges["poor"] += 1

    # 平均分
    avg_stmt = select(func.avg(FinalReport.final_score))
    avg_result = await db.execute(avg_stmt)
    avg_score = avg_result.scalar() or 0

    return {
        "total_reports": total,
        "score_distribution": score_ranges,
        "average_score": round(avg_score, 2),
    }
