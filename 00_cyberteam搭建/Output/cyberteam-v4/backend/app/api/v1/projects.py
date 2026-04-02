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
    # ========== 新增字段：本地文件夹路径 ==========
    local_path: Optional[str] = None
    # =============================================
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
    # ========== 新增字段：本地文件夹路径 ==========
    local_path: Optional[str] = None
    # =============================================
    status: str
    metadata: dict
    created_at: str
    updated_at: str


class ContextResponse(BaseModel):
    """项目上下文响应。"""
    project_id: str
    project_name: str
    local_path: Optional[str] = None
    business_context: str  # 改为字符串而非字典
    has_context: bool = False
    files: List[str] = []


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
        local_path=request.local_path,  # ========== 保存本地路径 ==========
    )

    return ProjectResponse(
        id=project.id,
        user_id=user["sub"],
        name=project.name,
        description=project.description,
        local_path=project.local_path,  # ========== 返回本地路径 ==========
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
            local_path=p.local_path,  # ========== 返回本地路径 ==========
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
        local_path=project.local_path,  # ========== 返回本地路径 ==========
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
        local_path=project.local_path,  # ========== 返回本地路径 ==========
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
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取项目上下文。

    优先读取顺序：
    1. local_path 下的 context/business_context.md
    2. 项目模板目录下的 context/business_context.md
    3. 如果都没有，返回空
    """
    from pathlib import Path

    repo = ProjectRepository(db)
    project = await repo.get(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context_content = ""
    context_files: List[str] = []
    local_path = project.local_path

    # 策略1: 如果有 local_path，尝试读取文件
    if local_path:
        base_path = Path(local_path)

        # 读取 context/business_context.md
        business_context_file = base_path / "context" / "business_context.md"
        if business_context_file.exists():
            try:
                context_content = business_context_file.read_text(encoding="utf-8")
            except Exception as e:
                context_content = f"（读取失败: {str(e)}）"

        # 扫描 context/ 目录下的所有文件
        context_dir = base_path / "context"
        if context_dir.exists() and context_dir.is_dir():
            for f in context_dir.rglob("*"):
                if f.is_file():
                    context_files.append(str(f.relative_to(base_path)))

    # 策略2: 如果没有 local_path 或文件不存在，尝试从项目模板目录读取
    if not context_content:
        template_context = (
            Path(__file__).parent.parent.parent.parent
            / "projects"
            / "_template"
            / "context"
            / "business_context.md"
        )
        if template_context.exists():
            try:
                context_content = template_context.read_text(encoding="utf-8")
            except Exception:
                pass

    return ContextResponse(
        project_id=project_id,
        project_name=project.name,
        local_path=local_path,
        business_context=context_content,
        has_context=bool(context_content.strip()),
        files=context_files,
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
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """生成 Playground 交互式看板。

    流程：
    1. 从 DB 获取项目信息
    2. 扫描 projects/ 目录找到对应的项目文件夹
    3. 调用项目目录下的 generate_playground.py 脚本
    4. 返回生成的 HTML 文件路径（供前端 iframe 加载）
    """
    import subprocess
    import re
    from pathlib import Path

    # 1. 获取项目
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 2. 查找项目目录（projects/{name}/）
    #    项目目录格式: projects/{project_name}_{date}/
    projects_root = Path(__file__).parent.parent.parent.parent / "projects"
    project_name = project.name
    matched_dir = None

    for candidate in projects_root.iterdir():
        if candidate.is_dir() and not candidate.name.startswith("_"):
            # 匹配：目录名以项目名开头，或包含项目名
            if candidate.name.startswith(project_name) or project_name in candidate.name:
                matched_dir = candidate
                break

    if not matched_dir:
        raise HTTPException(
            status_code=404,
            detail=f"未找到项目目录（projects/ 中无匹配 '{project_name}' 的文件夹）",
        )

    # 3. 确认 Playground 目录存在
    playground_dir = matched_dir / "05_Playground"
    generator_script = playground_dir / "generate_playground.py"
    template_html = playground_dir / "活动看板_v8.html"

    if not generator_script.exists():
        raise HTTPException(
            status_code=400,
            detail=f"generate_playground.py 不存在: {generator_script}",
        )

    # 4. 确定输出文件路径
    output_file = playground_dir / f"活动看板_{project_name}.html"

    # 5. 调用生成器脚本
    try:
        result = subprocess.run(
            [
                "python3",
                str(generator_script),
                "--project",
                str(matched_dir),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"生成失败: {result.stderr[:500]}",
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="生成超时（60s）")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成异常: {str(e)}")

    # 6. 返回相对路径（前端通过 /api/static/... 访问，或直接返回内容）
    #    转换为可通过后端静态文件服务访问的路径
    #    后端 static 挂载在 /static，projects 在项目根目录
    #    返回绝对路径让前端通过 fetch 获取 HTML 内容
    return {
        "status": "ok",
        "project_id": project_id,
        "playground_path": str(output_file.relative_to(projects_root.parent)),
        "playground_url": f"/api/v1/projects/{project_id}/playground/file",
        "generated_at": result.stdout.strip() if result.stdout else "",
    }


@router.get("/{project_id}/playground/file")
async def get_playground_file(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回生成的 Playground HTML 文件内容。

    前端通过 iframe srcdoc 或直接嵌入方式加载。
    """
    import re
    from pathlib import Path
    from fastapi.responses import HTMLResponse

    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    projects_root = Path(__file__).parent.parent.parent.parent / "projects"
    project_name = project.name

    matched_dir = None
    for candidate in projects_root.iterdir():
        if candidate.is_dir() and not candidate.name.startswith("_"):
            if candidate.name.startswith(project_name) or project_name in candidate.name:
                matched_dir = candidate
                break

    if not matched_dir:
        raise HTTPException(status_code=404, detail="项目目录不存在")

    output_file = matched_dir / "05_Playground" / f"活动看板_{project_name}.html"
    if not output_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Playground 文件尚未生成，请先调用 POST /playground 生成",
        )

    html_content = output_file.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)
