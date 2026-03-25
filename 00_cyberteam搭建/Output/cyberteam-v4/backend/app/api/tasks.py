"""Tasks API — 任务管理。"""

import uuid
from typing import Optional, Union, List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Task, TaskState

log = logging.getLogger("cyberteam.api.tasks")
router = APIRouter()


# ── Schemas ──

class TaskCreate(BaseModel):
    """任务创建请求。"""
    user_input: str = Field(..., description="用户输入的业务目标")
    priority: str = Field(default="中", description="优先级: 高/中/低")
    tags: List[str] = Field(default_factory=list)


class TaskTransition(BaseModel):
    """状态流转请求。"""
    new_state: str
    agent: str = "system"
    reason: str = ""


class TaskOut(BaseModel):
    """任务输出。"""
    task_id: str
    trace_id: str
    title: str
    description: str
    user_input: str
    state: str
    priority: str
    assignee_org: Optional[str]
    creator: str
    tags: List[str]
    score: Optional[float]
    created_at: Optional[str]
    updated_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


# ── Endpoints ──

@router.get("")
async def list_tasks(
    state: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """获取任务列表。"""
    from sqlalchemy import select, func

    stmt = select(Task)
    if state:
        stmt = stmt.filter(Task.state == state)
    if priority:
        stmt = stmt.filter(Task.priority == priority)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return {
        "tasks": [t.to_dict() for t in tasks],
        "count": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats")
async def task_stats(db: AsyncSession = Depends(get_db)):
    """任务统计。"""
    from sqlalchemy import select, func

    stmt = select(Task.state, func.count(Task.task_id)).group_by(Task.state)
    result = await db.execute(stmt)
    stats = {row[0]: row[1] for row in result.all()}

    total = sum(stats.values())
    return {"total": total, "by_state": stats}


@router.post("", status_code=201)
async def create_task(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新任务。"""
    task_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())

    task = Task(
        task_id=task_id,
        trace_id=trace_id,
        title=body.user_input[:100],  # 截取标题
        description="",
        user_input=body.user_input,
        state=TaskState.PENDING,
        priority=body.priority,
        creator="user",
        tags=body.tags,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    log.info(f"Task created: {task_id}")

    return {
        "task_id": task.task_id,
        "trace_id": task.trace_id,
        "state": task.state.value,
    }


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取任务详情。"""
    from sqlalchemy import select

    stmt = select(Task).filter(Task.task_id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task.to_dict()


@router.post("/{task_id}/transition")
async def transition_task(
    task_id: str,
    body: TaskTransition,
    db: AsyncSession = Depends(get_db),
):
    """执行状态流转。"""
    from sqlalchemy import select

    stmt = select(Task).filter(Task.task_id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        task.state = TaskState(body.new_state)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {body.new_state}")

    task.updated_at = datetime.utcnow()
    await db.commit()

    return {"task_id": task.task_id, "state": task.state.value}


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除任务。"""
    from sqlalchemy import select, delete

    stmt = select(Task).filter(Task.task_id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()

    return {"message": "deleted", "task_id": task_id}