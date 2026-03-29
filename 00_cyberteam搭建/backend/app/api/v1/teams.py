"""Teams API — Agent 团队管理，支持内置模板和用户自定义团队。"""
from __future__ import annotations

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.deps import get_db, get_current_user
from app.db.models import Team

router = APIRouter()

# Predefined team templates
BUILTIN_TEAMS = [
    {
        "id": "marketing-campaign",
        "name": "全渠道营销团队",
        "description": "CEO + COO + 营销部 + 设计部，适合全渠道营销任务",
        "members": ["ceo-agent", "coo-agent", "marketing-director", "design-director"],
        "skills": ["渠道推广四大避坑点", "渠道效果分析法", "短文案四姿势"],
        "status": "active",
        "is_builtin": True,
    },
    {
        "id": "product-launch",
        "name": "新品发布团队",
        "description": "CEO + 产品部 + 运营部 + 设计部，适合新品上市策划",
        "members": ["ceo-agent", "product-director", "operations-director", "design-director"],
        "skills": ["目标拆解为行动计划", "成功三要素分析"],
        "status": "active",
        "is_builtin": True,
    },
    {
        "id": "crisis-response",
        "name": "危机应对团队",
        "description": "CEO + 运营部 + 公关，适合紧急事件处理",
        "members": ["ceo-agent", "operations-director", "pr-agent"],
        "skills": ["风险预案", "杠铃破局点识别"],
        "status": "standby",
        "is_builtin": True,
    },
]


class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    members: list[str] = []
    skills: list[str] = []
    status: str = "active"


class TeamUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[list[str]] = None
    skills: Optional[list[str]] = None
    status: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    members: list[str]
    skills: list[str]
    status: str
    is_builtin: bool
    created_at: Optional[str] = None


@router.get("", response_model=list[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[TeamResponse]:
    """List all teams (built-in + user-created)."""
    user_id = current_user.get("sub", "anonymous")

    # Get user teams
    stmt = select(Team).where(Team.user_id == user_id).order_by(Team.created_at.desc())
    result = await db.execute(stmt)
    user_teams = result.scalars().all()

    # Combine built-in + user teams
    teams = [
        TeamResponse(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            members=t.get("members", []),
            skills=t.get("skills", []),
            status=t["status"],
            is_builtin=True,
        )
        for t in BUILTIN_TEAMS
    ] + [
        TeamResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            members=t.members or [],
            skills=t.skills or [],
            status=t.status,
            is_builtin=False,
            created_at=t.created_at.isoformat() if t.created_at else None,
        )
        for t in user_teams
    ]

    return teams


@router.post("", response_model=TeamResponse)
async def create_team(
    request: TeamCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TeamResponse:
    """Create a new team."""
    user_id = current_user.get("sub", "anonymous")

    team = Team(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        members=request.members,
        skills=request.skills,
        status=request.status,
        is_template=False,
        user_id=user_id,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        members=team.members or [],
        skills=team.skills or [],
        status=team.status,
        is_builtin=False,
        created_at=team.created_at.isoformat() if team.created_at else None,
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TeamResponse:
    """Get a team by ID."""
    user_id = current_user.get("sub", "anonymous")

    # Check built-in first
    for t in BUILTIN_TEAMS:
        if t["id"] == team_id:
            return TeamResponse(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                members=t.get("members", []),
                skills=t.get("skills", []),
                status=t["status"],
                is_builtin=True,
            )

    # Check user teams
    stmt = select(Team).where(Team.id == team_id, Team.user_id == user_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        members=team.members or [],
        skills=team.skills or [],
        status=team.status,
        is_builtin=False,
        created_at=team.created_at.isoformat() if team.created_at else None,
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    request: TeamUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> TeamResponse:
    """Update a team."""
    user_id = current_user.get("sub", "anonymous")

    # Cannot update built-in teams
    for t in BUILTIN_TEAMS:
        if t["id"] == team_id:
            raise HTTPException(status_code=403, detail="Cannot modify built-in teams")

    stmt = select(Team).where(Team.id == team_id, Team.user_id == user_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if request.name is not None:
        team.name = request.name
    if request.description is not None:
        team.description = request.description
    if request.members is not None:
        team.members = request.members
    if request.skills is not None:
        team.skills = request.skills
    if request.status is not None:
        team.status = request.status

    await db.commit()
    await db.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        members=team.members or [],
        skills=team.skills or [],
        status=team.status,
        is_builtin=False,
        created_at=team.created_at.isoformat() if team.created_at else None,
    )


@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a team."""
    user_id = current_user.get("sub", "anonymous")

    # Cannot delete built-in teams
    for t in BUILTIN_TEAMS:
        if t["id"] == team_id:
            raise HTTPException(status_code=403, detail="Cannot delete built-in teams")

    stmt = delete(Team).where(Team.id == team_id, Team.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Team not found")

    return {"status": "deleted", "id": team_id}