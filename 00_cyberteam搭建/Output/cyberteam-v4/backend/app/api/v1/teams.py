"""Teams API v1 - 内存存储的团队管理 API。

API 路由：
- POST /api/v1/teams - 创建团队
- GET /api/v1/teams - 列出团队（支持 company_id 过滤）
- GET /api/v1/teams/{team_id} - 获取团队详情
- PUT /api/v1/teams/{team_id} - 更新团队
- DELETE /api/v1/teams/{team_id} - 删除团队
- POST /api/v1/teams/{team_id}/members - 添加成员
- DELETE /api/v1/teams/{team_id}/members/{member_id} - 移除成员
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/teams", tags=["teams v1"])

# === 内存存储 ===
_teams: dict[str, dict] = {}


# === Request/Response Models ===

class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    company_id: Optional[str] = None
    members: list[str] = []
    config: dict = Field(default_factory=dict)


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[list[str]] = None
    config: Optional[dict] = None


class TeamOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    company_id: Optional[str]
    members: list[str]
    member_count: int
    config: dict
    created_at: datetime
    updated_at: datetime


class MemberAdd(BaseModel):
    member_id: str


# === Routes ===

@router.post("", response_model=TeamOut, status_code=201)
async def create_team(request: TeamCreate):
    team_id = str(uuid.uuid4())
    now = datetime.utcnow()
    team = {
        "id": team_id,
        "name": request.name,
        "description": request.description,
        "company_id": request.company_id,
        "members": list(request.members),
        "config": dict(request.config),
        "created_at": now,
        "updated_at": now,
    }
    _teams[team_id] = team
    return _to_out(team)


@router.get("", response_model=list[TeamOut])
async def list_teams(
    company_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    results = list(_teams.values())
    if company_id is not None:
        results = [t for t in results if t.get("company_id") == company_id]
    results.sort(key=lambda t: t["created_at"], reverse=True)
    return [_to_out(t) for t in results[skip : skip + limit]]


@router.get("/{team_id}", response_model=TeamOut)
async def get_team(team_id: str):
    if team_id not in _teams:
        raise HTTPException(status_code=404, detail=f"团队 {team_id} 不存在")
    return _to_out(_teams[team_id])


@router.put("/{team_id}", response_model=TeamOut)
async def update_team(team_id: str, request: TeamUpdate):
    if team_id not in _teams:
        raise HTTPException(status_code=404, detail=f"团队 {team_id} 不存在")
    team = _teams[team_id]
    if request.name is not None:
        team["name"] = request.name
    if request.description is not None:
        team["description"] = request.description
    if request.members is not None:
        team["members"] = request.members
    if request.config is not None:
        team["config"] = request.config
    team["updated_at"] = datetime.utcnow()
    return _to_out(team)


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: str):
    if team_id not in _teams:
        raise HTTPException(status_code=404, detail=f"团队 {team_id} 不存在")
    del _teams[team_id]


@router.post("/{team_id}/members", response_model=TeamOut)
async def add_member(team_id: str, request: MemberAdd):
    if team_id not in _teams:
        raise HTTPException(status_code=404, detail=f"团队 {team_id} 不存在")
    team = _teams[team_id]
    if request.member_id not in team["members"]:
        team["members"].append(request.member_id)
    team["updated_at"] = datetime.utcnow()
    return _to_out(team)


@router.delete("/{team_id}/members/{member_id}", response_model=TeamOut)
async def remove_member(team_id: str, member_id: str):
    if team_id not in _teams:
        raise HTTPException(status_code=404, detail=f"团队 {team_id} 不存在")
    team = _teams[team_id]
    if member_id in team["members"]:
        team["members"].remove(member_id)
    team["updated_at"] = datetime.utcnow()
    return _to_out(team)


def _to_out(t: dict) -> TeamOut:
    return TeamOut(
        id=t["id"],
        name=t["name"],
        description=t.get("description"),
        company_id=t.get("company_id"),
        members=t["members"],
        member_count=len(t["members"]),
        config=t.get("config", {}),
        created_at=t["created_at"],
        updated_at=t["updated_at"],
    )
