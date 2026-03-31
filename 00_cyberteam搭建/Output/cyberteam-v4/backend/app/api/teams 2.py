"""Teams API — Agent 团队管理。

提供 RESTful API 用于创建、管理 Agent 团队。
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db
from ..models import Team

log = logging.getLogger("cyberteam.api.teams")
router = APIRouter()


# ── Schemas ──

class TeamCreate(BaseModel):
    id: Optional[str] = Field(None)
    name: str
    description: str = ""
    agentIds: List[str] = Field(default_factory=list)
    coordinationMode: str = "sequential"  # sequential/parallel/hierarchical
    reportingCycle: str = "daily"  # daily/weekly/monthly


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agentIds: Optional[List[str]] = None
    coordinationMode: Optional[str] = None
    reportingCycle: Optional[str] = None


class TeamOut(BaseModel):
    id: str
    name: str
    description: str
    agentIds: List[str]
    coordinationMode: str
    reportingCycle: str


# ── Endpoints ──

@router.get("")
async def list_teams(db: AsyncSession = Depends(get_db)) -> List[TeamOut]:
    """获取所有团队列表。"""
    result = await db.execute(select(Team))
    teams = result.scalars().all()
    return [TeamOut(
        id=t.id,
        name=t.name,
        description=t.description,
        agentIds=t.agent_ids or [],
        coordinationMode=t.coordination_mode,
        reportingCycle=t.reporting_cycle
    ) for t in teams]


@router.get("/{team_id}")
async def get_team(team_id: str, db: AsyncSession = Depends(get_db)) -> TeamOut:
    """获取单个团队详情。"""
    result = await db.execute(select(Team).filter(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team not found: {team_id}"
        )
    return TeamOut(
        id=team.id,
        name=team.name,
        description=team.description,
        agentIds=team.agent_ids or [],
        coordinationMode=team.coordination_mode,
        reportingCycle=team.reporting_cycle
    )


@router.post("")
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db)) -> TeamOut:
    """创建新团队。"""
    import uuid
    team_id = team.id or str(uuid.uuid4())
    
    db_team = Team(
        id=team_id,
        name=team.name,
        description=team.description,
        agent_ids=team.agentIds,
        coordination_mode=team.coordinationMode,
        reporting_cycle=team.reportingCycle
    )
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    
    log.info(f"Team created: {team_id} - {team.name}")
    return TeamOut(
        id=db_team.id,
        name=db_team.name,
        description=db_team.description,
        agentIds=db_team.agent_ids or [],
        coordinationMode=db_team.coordination_mode,
        reportingCycle=db_team.reporting_cycle
    )


@router.put("/{team_id}")
async def update_team(team_id: str, team: TeamUpdate, db: AsyncSession = Depends(get_db)) -> TeamOut:
    """更新团队信息。"""
    result = await db.execute(select(Team).filter(Team.id == team_id))
    db_team = result.scalar_one_or_none()
    
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team not found: {team_id}"
        )
    
    update_data = team.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "agentIds":
            setattr(db_team, "agent_ids", value)
        elif field == "coordinationMode":
            setattr(db_team, "coordination_mode", value)
        elif field == "reportingCycle":
            setattr(db_team, "reporting_cycle", value)
        else:
            setattr(db_team, field, value)
    
    await db.commit()
    await db.refresh(db_team)
    
    log.info(f"Team updated: {team_id}")
    return TeamOut(
        id=db_team.id,
        name=db_team.name,
        description=db_team.description,
        agentIds=db_team.agent_ids or [],
        coordinationMode=db_team.coordination_mode,
        reportingCycle=db_team.reporting_cycle
    )


@router.delete("/{team_id}")
async def delete_team(team_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """删除团队。"""
    result = await db.execute(select(Team).filter(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team not found: {team_id}"
        )
    
    await db.delete(team)
    await db.commit()
    
    log.info(f"Team deleted: {team_id}")
    return {"status": "ok", "message": f"Team {team_id} deleted"}


@router.get("/{team_id}/agents")
async def get_team_agents(team_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """获取团队成员列表。"""
    result = await db.execute(select(Team).filter(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team not found: {team_id}"
        )
    return {
        "team_id": team_id,
        "agents": team.agent_ids or [],
        "count": len(team.agent_ids or [])
    }
