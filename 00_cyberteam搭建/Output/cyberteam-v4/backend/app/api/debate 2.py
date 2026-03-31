"""Debate API — 辩论引擎控制。"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..config import get_settings

log = logging.getLogger("cyberteam.api.debate")
router = APIRouter()


# ── Schemas ──

class DebateStartRequest(BaseModel):
    """启动辩论请求。"""
    task_id: str = Field(..., description="任务ID")
    expert_ids: list[str] = Field(..., description="参与辩论的专家列表")
    max_rounds: int = Field(default=5, description="最大辩论轮次")


class DebateProgressRequest(BaseModel):
    """辩论进度更新请求。"""
    task_id: str = Field(..., description="任务ID")
    round_number: int = Field(..., description="当前轮次")
    expert_outputs: list[dict] = Field(..., description="专家输出列表")


class DebateConvergeRequest(BaseModel):
    """收敛检查请求。"""
    task_id: str = Field(..., description="任务ID")
    outputs: list[str] = Field(..., description="待检查的输出列表")


class DebateConvergeResponse(BaseModel):
    """收敛检查响应。"""
    is_converged: bool = Field(..., description="是否收敛")
    convergence_score: float = Field(..., description="收敛分数")
    threshold: float = Field(..., description="阈值")


class DebateEndRequest(BaseModel):
    """结束辩论请求。"""
    task_id: str = Field(..., description="任务ID")
    final_summary: str = Field(..., description="最终总结")


class DebateStatusResponse(BaseModel):
    """辩论状态响应。"""
    task_id: str
    status: str  # pending, running, converged, failed
    current_round: int
    max_rounds: int
    expert_count: int
    is_converged: bool


# ── Helper Functions ──

def check_convergence(outputs: list[str], threshold: float = 0.3) -> tuple[bool, float]:
    """检查辩论是否收敛。

    使用 Jaccard 相似度判断输出是否趋于一致。

    Args:
        outputs: 专家输出列表
        threshold: 相似度阈值（默认0.3）

    Returns:
        (is_converged, convergence_score): 是否收敛、收敛分数
    """
    if len(outputs) < 2:
        return True, 1.0

    # 简单关键词提取
    import re
    def extract_keywords(text: str) -> set:
        # 提取中文和英文单词
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text.lower())
        # 过滤停用词
        stopwords = {'的', '是', '在', '了', '和', '与', '或', '等', '这', '那', 'the', 'a', 'an', 'is', 'are'}
        return {w for w in words if len(w) > 1 and w not in stopwords}

    # 计算两两 Jaccard 相似度
    keywords_sets = [extract_keywords(out) for out in outputs]

    if not any(keywords_sets):
        return True, 1.0

    similarities = []
    for i, a in enumerate(keywords_sets):
        for j, b in enumerate(keywords_sets):
            if i < j:
                if len(a | b) > 0:
                    sim = len(a & b) / len(a | b)
                    similarities.append(sim)

    avg_similarity = sum(similarities) / len(similarities) if similarities else 0

    return avg_similarity >= threshold, avg_similarity


# ── Endpoints ──

@router.post("/start", status_code=201)
async def start_debate(
    body: DebateStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """启动辩论流程。"""
    from ..models import Task, TaskState, DebateRound
    from sqlalchemy import select

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 更新任务状态
    task.state = TaskState.DEBATING
    await db.commit()

    # 创建第一轮辩论记录
    first_round = DebateRound(
        task_id=body.task_id,
        round_number=1,
        round_type="initial",
    )
    db.add(first_round)
    await db.commit()

    log.info(f"Debate started: task={body.task_id}, experts={body.expert_ids}")

    return {
        "task_id": body.task_id,
        "status": "running",
        "current_round": 1,
        "max_rounds": body.max_rounds,
    }


@router.post("/progress")
async def update_debate_progress(
    body: DebateProgressRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新辩论进度。"""
    from ..models import Task, ExpertOutput
    from sqlalchemy import select

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 保存专家输出
    for output in body.expert_outputs:
        expert_output = ExpertOutput(
            task_id=body.task_id,
            expert_id=output.get("expert_id", "unknown"),
            expert_name=output.get("expert_name", "未知专家"),
            framework=output.get("framework", ""),
            analysis=output.get("analysis", ""),
            suggestions=output.get("suggestions", ""),
            risks=output.get("risks", ""),
            round=body.round_number,
        )
        db.add(expert_output)

    await db.commit()

    log.info(f"Debate progress updated: task={body.task_id}, round={body.round_number}")

    return {"message": "ok", "round": body.round_number}


@router.post("/converge-check", response_model=DebateConvergeResponse)
async def check_debate_convergence(
    body: DebateConvergeRequest,
):
    """检查辩论是否收敛。"""
    settings = get_settings()

    is_converged, convergence_score = check_convergence(
        body.outputs,
        threshold=settings.convergence_threshold
    )

    return DebateConvergeResponse(
        is_converged=is_converged,
        convergence_score=convergence_score,
        threshold=settings.convergence_threshold,
    )


@router.post("/end")
async def end_debate(
    body: DebateEndRequest,
    db: AsyncSession = Depends(get_db),
):
    """结束辩论流程。"""
    from ..models import Task, TaskState, DebateRound
    from sqlalchemy import select

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 更新任务状态为执行中
    task.state = TaskState.EXECUTING
    await db.commit()

    # 更新最后一轮
    stmt = select(DebateRound).filter(
        DebateRound.task_id == body.task_id
    ).order_by(DebateRound.round_number.desc())
    result = await db.execute(stmt)
    last_round = result.scalar_one_or_none()

    if last_round:
        last_round.summary = body.final_summary

    await db.commit()

    log.info(f"Debate ended: task={body.task_id}")

    return {
        "task_id": body.task_id,
        "status": "completed",
        "summary": body.final_summary[:200],
    }


@router.get("/status/{task_id}", response_model=DebateStatusResponse)
async def get_debate_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取辩论状态。"""
    from ..models import Task, DebateRound, ExpertOutput
    from sqlalchemy import select, func

    # 任务状态
    stmt = select(Task).filter(Task.task_id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 当前轮次
    stmt = select(func.max(DebateRound.round_number)).filter(
        DebateRound.task_id == task_id
    )
    result = await db.execute(stmt)
    current_round = result.scalar() or 0

    # 专家数量
    stmt = select(func.count(ExpertOutput.id)).filter(
        ExpertOutput.task_id == task_id
    )
    result = await db.execute(stmt)
    expert_count = result.scalar() or 0

    # 是否已收敛
    stmt = select(DebateRound.is_converged).filter(
        DebateRound.task_id == task_id,
        DebateRound.is_converged == True
    ).order_by(DebateRound.round_number.desc())
    result = await db.execute(stmt)
    is_converged = result.scalar_one_or_none() or False

    return DebateStatusResponse(
        task_id=task_id,
        status=task.state.value,
        current_round=current_round,
        max_rounds=5,
        expert_count=expert_count,
        is_converged=bool(is_converged),
    )