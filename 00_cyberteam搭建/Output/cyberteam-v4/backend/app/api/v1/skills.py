"""技能 API v1 - 真实化实现。

核心功能：
- Skill CRUD 操作
- Skill ↔ Agent 绑定统计
- Skill 分类浏览
- Skill 执行

API 路由：
- GET /api/v1/skills - 列出所有 Skill（支持 category/difficulty 过滤）
- GET /api/v1/skills/categories - Skill 分类列表
- GET /api/v1/skills/{skill_code} - Skill 详情（含使用它的 Agent 列表）
- POST /api/v1/skills - 创建自定义 Skill
- PUT /api/v1/skills/{skill_code} - 更新 Skill
- DELETE /api/v1/skills/{skill_code} - 删除 Skill
- GET /api/v1/skills/{skill_code}/agents - 使用此 Skill 的 Agent 列表
- POST /api/v1/skills/{skill_code}/execute - 执行 Skill
"""

import threading
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .agents import get_agent_store, get_skill_store

router = APIRouter(prefix="/skills", tags=["skills v1"])


# === Request/Response Models ===

class SkillCreate(BaseModel):
    """创建 Skill 请求"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., pattern=r"^[a-z0-9_-]+$")
    description: Optional[str] = None
    category: str = "custom"
    difficulty: str = "medium"
    trigger_keywords: List[str] = []
    success_metrics: Optional[dict] = {}
    config: Optional[dict] = {}


class SkillUpdate(BaseModel):
    """更新 Skill 请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    trigger_keywords: Optional[List[str]] = None
    success_metrics: Optional[dict] = None
    config: Optional[dict] = None


class SkillOut(BaseModel):
    """Skill 响应"""
    id: str
    code: str
    name: str
    description: Optional[str]
    category: str
    difficulty: str
    trigger_keywords: List[str]
    success_metrics: dict
    agent_count: int
    config: dict
    created_at: datetime
    updated_at: datetime


class SkillCategoryOut(BaseModel):
    """Skill 分类响应"""
    category: str
    count: int
    skills: List[SkillOut]


class AgentBriefOut(BaseModel):
    """Agent 简要信息（供 Skill 详情使用）"""
    id: str
    code: str
    name: str
    agent_type: str
    is_active: bool


class ExecuteSkillRequest(BaseModel):
    """执行 Skill 请求"""
    input: str = Field(..., description="输入内容")
    context: Optional[dict] = Field(default_factory=dict, description="上下文")


class ExecuteSkillResponse(BaseModel):
    """执行 Skill 响应"""
    execution_id: str
    skill_code: str
    status: str
    result: dict


# === Agent-Skill 绑定内存索引 ===
# agent_code -> list of skill_codes
_agent_skill_records: dict[str, list[str]] = {}
# skill_code -> list of agent_codes
_skill_agent_records: dict[str, list[str]] = {}


def _sync_skill_agent_records(agent_code: str, skill_codes: list[str]) -> None:
    """同步 skill-agent 记录到内存索引。"""
    _agent_skill_records[agent_code] = list(skill_codes)
    for skill_code in skill_codes:
        if skill_code not in _skill_agent_records:
            _skill_agent_records[skill_code] = []
        if agent_code not in _skill_agent_records[skill_code]:
            _skill_agent_records[skill_code].append(agent_code)


def _add_binding(agent_code: str, skill_code: str) -> None:
    """添加单个绑定到内存索引。"""
    if agent_code not in _agent_skill_records:
        _agent_skill_records[agent_code] = []
    if skill_code not in _agent_skill_records[agent_code]:
        _agent_skill_records[agent_code].append(skill_code)

    if skill_code not in _skill_agent_records:
        _skill_agent_records[skill_code] = []
    if agent_code not in _skill_agent_records[skill_code]:
        _skill_agent_records[skill_code].append(agent_code)


