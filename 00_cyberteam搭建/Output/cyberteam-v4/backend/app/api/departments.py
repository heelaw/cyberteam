"""Departments API — 部门执行管理。

提供 RESTful API 用于部门任务分配、执行、输出管理。
"""

import uuid
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from ..db import get_db
from ..models import DepartmentOutput, Task
from ..auth.dependencies import get_current_user, get_optional_user

log = logging.getLogger("cyberteam.api.departments")
router = APIRouter()

# ── Engine 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent
_engine_path = _backend_path / "engine"
_cyberteam_path = _backend_path / "cyberteam"
_integration_path = _backend_path / "integration"

for p in [str(_backend_path), str(_engine_path), str(_cyberteam_path), str(_integration_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ── 部门定义 ──

DEPARTMENTS = {
    "product": {
        "name": "产品部",
        "description": "需求分析、产品设计、功能规划",
        "responsibility": "产品规划与设计",
        "skills": ["需求分析", "产品规划", "原型设计", "用户研究"],
    },
    "engineering": {
        "name": "技术部",
        "description": "技术方案、架构设计、开发实现",
        "responsibility": "技术实现",
        "skills": ["系统架构", "后端开发", "前端开发", "测试"],
    },
    "design": {
        "name": "设计部",
        "description": "UI设计、用户体验、品牌视觉",
        "responsibility": "设计创作",
        "skills": ["UI设计", "UX设计", "品牌设计", "视觉设计"],
    },
    "operations": {
        "name": "运营部",
        "description": "用户增长、内容运营、活动策划",
        "responsibility": "运营策略",
        "skills": ["用户运营", "内容运营", "活动策划", "数据分析"],
    },
    "finance": {
        "name": "财务部",
        "description": "预算规划、成本控制、投资分析",
        "responsibility": "财务规划",
        "skills": ["预算管理", "成本控制", "财务分析", "投资决策"],
    },
    "hr": {
        "name": "人力部",
        "description": "招聘方案、团队激励、文化建设",
        "responsibility": "人力资源",
        "skills": ["招聘", "培训", "绩效管理", "团队建设"],
    },
}


# ── 部门执行器（懒加载）──

_department_executor = None


def _get_department_executor():
    """获取部门执行器（懒加载）"""
    global _department_executor
    if _department_executor is None:
        try:
            from engine.department import DepartmentExecutor
            _department_executor = DepartmentExecutor()
            log.info("DepartmentExecutor loaded successfully")
        except Exception as e:
            log.warning(f"Failed to load DepartmentExecutor: {e}")
            _department_executor = None
    return _department_executor


# ── Schemas ──

class DepartmentOut(BaseModel):
    """部门信息响应。"""
    department_id: str
    name: str
    description: str
    responsibility: str
    skills: List[str]


class DepartmentTaskAssign(BaseModel):
    """部门任务分配请求。"""
    task_id: str = Field(..., description="任务ID")
    department: str = Field(..., description="部门ID")
    instructions: str = Field(..., description="执行指令")
    priority: str = Field(default="中", description="优先级")
    deadline: Optional[str] = Field(None, description="截止日期")


class DepartmentTaskUpdate(BaseModel):
    """部门任务更新请求。"""
    status: str = Field(..., description="状态: running/completed/failed")
    output: Optional[str] = Field(None, description="执行输出")


class DepartmentOutputOut(BaseModel):
    """部门输出响应。"""
    id: int
    task_id: str
    department: str
    output: str
    status: str
    created_at: str
    completed_at: Optional[str]


class DepartmentExecuteRequest(BaseModel):
    """部门执行请求。"""
    task_id: str = Field(..., description="任务ID")
    department: str = Field(..., description="部门ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="执行上下文")


class DepartmentExecuteResponse(BaseModel):
    """部门执行响应。"""
    task_id: str
    department: str
    output_id: int
    status: str
    output: str


# ── Endpoints ──

@router.get("")
async def list_departments():
    """获取所有部门列表。"""
    departments = []
    for dept_id, info in DEPARTMENTS.items():
        departments.append({
            "department_id": dept_id,
            "name": info["name"],
            "description": info["description"],
            "responsibility": info["responsibility"],
            "skills": info["skills"],
        })

    return {"departments": departments, "total": len(departments)}


@router.get("/{department_id}")
async def get_department(department_id: str):
    """获取单个部门详情。"""
    if department_id not in DEPARTMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department not found: {department_id}"
        )

    info = DEPARTMENTS[department_id]
    return {
        "department_id": department_id,
        "name": info["name"],
        "description": info["description"],
        "responsibility": info["responsibility"],
        "skills": info["skills"],
    }


@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_department_task(
    body: DepartmentTaskAssign,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分配任务给部门。"""
    # 验证部门存在
    if body.department not in DEPARTMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid department: {body.department}"
        )

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {body.task_id}"
        )

    # 创建部门输出记录
    output = DepartmentOutput(
        task_id=body.task_id,
        department=body.department,
        output=body.instructions,
        status="pending",
    )
    db.add(output)
    await db.commit()
    await db.refresh(output)

    log.info(f"Task assigned to department: task={body.task_id}, dept={body.department}")

    return {
        "output_id": output.id,
        "task_id": body.task_id,
        "department": body.department,
        "status": "pending",
    }


@router.post("/execute", response_model=DepartmentExecuteResponse)
async def execute_department_task(
    body: DepartmentExecuteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行部门任务。"""
    # 验证部门存在
    if body.department not in DEPARTMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid department: {body.department}"
        )

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {body.task_id}"
        )

    # 获取部门执行器
    executor = _get_department_executor()
    if executor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DepartmentExecutor not available"
        )

    try:
        # 执行部门任务
        result = await executor.execute(
            department=body.department,
            task_id=body.task_id,
            context=body.context,
        )

        # 创建或更新部门输出记录
        stmt = select(DepartmentOutput).filter(
            DepartmentOutput.task_id == body.task_id,
            DepartmentOutput.department == body.department
        )
        result_db = await db.execute(stmt)
        output = result_db.scalar_one_or_none()

        if output:
            output.output = result.get("output", "")
            output.status = "completed"
            output.completed_at = datetime.utcnow()
        else:
            output = DepartmentOutput(
                task_id=body.task_id,
                department=body.department,
                output=result.get("output", ""),
                status="completed",
            )
            db.add(output)

        await db.commit()
        await db.refresh(output)

        log.info(f"Department task executed: task={body.task_id}, dept={body.department}")

        return DepartmentExecuteResponse(
            task_id=body.task_id,
            department=body.department,
            output_id=output.id,
            status="completed",
            output=result.get("output", ""),
        )

    except Exception as e:
        log.error(f"Department execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}"
        )


