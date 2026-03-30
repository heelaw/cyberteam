"""任务调度 REST API v1 - 抄 Magic。

核心功能：
- 创建即时/定时任务
- 列出任务
- 获取任务详情
- 取消任务

API 路由：
- POST /api/v1/tasks — 创建即时任务
- POST /api/v1/tasks/scheduled — 创建定时任务
- GET /api/v1/tasks — 列出任务
- GET /api/v1/tasks/{task_id} — 获取任务详情
- DELETE /api/v1/tasks/{task_id} — 取消任务
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

# ── Engine 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent.parent  # v1/tasks.py -> api/v1 -> app -> backend
_engine_path = _backend_path / "app" / "engine"

for p in [str(_backend_path), str(_engine_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Domain 模块导入 ──
from app.engine.task_scheduler import TaskSchedulerDomainService, TaskScheduler
from app.engine.task_types import TaskStatus, TaskType

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks v1"])

# ── 全局领域服务实例 ──
_task_scheduler_service: Optional[TaskSchedulerDomainService] = None


def get_task_scheduler() -> TaskSchedulerDomainService:
    """获取任务调度领域服务实例"""
    global _task_scheduler_service
    if _task_scheduler_service is None:
        _task_scheduler_service = TaskSchedulerDomainService()
    return _task_scheduler_service


# ── Request/Response Models ──

class CreateTaskRequest(BaseModel):
    """创建即时任务请求"""
    name: str = Field(..., description="任务名称")
    callback_type: str = Field(default="echo", description="回调类型: echo/sleep/error")
    params: dict = Field(default_factory=dict, description="回调参数")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")


class CreateScheduledTaskRequest(BaseModel):
    """创建定时任务请求"""
    name: str = Field(..., description="任务名称")
    run_at: datetime = Field(..., description="执行时间")
    callback_type: str = Field(default="echo", description="回调类型: echo/sleep/error")
    params: dict = Field(default_factory=dict, description="回调参数")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    name: str
    task_type: int
    status: int
    expect_time: Optional[str] = None
    actual_time: Optional[str] = None
    created_at: str
    updated_at: str
    retry_times: int
    max_retries: int
    callback_method: str
    callback_params: dict
    error_message: Optional[str] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskResponse]
    total: int


# ── 回调函数 ──

async def echo_callback(params: dict) -> str:
    """回显回调"""
    return params.get("message", "echo ok")


async def sleep_callback(params: dict) -> str:
    """睡眠回调"""
    import asyncio
    seconds = params.get("seconds", 0.1)
    await asyncio.sleep(seconds)
    return f"slept {seconds}s"


async def error_callback(params: dict) -> str:
    """错误回调"""
    raise Exception(params.get("message", "task error"))


def get_callback(callback_type: str) -> tuple:
    """获取回调函数和参数处理"""
    callbacks = {
        "echo": (echo_callback, {}),
        "sleep": (sleep_callback, {}),
        "error": (error_callback, {}),
    }
    return callbacks.get(callback_type, (echo_callback, {}))


# ── Routes ──

@router.post("", response_model=dict)
async def create_task(
    request: CreateTaskRequest,
):
    """创建即时任务"""
    service = get_task_scheduler()
    callback, _ = get_callback(request.callback_type)

    task_id = await service.create_task(
        name=request.name,
        callback=callback,
        params=request.params,
        max_retries=request.max_retries,
    )

    return {
        "task_id": task_id,
        "name": request.name,
        "status": "pending",
    }


@router.post("/scheduled", response_model=dict)
async def create_scheduled_task(
    request: CreateScheduledTaskRequest,
):
    """创建定时任务"""
    service = get_task_scheduler()
    callback, _ = get_callback(request.callback_type)

    task_id = await service.create_scheduled_task(
        name=request.name,
        run_at=request.run_at,
        callback=callback,
        params=request.params,
        max_retries=request.max_retries,
    )

    return {
        "task_id": task_id,
        "name": request.name,
        "run_at": request.run_at.isoformat(),
        "status": "pending",
    }


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
):
    """列出任务"""
    service = get_task_scheduler()

    task_status = TaskStatus(status) if status is not None else None
    tasks = service.list_tasks(status=task_status)

    # 分页
    total = len(tasks)
    tasks = tasks[offset:offset + limit]

    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=t.id,
                name=t.name,
                task_type=t.task_type.value,
                status=t.status.value,
                expect_time=t.expect_time.isoformat() if t.expect_time else None,
                actual_time=t.actual_time.isoformat() if t.actual_time else None,
                created_at=t.created_at.isoformat() if t.created_at else None,
                updated_at=t.updated_at.isoformat() if t.updated_at else None,
                retry_times=t.retry_times,
                max_retries=t.max_retries,
                callback_method=t.callback_method,
                callback_params=t.callback_params,
                error_message=t.error_message,
            )
            for t in tasks
        ],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
):
    """获取任务详情"""
    service = get_task_scheduler()
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse(
        id=task.id,
        name=task.name,
        task_type=task.task_type.value,
        status=task.status.value,
        expect_time=task.expect_time.isoformat() if task.expect_time else None,
        actual_time=task.actual_time.isoformat() if task.actual_time else None,
        created_at=task.created_at.isoformat() if task.created_at else None,
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
        retry_times=task.retry_times,
        max_retries=task.max_retries,
        callback_method=task.callback_method,
        callback_params=task.callback_params,
        error_message=task.error_message,
    )


@router.delete("/{task_id}", response_model=dict)
async def cancel_task(
    task_id: str,
):
    """取消任务"""
    service = get_task_scheduler()
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    success = await service.cancel(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} cannot be cancelled in current state"
        )

    return {
        "task_id": task_id,
        "status": "cancelled",
    }