def _remove_binding(agent_code: str, skill_code: str) -> None:
    """从内存索引移除绑定。"""
    if agent_code in _agent_skill_records and skill_code in _agent_skill_records[agent_code]:
        _agent_skill_records[agent_code].remove(skill_code)
    if skill_code in _skill_agent_records and agent_code in _skill_agent_records[skill_code]:
        _skill_agent_records[skill_code].remove(agent_code)


# === Routes ===

@router.get("", response_model=List[SkillOut])
async def list_skills(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
):
    """列出所有 Skill（支持 category/difficulty 过滤）"""
    store = get_skill_store()
    agent_store = get_agent_store()

    skills = store.list_skills()

    # 过滤
    if category:
        skills = [s for s in skills if s.get("category") == category]
    if difficulty:
        skills = [s for s in skills if s.get("difficulty") == difficulty]

    # 补充 agent_count
    all_agents = agent_store.list_agents()
    agent_skill_map: dict[str, int] = {}
    for agent in all_agents:
        for skill_id in agent.get("skills", []):
            agent_skill_map[skill_id] = agent_skill_map.get(skill_id, 0) + 1

    for skill in skills:
        skill["agent_count"] = agent_skill_map.get(skill["code"], 0)

    return skills


@router.get("/categories", response_model=List[SkillCategoryOut])
async def get_skill_categories():
    """获取 Skill 分类列表"""
    store = get_skill_store()
    agent_store = get_agent_store()

    skills = store.list_skills()

    # 统计各分类的 Skill 数量
    category_map: dict[str, List[dict]] = {}
    for skill in skills:
        cat = skill.get("category", "custom")
        if cat not in category_map:
            category_map[cat] = []
        category_map[cat].append(skill)

    # 补充 agent_count
    all_agents = agent_store.list_agents()
    agent_skill_map: dict[str, int] = {}
    for agent in all_agents:
        for skill_id in agent.get("skills", []):
            agent_skill_map[skill_id] = agent_skill_map.get(skill_id, 0) + 1

    for skills_in_cat in category_map.values():
        for skill in skills_in_cat:
            skill["agent_count"] = agent_skill_map.get(skill["code"], 0)

    return [
        SkillCategoryOut(
            category=cat,
            count=len(skills_in_cat),
            skills=skills_in_cat,
        )
        for cat, skills_in_cat in category_map.items()
    ]


@router.get("/{skill_code}", response_model=SkillOut)
async def get_skill(skill_code: str):
    """获取 Skill 详情（含使用它的 Agent 列表）"""
    store = get_skill_store()
    agent_store = get_agent_store()

    skill = store.get_skill(skill_code)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_code} 不存在",
        )

    # 统计使用此 Skill 的 Agent 数量
    all_agents = agent_store.list_agents()
    agent_count = 0
    for agent in all_agents:
        if skill_code in agent.get("skills", []):
            agent_count += 1

    skill["agent_count"] = agent_count
    return skill


@router.post("", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
async def create_skill(request: SkillCreate):
    """创建自定义 Skill"""
    store = get_skill_store()
    try:
        skill = store.create_skill(request.model_dump())
        return skill
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{skill_code}", response_model=SkillOut)
async def update_skill(skill_code: str, request: SkillUpdate):
    """更新 Skill"""
    store = get_skill_store()
    agent_store = get_agent_store()

    skill = store.update_skill(skill_code, request.model_dump(exclude_unset=True))
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_code} 不存在",
        )

    # 补充 agent_count
    all_agents = agent_store.list_agents()
    agent_count = 0
    for agent in all_agents:
        if skill_code in agent.get("skills", []):
            agent_count += 1
    skill["agent_count"] = agent_count

    return skill


@router.delete("/{skill_code}")
async def delete_skill(skill_code: str):
    """删除 Skill"""
    store = get_skill_store()
    success = store.delete_skill(skill_code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_code} 不存在",
        )
    return {"status": "ok", "skill_code": skill_code}