@router.get("/outputs/{task_id}")
async def get_department_outputs(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取任务的所有部门输出。"""
    stmt = select(DepartmentOutput).filter(DepartmentOutput.task_id == task_id)
    result = await db.execute(stmt)
    outputs = result.scalars().all()

    return {
        "task_id": task_id,
        "outputs": [
            {
                "id": o.id,
                "department": o.department,
                "output": o.output,
                "status": o.status,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "completed_at": o.completed_at.isoformat() if o.completed_at else None,
            }
            for o in outputs
        ],
        "total": len(outputs),
    }


@router.get("/outputs/{output_id}")
async def get_department_output(
    output_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取单个部门输出详情。"""
    stmt = select(DepartmentOutput).filter(DepartmentOutput.id == output_id)
    result = await db.execute(stmt)
    output = result.scalar_one_or_none()

    if not output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output not found: {output_id}"
        )

    return {
        "id": output.id,
        "task_id": output.task_id,
        "department": output.department,
        "output": output.output,
        "status": output.status,
        "created_at": output.created_at.isoformat() if output.created_at else None,
        "completed_at": output.completed_at.isoformat() if output.completed_at else None,
    }


@router.patch("/outputs/{output_id}")
async def update_department_output(
    output_id: int,
    body: DepartmentTaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新部门输出。"""
    stmt = select(DepartmentOutput).filter(DepartmentOutput.id == output_id)
    result = await db.execute(stmt)
    output = result.scalar_one_or_none()

    if not output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output not found: {output_id}"
        )

    # 更新字段
    output.status = body.status
    if body.output is not None:
        output.output = body.output

    if body.status == "completed":
        output.completed_at = datetime.utcnow()

    await db.commit()

    log.info(f"Department output updated: output_id={output_id}")

    return {
        "id": output.id,
        "task_id": output.task_id,
        "department": output.department,
        "status": output.status,
    }


@router.get("/executor/status")
async def get_executor_status():
    """获取部门执行器状态。"""
    executor = _get_department_executor()

    return {
        "executor_available": executor is not None,
        "departments": list(DEPARTMENTS.keys()),
    }
