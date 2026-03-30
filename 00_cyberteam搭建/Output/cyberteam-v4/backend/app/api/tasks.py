"""Tasks API — 任务管理。"""

import uuid
import sys
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Task, TaskState

log = logging.getLogger("cyberteam.api.tasks")
router = APIRouter()

# ── Engine 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent
_engine_path = _backend_path / "engine"
_cyberteam_path = _backend_path / "cyberteam"
_integration_path = _backend_path / "integration"

for p in [str(_backend_path), str(_engine_path), str(_cyberteam_path), str(_integration_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── SwarmOrchestrator 和 CyberTeamAdapter (懒加载) ──

_cyberteam_adapter = None


def _get_cyberteam_adapter():
    """获取 CyberTeam 适配器（懒加载）"""
    global _cyberteam_adapter
    if _cyberteam_adapter is None:
        try:
            from integration.cyberteam_adapter import CyberTeamAdapter
            _cyberteam_adapter = CyberTeamAdapter(repo_root=_backend_path)
            log.info("CyberTeamAdapter loaded successfully")
        except Exception as e:
            log.warning(f"Failed to load CyberTeamAdapter: {e}")
            _cyberteam_adapter = None
    return _cyberteam_adapter


# ── Schemas ──

class TaskCreate(BaseModel):
    """任务创建请求。"""
    user_input: str = Field(..., description="用户输入的业务目标")
    priority: str = Field(default="中", description="优先级: 高/中/低")
    tags: list[str] = Field(default_factory=list)


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
    tags: list[str]
    score: Optional[float]
    created_at: Optional[str]
    updated_at: Optional[str]
    completed_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ── Swarm 相关 Schemas ──

class SwarmCreate(BaseModel):
    """创建 Swarm 团队请求"""
    team_name: str = Field(..., description="团队名称")
    goal: str = Field(..., description="团队目标")
    template: str = Field(default="swarm", description="团队模板: dev/research/content/fullstack/swarm")


class SwarmAssignTask(BaseModel):
    """分配 Swarm 任务请求"""
    team_name: str = Field(..., description="团队名称")
    agent_name: str = Field(..., description="Agent 名称")
    task: str = Field(..., description="任务描述")
    blocked_by: Optional[list[str]] = Field(default=None, description="依赖任务ID列表")


class SwarmStatus(BaseModel):
    """Swarm 状态响应"""
    name: str
    goal: str
    status: str
    agent_count: int
    started_at: str


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


# ── Swarm SwarmOrchestrator 集成 ──

@router.post("/swarm/create", status_code=201)
async def create_swarm(
    body: SwarmCreate,
):
    """创建 Swarm 团队"""
    adapter = _get_cyberteam_adapter()
    if adapter is None:
        raise HTTPException(status_code=503, detail="CyberTeamAdapter not available")

    try:
        swarm = adapter.create_swarm(
            team_name=body.team_name,
            goal=body.goal,
            template=body.template
        )

        return {
            "success": True,
            "team_name": swarm.team_name,
            "goal": swarm.goal,
            "agents": list(swarm.agents.keys()),
            "status": "created"
        }
    except Exception as e:
        log.error(f"Failed to create swarm: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create swarm: {str(e)}")


@router.post("/swarm/assign")
async def assign_swarm_task(
    body: SwarmAssignTask,
):
    """为 Swarm Agent 分配任务"""
    adapter = _get_cyberteam_adapter()
    if adapter is None:
        raise HTTPException(status_code=503, detail="CyberTeamAdapter not available")

    try:
        task = adapter.assign_task(
            team_name=body.team_name,
            agent_name=body.agent_name,
            task=body.task,
            blocked_by=body.blocked_by
        )

        if task is None:
            raise HTTPException(status_code=404, detail="Swarm or agent not found")

        return {
            "success": True,
            "task_id": task.task_id,
            "subject": task.subject,
            "blocked_by": body.blocked_by or []
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to assign task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign task: {str(e)}")


@router.get("/swarm/{team_name}/status")
async def get_swarm_status(
    team_name: str,
):
    """获取 Swarm 状态"""
    adapter = _get_cyberteam_adapter()
    if adapter is None:
        raise HTTPException(status_code=503, detail="CyberTeamAdapter not available")

    status = adapter.get_swarm_status(team_name)
    if status is None:
        raise HTTPException(status_code=404, detail="Swarm not found")

    return status


@router.get("/swarm/{team_name}/tasks")
async def get_swarm_tasks(
    team_name: str,
):
    """获取 Swarm 所有任务"""
    adapter = _get_cyberteam_adapter()
    if adapter is None:
        raise HTTPException(status_code=503, detail="CyberTeamAdapter not available")

    swarm = adapter.get_swarm(team_name)
    if swarm is None:
        raise HTTPException(status_code=404, detail="Swarm not found")

    tasks = []
    for task_id, task in swarm.task_store.items():
        tasks.append({
            "task_id": task.task_id,
            "subject": task.subject,
            "status": task.status.value,
            "assigned_to": task.assigned_to,
            "blocked_by": task.blocked_by,
            "created_at": task.created_at
        })

    return {"tasks": tasks, "total": len(tasks)}


@router.get("/swarms")
async def list_swarms():
    """列出所有活跃的 Swarms"""
    adapter = _get_cyberteam_adapter()
    if adapter is None:
        raise HTTPException(status_code=503, detail="CyberTeamAdapter not available")

    return {"swarms": adapter.list_swarms(), "total": len(adapter.list_swarms())}


@router.post("/swarm/{team_name}/shutdown")
async def shutdown_swarm(
    team_name: str,
):
    """关闭 Swarm"""
    adapter = _get_cyberteam_adapter()
    if adapter is None:
        raise HTTPException(status_code=503, detail="CyberTeamAdapter not available")

    success = adapter.shutdown_swarm(team_name)
    if not success:
        raise HTTPException(status_code=404, detail="Swarm not found")

    return {"message": "shutdown", "team_name": team_name}


@router.get("/swarm/status")
async def get_swarm_integration_status():
    """获取 Swarm 集成状态"""
    adapter = _get_cyberteam_adapter()
    return {
        "adapter_available": adapter is not None,
        "swarm_count": len(adapter.swarms) if adapter else 0
    }