@router.get("/{skill_code}/agents", response_model=List[AgentBriefOut])
async def get_skill_agents(skill_code: str):
    """获取使用此 Skill 的 Agent 列表"""
    store = get_skill_store()
    agent_store = get_agent_store()

    # 验证 Skill 存在
    skill = store.get_skill(skill_code)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_code} 不存在",
        )

    # 优先从内存索引获取，其次从 agent_store 遍历
    if skill_code in _skill_agent_records:
        agent_codes = _skill_agent_records[skill_code]
        matching_agents = []
        for agent_code in agent_codes:
            agent = agent_store.get_agent(agent_code)
            if agent:
                matching_agents.append(
                    AgentBriefOut(
                        id=agent["id"],
                        code=agent["code"],
                        name=agent["name"],
                        agent_type=agent.get("agent_type", "custom"),
                        is_active=agent.get("is_active", True),
                    )
                )
        return matching_agents

    # 回退：从 agent_store 遍历
    all_agents = agent_store.list_agents()
    matching_agents = [
        AgentBriefOut(
            id=agent["id"],
            code=agent["code"],
            name=agent["name"],
            agent_type=agent.get("agent_type", "custom"),
            is_active=agent.get("is_active", True),
        )
        for agent in all_agents
        if skill_code in agent.get("skills", [])
    ]

    return matching_agents


@router.post("/{skill_code}/agents/{agent_code}", status_code=status.HTTP_201_CREATED)
async def bind_skill_to_agent(skill_code: str, agent_code: str):
    """绑定 Skill 到 Agent（持久化到内存索引）"""
    store = get_skill_store()
    agent_store = get_agent_store()

    # 验证 Skill 存在
    skill = store.get_skill(skill_code)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_code} 不存在",
        )

    # 验证 Agent 存在
    agent = agent_store.get_agent(agent_code)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_code} 不存在",
        )

    # 添加绑定到 AgentStore
    updated_agent = agent_store.add_skill(agent_code, skill_code)
    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="绑定失败",
        )

    # 同步到内存索引
    _add_binding(agent_code, skill_code)

    return {
        "skill_code": skill_code,
        "agent_code": agent_code,
        "status": "bound",
    }


@router.delete("/{skill_code}/agents/{agent_code}")
async def unbind_skill_from_agent(skill_code: str, agent_code: str):
    """从 Agent 解绑 Skill"""
    agent_store = get_agent_store()

    # 验证 Agent 存在
    agent = agent_store.get_agent(agent_code)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_code} 不存在",
        )

    # 从 AgentStore 移除绑定
    updated_agent = agent_store.remove_skill(agent_code, skill_code)
    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="解绑失败",
        )

    # 从内存索引移除
    _remove_binding(agent_code, skill_code)

    return {
        "skill_code": skill_code,
        "agent_code": agent_code,
        "status": "unbound",
    }


@router.get("/agents/{agent_code}/skills")
async def get_agent_skills(agent_code: str):
    """获取 Agent 绑定的所有 Skill"""
    agent_store = get_agent_store()

    # 验证 Agent 存在
    agent = agent_store.get_agent(agent_code)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_code} 不存在",
        )

    # 从内存索引获取，或从 agent_store 获取
    skills = _agent_skill_records.get(agent_code, agent.get("skills", []))
    return {
        "agent_code": agent_code,
        "skills": skills,
        "count": len(skills),
    }


@router.post("/{skill_code}/execute", response_model=ExecuteSkillResponse)
async def execute_skill(skill_code: str, request: ExecuteSkillRequest):
    """执行 Skill"""
    store = get_skill_store()

    # 验证 Skill 存在
    skill = store.get_skill(skill_code)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_code} 不存在",
        )

    execution_id = str(uuid.uuid4())

    # Skill 执行逻辑（这里只是模拟）
    # 实际实现应该根据 skill 的 trigger_keywords 和 workflow 执行
    result = {
        "output": f"Skill {skill_code} executed with input: {request.input}",
        "context": request.context,
        "skill_name": skill.get("name"),
    }

    return ExecuteSkillResponse(
        execution_id=execution_id,
        skill_code=skill_code,
        status="completed",
        result=result,
    )
