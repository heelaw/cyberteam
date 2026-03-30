"""Skills API — 技能管理。

提供 RESTful API 用于管理 Agent 技能。
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db
from ..models import Skill
from ..auth.dependencies import get_current_user, get_optional_user

log = logging.getLogger("cyberteam.api.skills")
router = APIRouter()


# ── Schemas ──

class SkillCreate(BaseModel):
    id: Optional[str] = Field(None)
    name: str
    category: str = "growth"
    description: str = ""
    triggerConditions: str = ""
    usageGuide: str = ""
    difficulty: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    success_metrics: Optional[dict] = None
    references: Optional[List[dict]] = None
    content: Optional[str] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    triggerConditions: Optional[str] = None
    usageGuide: Optional[str] = None
    difficulty: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    success_metrics: Optional[dict] = None
    references: Optional[List[dict]] = None
    content: Optional[str] = None


class SkillOut(BaseModel):
    id: str
    name: str
    category: str
    description: str
    triggerConditions: str
    usageGuide: str
    difficulty: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    success_metrics: Optional[dict] = None
    references: Optional[List[dict]] = None
    content: Optional[str] = None


# ── Endpoints ──

@router.get("")
async def list_skills(category: Optional[str] = None, db: AsyncSession = Depends(get_db)) -> List[SkillOut]:
    """获取所有技能列表，可按分类筛选。"""
    stmt = select(Skill)
    if category:
        stmt = stmt.filter(Skill.category == category)
    result = await db.execute(stmt)
    skills = result.scalars().all()
    return [SkillOut(
        id=s.id,
        name=s.name,
        category=s.category,
        description=s.description,
        triggerConditions=s.trigger_conditions,
        usageGuide=s.usage_guide,
        difficulty=s.difficulty,
        version=s.version,
        author=s.author,
        tags=s.tags or [],
        success_metrics=s.success_metrics,
        references=s.references,
        content=s.content
    ) for s in skills]


@router.get("/{skill_id}")
async def get_skill(skill_id: str, db: AsyncSession = Depends(get_db)) -> SkillOut:
    """获取单个技能详情。"""
    result = await db.execute(select(Skill).filter(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {skill_id}"
        )
    return SkillOut(
        id=skill.id,
        name=skill.name,
        category=skill.category,
        description=skill.description,
        triggerConditions=skill.trigger_conditions,
        usageGuide=skill.usage_guide,
        difficulty=skill.difficulty,
        version=skill.version,
        author=skill.author,
        tags=skill.tags or [],
        success_metrics=skill.success_metrics,
        references=skill.references,
        content=skill.content
    )


@router.post("")
async def create_skill(
    skill: SkillCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillOut:
    """创建新技能。"""
    import uuid
    skill_id = skill.id or str(uuid.uuid4())

    # Fix6: Skill ID 唯一性验证
    result = await db.execute(select(Skill).filter(Skill.id == skill_id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill编码已存在"
        )

    db_skill = Skill(
        id=skill_id,
        name=skill.name,
        category=skill.category,
        description=skill.description,
        trigger_conditions=skill.triggerConditions,
        usage_guide=skill.usageGuide,
        difficulty=skill.difficulty,
        version=skill.version,
        author=skill.author,
        tags=skill.tags,
        success_metrics=skill.success_metrics,
        references=skill.references,
        content=skill.content
    )
    db.add(db_skill)
    await db.commit()
    await db.refresh(db_skill)
    
    log.info(f"Skill created: {skill_id} - {skill.name}")
    return SkillOut(
        id=db_skill.id,
        name=db_skill.name,
        category=db_skill.category,
        description=db_skill.description,
        triggerConditions=db_skill.trigger_conditions,
        usageGuide=db_skill.usage_guide,
        difficulty=db_skill.difficulty,
        version=db_skill.version,
        author=db_skill.author,
        tags=db_skill.tags or [],
        success_metrics=db_skill.success_metrics,
        references=db_skill.references,
        content=db_skill.content
    )


@router.put("/{skill_id}")
async def update_skill(
    skill_id: str,
    skill: SkillUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillOut:
    """更新技能信息。"""
    result = await db.execute(select(Skill).filter(Skill.id == skill_id))
    db_skill = result.scalar_one_or_none()
    
    if not db_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {skill_id}"
        )
    
    update_data = skill.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "triggerConditions":
            setattr(db_skill, "trigger_conditions", value)
        elif field == "usageGuide":
            setattr(db_skill, "usage_guide", value)
        elif field == "success_metrics":
            setattr(db_skill, "success_metrics", value)
        elif field == "references":
            setattr(db_skill, "references", value)
        else:
            setattr(db_skill, field, value)
    
    await db.commit()
    await db.refresh(db_skill)
    
    log.info(f"Skill updated: {skill_id}")
    return SkillOut(
        id=db_skill.id,
        name=db_skill.name,
        category=db_skill.category,
        description=db_skill.description,
        triggerConditions=db_skill.trigger_conditions,
        usageGuide=db_skill.usage_guide,
        difficulty=db_skill.difficulty,
        version=db_skill.version,
        author=db_skill.author,
        tags=db_skill.tags or [],
        success_metrics=db_skill.success_metrics,
        references=db_skill.references,
        content=db_skill.content
    )


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """删除技能。"""
    result = await db.execute(select(Skill).filter(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {skill_id}"
        )
    
    await db.delete(skill)
    await db.commit()
    
    log.info(f"Skill deleted: {skill_id}")
    return {"status": "ok", "message": f"Skill {skill_id} deleted"}


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)) -> dict:
    """获取所有技能分类。"""
    result = await db.execute(select(Skill.category).distinct())
    categories = [row[0] for row in result.all() if row[0]]
    return {"categories": sorted(categories) if categories else []}
