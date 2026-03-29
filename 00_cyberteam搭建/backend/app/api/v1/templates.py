"""Templates API — 任务模板管理，支持内置模板和用户自定义模板。"""
from __future__ import annotations

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.deps import get_db, get_current_user
from app.db.models import Template

router = APIRouter()

# Predefined task templates
BUILTIN_TEMPLATES = [
    {
        "id": "marketing-plan",
        "name": "全渠道营销方案",
        "description": "CEO→COO→营销部→设计部 完整营销策划流程",
        "department": "marketing",
        "steps": [
            "CEO→COO 战略对齐",
            "COO→专家 策略讨论",
            "COO→专家 风险预案",
            "COO→CEO 汇报审批",
            "设计联动",
            "文案产出",
            "CEO汇总",
            "复盘进化",
        ],
        "estimated_time": "30min",
        "is_builtin": True,
    },
    {
        "id": "product-strategy",
        "name": "产品策略分析",
        "description": "CEO→产品部→运营部 产品规划分析",
        "department": "product",
        "steps": [
            "CEO→产品总监 需求对齐",
            "产品总监→专家 用户分析",
            "产品总监→专家 竞品分析",
            "产品总监→CEO 方案汇报",
        ],
        "estimated_time": "20min",
        "is_builtin": True,
    },
    {
        "id": "crisis-response",
        "name": "危机应对",
        "description": "CEO→运营部→公关部 紧急事件处理",
        "department": "operations",
        "steps": [
            "CEO→COO 危机评估",
            "COO→运营总监 方案制定",
            "运营总监→公关 执行",
            "COO→CEO 结果汇报",
        ],
        "estimated_time": "15min",
        "is_builtin": True,
    },
]


class TemplateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    department: Optional[str] = ""
    steps: list[str] = []
    estimated_time: Optional[str] = ""


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    steps: Optional[list[str]] = None
    estimated_time: Optional[str] = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    department: Optional[str]
    steps: list[str]
    estimated_time: Optional[str]
    is_builtin: bool
    created_at: Optional[str] = None


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[TemplateResponse]:
    """List all templates (built-in + user-created)."""
    user_id = current_user.get("sub", "anonymous")

    # Get user templates
    stmt = select(Template).where(Template.user_id == user_id).order_by(Template.created_at.desc())
    result = await db.execute(stmt)
    user_templates = result.scalars().all()

    # Combine built-in + user templates
    templates = [
        TemplateResponse(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            department=t.get("department"),
            steps=t.get("steps", []),
            estimated_time=t.get("estimated_time"),
            is_builtin=True,
        )
        for t in BUILTIN_TEMPLATES
    ] + [
        TemplateResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            department=t.department,
            steps=t.steps or [],
            estimated_time=t.estimated_time,
            is_builtin=False,
            created_at=t.created_at.isoformat() if t.created_at else None,
        )
        for t in user_templates
    ]

    return templates


@router.post("", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """Create a new template."""
    user_id = current_user.get("sub", "anonymous")

    template = Template(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        department=request.department,
        steps=request.steps,
        estimated_time=request.estimated_time,
        is_template=True,
        user_id=user_id,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)

    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        department=template.department,
        steps=template.steps or [],
        estimated_time=template.estimated_time,
        is_builtin=False,
        created_at=template.created_at.isoformat() if template.created_at else None,
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """Get a template by ID."""
    user_id = current_user.get("sub", "anonymous")

    # Check built-in first
    for t in BUILTIN_TEMPLATES:
        if t["id"] == template_id:
            return TemplateResponse(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                department=t.get("department"),
                steps=t.get("steps", []),
                estimated_time=t.get("estimated_time"),
                is_builtin=True,
            )

    # Check user templates
    stmt = select(Template).where(Template.id == template_id, Template.user_id == user_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        department=template.department,
        steps=template.steps or [],
        estimated_time=template.estimated_time,
        is_builtin=False,
        created_at=template.created_at.isoformat() if template.created_at else None,
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TemplateResponse:
    """Update a template."""
    user_id = current_user.get("sub", "anonymous")

    # Cannot update built-in templates
    for t in BUILTIN_TEMPLATES:
        if t["id"] == template_id:
            raise HTTPException(status_code=403, detail="Cannot modify built-in templates")

    stmt = select(Template).where(Template.id == template_id, Template.user_id == user_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if request.name is not None:
        template.name = request.name
    if request.description is not None:
        template.description = request.description
    if request.department is not None:
        template.department = request.department
    if request.steps is not None:
        template.steps = request.steps
    if request.estimated_time is not None:
        template.estimated_time = request.estimated_time

    await db.commit()
    await db.refresh(template)

    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        department=template.department,
        steps=template.steps or [],
        estimated_time=template.estimated_time,
        is_builtin=False,
        created_at=template.created_at.isoformat() if template.created_at else None,
    )


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a template."""
    user_id = current_user.get("sub", "anonymous")

    # Cannot delete built-in templates
    for t in BUILTIN_TEMPLATES:
        if t["id"] == template_id:
            raise HTTPException(status_code=403, detail="Cannot delete built-in templates")

    stmt = delete(Template).where(Template.id == template_id, Template.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"status": "deleted", "id": template_id}