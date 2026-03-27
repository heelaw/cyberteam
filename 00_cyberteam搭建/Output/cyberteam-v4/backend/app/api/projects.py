"""Projects API — 项目管理。

提供 RESTful API 用于创建、读取、更新、删除项目。
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
from ..models import Task, TaskState

log = logging.getLogger("cyberteam.api.projects")
router = APIRouter()


# ── 项目数据存储（临时使用内存，后续迁移到数据库）──

_projects: Dict[str, Dict[str, Any]] = {}


# ── Schemas (请求/响应模型) ──

class ProjectCreate(BaseModel):
    """创建项目请求。"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, max_length=5000, description="项目描述")
    goal: str = Field(..., description="项目目标")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class ProjectUpdate(BaseModel):
    """更新项目请求。"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    goal: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ProjectOut(BaseModel):
    """项目响应。"""
    project_id: str
    name: str
    description: Optional[str]
    goal: str
    tags: List[str]
    metadata: Dict[str, Any]
    status: str
    task_count: int
    created_at: str
    updated_at: str


class ProjectListResponse(BaseModel):
    """项目列表响应。"""
    projects: List[ProjectOut]
    total: int
    limit: int
    offset: int


class ProjectStatsResponse(BaseModel):
    """项目统计响应。"""
    total: int
    by_status: Dict[str, int]
    total_tasks: int
    active_projects: int


# ── Helper Functions ──

def _project_to_dict(project_id: str, project: Dict[str, Any]) -> Dict[str, Any]:
    """转换为字典。"""
    return {
        "project_id": project_id,
        "name": project.get("name", ""),
        "description": project.get("description"),
        "goal": project.get("goal", ""),
        "tags": project.get("tags", []),
        "metadata": project.get("metadata", {}),
        "status": project.get("status", "active"),
        "created_at": project.get("created_at", datetime.utcnow().isoformat()),
        "updated_at": project.get("updated_at", datetime.utcnow().isoformat()),
    }


# ── Endpoints ──

@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="按状态筛选"),
    search: Optional[str] = Query(None, description="搜索名称或描述"),
    limit: int = Query(default=50, ge=1, le=200, description="每页数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
):
    """获取项目列表。

    支持按状态筛选、关键词搜索。
    """
    # 筛选
    filtered_projects = []
    for project_id, project in _projects.items():
        if status and project.get("status") != status:
            continue
        if search:
            search_lower = search.lower()
            name = project.get("name", "").lower()
            desc = project.get("description", "").lower()
            if search_lower not in name and search_lower not in desc:
                continue
        filtered_projects.append((project_id, project))

    # 排序（按更新时间倒序）
    filtered_projects.sort(
        key=lambda x: x[1].get("updated_at", ""), reverse=True
    )

    # 分页
    total = len(filtered_projects)
    paginated = filtered_projects[offset:offset + limit]

    projects = []
    for project_id, project in paginated:
        projects.append(_project_to_dict(project_id, project))

    return ProjectListResponse(
        projects=projects,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=ProjectStatsResponse)
async def get_project_stats():
    """获取项目统计信息。

    返回总数、按状态分组、任务总数等。
    """
    by_status: Dict[str, int] = {}
    total_tasks = 0
    active_projects = 0

    for project in _projects.values():
        status_val = project.get("status", "active")
        by_status[status_val] = by_status.get(status_val, 0) + 1
        total_tasks += project.get("task_count", 0)
        if status_val == "active":
            active_projects += 1

    return ProjectStatsResponse(
        total=len(_projects),
        by_status=by_status,
        total_tasks=total_tasks,
        active_projects=active_projects,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProjectOut)
async def create_project(
    body: ProjectCreate,
):
    """创建新项目。"""
    project_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    project = {
        "name": body.name,
        "description": body.description,
        "goal": body.goal,
        "tags": body.tags,
        "metadata": body.metadata,
        "status": "active",
        "task_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    _projects[project_id] = project

    log.info(f"Project created: {project_id}")

    return ProjectOut(**_project_to_dict(project_id, project))


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
):
    """获取单个项目详情。"""
    project = _projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    return ProjectOut(**_project_to_dict(project_id, project))


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    body: ProjectUpdate,
):
    """更新项目。

    支持部分更新，只更新提供的字段。
    """
    project = _projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    # 更新字段
    if body.name is not None:
        project["name"] = body.name
    if body.description is not None:
        project["description"] = body.description
    if body.goal is not None:
        project["goal"] = body.goal
    if body.tags is not None:
        project["tags"] = body.tags
    if body.metadata is not None:
        project["metadata"] = body.metadata
    if body.status is not None:
        project["status"] = body.status

    project["updated_at"] = datetime.utcnow().isoformat()

    log.info(f"Project updated: {project_id}")

    return ProjectOut(**_project_to_dict(project_id, project))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
):
    """删除项目。"""
    project = _projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    del _projects[project_id]

    log.info(f"Project deleted: {project_id}")

    return None


@router.post("/{project_id}/archive", response_model=ProjectOut)
async def archive_project(
    project_id: str,
):
    """归档项目。"""
    project = _projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    project["status"] = "archived"
    project["updated_at"] = datetime.utcnow().isoformat()

    log.info(f"Project archived: {project_id}")

    return ProjectOut(**_project_to_dict(project_id, project))


@router.post("/{project_id}/activate", response_model=ProjectOut)
async def activate_project(
    project_id: str,
):
    """激活项目。"""
    project = _projects.get(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    project["status"] = "active"
    project["updated_at"] = datetime.utcnow().isoformat()

    log.info(f"Project activated: {project_id}")

    return ProjectOut(**_project_to_dict(project_id, project))


@router.get("/{project_id}/tasks")
async def get_project_tasks(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取项目的所有任务。"""
    # 检查项目是否存在
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    # 从任务表中获取相关任务
    stmt = select(Task).filter(Task.task_id.startswith(f"{project_id}-"))
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return {
        "project_id": project_id,
        "tasks": [task.to_dict() for task in tasks],
        "total": len(tasks),
    }


@router.post("/{project_id}/link-task")
async def link_task_to_project(
    project_id: str,
    task_id: str = Field(..., description="任务ID"),
    db: AsyncSession = Depends(get_db),
):
    """将任务关联到项目。"""
    # 检查项目是否存在
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    # 检查任务是否存在
    stmt = select(Task).filter(Task.task_id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}"
        )

    # 更新项目的元数据，记录任务关联
    project = _projects[project_id]
    if "linked_tasks" not in project["metadata"]:
        project["metadata"]["linked_tasks"] = []

    if task_id not in project["metadata"]["linked_tasks"]:
        project["metadata"]["linked_tasks"].append(task_id)
        project["task_count"] = len(project["metadata"]["linked_tasks"])
        project["updated_at"] = datetime.utcnow().isoformat()

    log.info(f"Task linked to project: task={task_id}, project={project_id}")

    return {
        "project_id": project_id,
        "task_id": task_id,
        "message": "Task linked successfully",
    }
