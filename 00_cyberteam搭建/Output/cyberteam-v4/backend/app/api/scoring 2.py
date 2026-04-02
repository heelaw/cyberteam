"""Scoring API — 方案评分与质量门禁。"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..config import get_settings

log = logging.getLogger("cyberteam.api.scoring")
router = APIRouter()


# ── 六维评分权重 ──

SCORE_WEIGHTS = {
    "completeness": 0.25,   # 完整性 25%
    "professionalism": 0.25,  # 专业性 25%
    "practicality": 0.20,   # 实用性 20%
    "logic": 0.15,         # 逻辑性 15%
    "innovation": 0.10,    # 创新性 10%
    "safety": 0.05,        # 安全性 5%
}


# ── Schemas ──

class ScoreRequest(BaseModel):
    """评分请求。"""
    task_id: str = Field(..., description="任务ID")
    expert_id: str = Field(..., description="专家ID")
    completeness: float = Field(..., ge=0, le=100, description="完整性 0-100")
    professionalism: float = Field(..., ge=0, le=100, description="专业性 0-100")
    practicality: float = Field(..., ge=0, le=100, description="实用性 0-100")
    logic: float = Field(..., ge=0, le=100, description="逻辑性 0-100")
    innovation: float = Field(..., ge=0, le=100, description="创新性 0-100")
    safety: float = Field(..., ge=0, le=100, description="安全性 0-100")


class ScoreResponse(BaseModel):
    """评分响应。"""
    task_id: str
    expert_id: str
    completeness: float
    professionalism: float
    practicality: float
    logic: float
    innovation: float
    safety: float
    total_score: float = Field(..., description="加权总分")


class QualityGateRequest(BaseModel):
    """质量门禁检查请求。"""
    task_id: str = Field(..., description="任务ID")
    gate_level: int = Field(..., description="门禁级别 0-4")


class QualityGateResponse(BaseModel):
    """质量门禁检查响应。"""
    passed: bool = Field(..., description="是否通过")
    gate_level: int = Field(..., description="门禁级别")
    score: float = Field(..., description="总分")
    issues: list[str] = Field(default_factory=list, description="问题列表")


class AggregateScoreRequest(BaseModel):
    """聚合评分请求。"""
    task_id: str = Field(..., description="任务ID")


class AggregateScoreResponse(BaseModel):
    """聚合评分响应。"""
    task_id: str
    expert_count: int
    completeness: float
    professionalism: float
    practicality: float
    logic: float
    innovation: float
    safety: float
    total_score: float
    passed_l1: bool
    passed_l3: bool
    passed_l4: bool


# ── Helper Functions ──

def calculate_total_score(
    completeness: float,
    professionalism: float,
    practicality: float,
    logic: float,
    innovation: float,
    safety: float,
) -> float:
    """计算加权总分。

    归一化系数: /3.55 (基于权重总和)
    """
    total = (
        completeness * SCORE_WEIGHTS["completeness"] +
        professionalism * SCORE_WEIGHTS["professionalism"] +
        practicality * SCORE_WEIGHTS["practicality"] +
        logic * SCORE_WEIGHTS["logic"] +
        innovation * SCORE_WEIGHTS["innovation"] +
        safety * SCORE_WEIGHTS["safety"]
    )
    return round(total, 2)


def check_quality_gate(score: float, level: int) -> tuple[bool, list[str]]:
    """检查质量门禁。

    Args:
        score: 总分
        level: 门禁级别 (0-4)

    Returns:
        (passed, issues): 是否通过、问题列表
    """
    settings = get_settings()
    issues = []

    if level == 0:
        # L0: 输入校验 - 无错误即通过（由其他模块处理）
        return True, []

    elif level == 1:
        # L1: 计划审批 - ≥70分
        if score < settings.quality_gate_l1:
            issues.append(f"总分 {score} < {settings.quality_gate_l1} 分")

    elif level == 2:
        # L2: 过程检查 - 进度正常（由监控系统处理）
        return True, []

    elif level == 3:
        # L3: 结果评审 - ≥70分
        if score < settings.quality_gate_l3:
            issues.append(f"总分 {score} < {settings.quality_gate_l3} 分")

    elif level == 4:
        # L4: 交付终审 - ≥75分 + 中低风险
        if score < settings.quality_gate_l4:
            issues.append(f"总分 {score} < {settings.quality_gate_l4} 分")

    return len(issues) == 0, issues


# ── Endpoints ──

@router.post("/rate", response_model=ScoreResponse)
async def rate_expert_output(
    body: ScoreRequest,
    db: AsyncSession = Depends(get_db),
):
    """为专家输出评分。"""
    from ..models import ExpertOutput, Task
    from sqlalchemy import select

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 查找或创建专家输出记录
    stmt = select(ExpertOutput).filter(
        ExpertOutput.task_id == body.task_id,
        ExpertOutput.expert_id == body.expert_id
    )
    result = await db.execute(stmt)
    expert_output = result.scalar_one_or_none()

    if expert_output:
        # 更新现有评分
        expert_output.completeness = body.completeness
        expert_output.professionalism = body.professionalism
        expert_output.practicality = body.practicality
        expert_output.logic = body.logic
        expert_output.innovation = body.innovation
        expert_output.safety = body.safety
    else:
        # 创建新记录
        expert_output = ExpertOutput(
            task_id=body.task_id,
            expert_id=body.expert_id,
            expert_name=body.expert_id,
            framework="",
            analysis="",
            suggestions="",
            round=1,
            completeness=body.completeness,
            professionalism=body.professionalism,
            practicality=body.practicality,
            logic=body.logic,
            innovation=body.innovation,
            safety=body.safety,
        )
        db.add(expert_output)

    await db.commit()

    total_score = calculate_total_score(
        body.completeness,
        body.professionalism,
        body.practicality,
        body.logic,
        body.innovation,
        body.safety,
    )

    log.info(f"Expert rated: task={body.task_id}, expert={body.expert_id}, score={total_score}")

    return ScoreResponse(
        task_id=body.task_id,
        expert_id=body.expert_id,
        completeness=body.completeness,
        professionalism=body.professionalism,
        practicality=body.practicality,
        logic=body.logic,
        innovation=body.innovation,
        safety=body.safety,
        total_score=total_score,
    )


@router.post("/gate", response_model=QualityGateResponse)
async def check_gate(
    body: QualityGateRequest,
    db: AsyncSession = Depends(get_db),
):
    """检查质量门禁。"""
    from ..models import Task
    from sqlalchemy import select

    # 获取任务评分
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    score = task.score or 0
    passed, issues = check_quality_gate(score, body.gate_level)

    return QualityGateResponse(
        passed=passed,
        gate_level=body.gate_level,
        score=score,
        issues=issues,
    )


@router.post("/aggregate", response_model=AggregateScoreResponse)
async def aggregate_scores(
    body: AggregateScoreRequest,
    db: AsyncSession = Depends(get_db),
):
    """聚合所有专家评分。"""
    from ..models import ExpertOutput, Task
    from sqlalchemy import select, func

    settings = get_settings()

    # 获取所有专家评分
    stmt = select(ExpertOutput).filter(ExpertOutput.task_id == body.task_id)
    result = await db.execute(stmt)
    outputs = result.scalars().all()

    if not outputs:
        raise HTTPException(status_code=404, detail="No expert outputs found")

    # 计算平均分
    n = len(outputs)
    avg_completeness = sum(o.completeness for o in outputs) / n
    avg_professionalism = sum(o.professionalism for o in outputs) / n
    avg_practicality = sum(o.practicality for o in outputs) / n
    avg_logic = sum(o.logic for o in outputs) / n
    avg_innovation = sum(o.innovation for o in outputs) / n
    avg_safety = sum(o.safety for o in outputs) / n

    total_score = calculate_total_score(
        avg_completeness,
        avg_professionalism,
        avg_practicality,
        avg_logic,
        avg_innovation,
        avg_safety,
    )

    # 更新任务评分
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if task:
        task.completeness = avg_completeness
        task.professionalism = avg_professionalism
        task.practicality = avg_practicality
        task.logic = avg_logic
        task.innovation = avg_innovation
        task.safety = avg_safety
        task.score = total_score
        await db.commit()

    # 检查各级门禁
    _, l1_issues = check_quality_gate(total_score, 1)
    _, l3_issues = check_quality_gate(total_score, 3)
    _, l4_issues = check_quality_gate(total_score, 4)

    log.info(f"Scores aggregated: task={body.task_id}, experts={n}, total={total_score}")

    return AggregateScoreResponse(
        task_id=body.task_id,
        expert_count=n,
        completeness=round(avg_completeness, 2),
        professionalism=round(avg_professionalism, 2),
        practicality=round(avg_practicality, 2),
        logic=round(avg_logic, 2),
        innovation=round(avg_innovation, 2),
        safety=round(avg_safety, 2),
        total_score=total_score,
        passed_l1=len(l1_issues) == 0,
        passed_l3=len(l3_issues) == 0,
        passed_l4=len(l4_issues) == 0,
    )


@router.get("/weights")
async def get_score_weights():
    """获取评分权重配置。"""
    return {"weights": SCORE_WEIGHTS, "total": sum(SCORE_WEIGHTS.values())}