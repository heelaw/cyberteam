"""项目 API v1 - CyberTeam 特色。

核心功能：
- 创建/获取/更新/删除项目
- 项目上下文管理（business_context.md）
- 项目文件结构管理
- Playground 生成

API 路由：
- POST /api/v1/projects - 创建项目
- GET /api/v1/projects - 列出项目
- GET /api/v1/projects/{id} - 获取项目详情
- PUT /api/v1/projects/{id} - 更新项目
- DELETE /api/v1/projects/{id} - 删除项目
- GET /api/v1/projects/{id}/context - 获取项目上下文
- PUT /api/v1/projects/{id}/context - 更新项目上下文
- POST /api/v1/projects/{id}/playground - 生成 Playground
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_db
from ...auth import get_current_user
from ..repositories import ProjectRepository

router = APIRouter(prefix="/projects", tags=["projects v1"])


# === Request/Response Models ===

class CreateProjectRequest(BaseModel):
    """创建项目请求。"""
    name: str
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class UpdateProjectRequest(BaseModel):
    """更新项目请求。"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None


class ProjectResponse(BaseModel):
    """项目响应。"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    status: str
    metadata: dict
    created_at: str
    updated_at: str


class ContextResponse(BaseModel):
    """项目上下文响应。"""
    project_id: str
    business_context: dict
    research: dict
    agents: dict
    files: List[str]


# === Routes ===

@router.post("", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """创建新项目。"""
    repo = ProjectRepository(db)

    project = await repo.create(
        name=request.name,
        user_id=user["sub"],
        goal="",  # 可以后续通过更新接口设置
        description=request.description,
        extra_data=request.metadata,
    )

    return ProjectResponse(
        id=project.id,
        user_id=user["sub"],
        name=project.name,
        description=project.description,
        status=project.status,
        metadata=project.extra_data or {},
        created_at=project.created_at.isoformat() if project.created_at else "",
        updated_at=project.updated_at.isoformat() if project.updated_at else "",
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取项目列表。"""
    repo = ProjectRepository(db)
    projects = await repo.list_by_user(
        user_id=user["sub"],
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return [
        ProjectResponse(
            id=p.id,
            user_id=user["sub"],
            name=p.name,
            description=p.description,
            status=p.status,
            metadata=p.extra_data or {},
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else "",
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取项目详情。"""
    repo = ProjectRepository(db)
    project = await repo.get(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return ProjectResponse(
        id=project.id,
        user_id=user["sub"],
        name=project.name,
        description=project.description,
        status=project.status,
        metadata=project.extra_data or {},
        created_at=project.created_at.isoformat() if project.created_at else "",
        updated_at=project.updated_at.isoformat() if project.updated_at else "",
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """更新项目。"""
    repo = ProjectRepository(db)
    project = await repo.update(
        project_id=project_id,
        name=request.name,
        goal=request.metadata.get("goal") if request.metadata else None,
        description=request.description,
        tags=request.metadata.get("tags") if request.metadata else None,
        status=request.status,
    )

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return ProjectResponse(
        id=project.id,
        user_id=user["sub"],
        name=project.name,
        description=project.description,
        status=project.status,
        metadata=project.extra_data or {},
        created_at=project.created_at.isoformat() if project.created_at else "",
        updated_at=project.updated_at.isoformat() if project.updated_at else "",
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """删除项目。"""
    repo = ProjectRepository(db)
    success = await repo.delete(project_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return {"status": "ok", "project_id": project_id}


@router.get("/{project_id}/context", response_model=ContextResponse)
async def get_project_context(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """获取项目上下文。"""
    # TODO: 读取项目目录下的 context/ 文件
    return ContextResponse(
        project_id=project_id,
        business_context={},
        research={},
        agents={},
        files=[],
    )


@router.put("/{project_id}/context")
async def update_project_context(
    project_id: str,
    business_context: Optional[dict] = None,
    user: dict = Depends(get_current_user),
):
    """更新项目上下文。"""
    # TODO: 写入 context/business_context.md
    return {"status": "ok", "project_id": project_id}


@router.post("/{project_id}/playground")
async def generate_playground(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """生成 Playground 交互式看板。"""
    # TODO: 调用 Playground 生成器
    return {
        "status": "ok",
        "project_id": project_id,
        "playground_url": f"/projects/{project_id}/playground.html",
    }
