"""Agents API endpoints — 支持内置 Agent YAML 和用户自定义 Agent CRUD。"""
from __future__ import annotations

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.deps import get_db, get_current_user
from app.db.models import CustomAgent
from app.engine.agent_compiler import agent_compiler, AgentProfile
from app.engine.thinking_injector import thinking_injector, ThinkingMode
from app.engine.model_gateway import model_gateway

router = APIRouter()


class AgentResponse(BaseModel):
    """Agent information response."""
    name: str
    llm: str
    tools: list[str]
    skills: list[str]
    departments: list[str]
    version: str
    description: str


class AgentCreateRequest(BaseModel):
    """Request to create a custom agent."""
    name: str
    llm: str = "claude"
    description: Optional[str] = ""
    system_prompt: Optional[str] = ""
    tools: list[str] = []
    skills: list[str] = []
    departments: list[str] = []


class AgentUpdateRequest(BaseModel):
    """Request to update a custom agent."""
    llm: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    tools: Optional[list[str]] = None
    skills: Optional[list[str]] = None
    departments: Optional[list[str]] = None
    is_active: Optional[bool] = None


class CustomAgentResponse(BaseModel):
    """Custom agent response."""
    id: str
    name: str
    llm: str
    description: Optional[str]
    tools: list[str]
    skills: list[str]
    departments: list[str]
    version: str
    is_active: bool
    created_at: str


class AgentRunRequest(BaseModel):
    """Request to run an agent."""
    task: str
    input_data: Optional[dict] = None
    thinking_mode: Optional[str] = None
    model: Optional[str] = None


class AgentRunResponse(BaseModel):
    """Response from agent execution."""
    execution_id: str
    status: str
    output: Optional[dict] = None
    error: Optional[str] = None


class SkillResponse(BaseModel):
    """Skill information."""
    name: str
    description: str
    thinking_questions: list[str]


# ============ Custom Agent CRUD (MUST be before /{name}) ============

@router.post("", response_model=CustomAgentResponse)
async def create_agent(
    request: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new custom agent."""
    user_id = current_user.get("sub", "anonymous")

    # Check if name already exists (in DB or YAML)
    stmt = select(CustomAgent).where(CustomAgent.name == request.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Agent '{request.name}' already exists")
    if agent_compiler.get_agent(request.name):
        raise HTTPException(status_code=400, detail=f"Agent '{request.name}' conflicts with built-in agent")

    agent = CustomAgent(
        id=str(uuid.uuid4()),
        name=request.name,
        llm=request.llm,
        description=request.description,
        system_prompt=request.system_prompt,
        tools=request.tools,
        skills=request.skills,
        departments=request.departments,
        version="1.0.0",
        is_active=True,
        user_id=user_id,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    # Sync to compiler cache so chat can find it
    agent_compiler.add_custom_agent(agent)

    return CustomAgentResponse(
        id=agent.id,
        name=agent.name,
        llm=agent.llm,
        description=agent.description,
        tools=agent.tools or [],
        skills=agent.skills or [],
        departments=agent.departments or [],
        version=agent.version,
        is_active=agent.is_active,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
    )


@router.get("/custom", response_model=list[CustomAgentResponse])
async def list_custom_agents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List user's custom agents."""
    user_id = current_user.get("sub", "anonymous")
    stmt = (
        select(CustomAgent)
        .where(CustomAgent.user_id == user_id)
        .order_by(CustomAgent.created_at.desc())
    )
    result = await db.execute(stmt)
    agents = result.scalars().all()

    return [
        CustomAgentResponse(
            id=a.id,
            name=a.name,
            llm=a.llm,
            description=a.description,
            tools=a.tools or [],
            skills=a.skills or [],
            departments=a.departments or [],
            version=a.version,
            is_active=a.is_active,
            created_at=a.created_at.isoformat() if a.created_at else "",
        )
        for a in agents
    ]


@router.get("/custom/{agent_id}", response_model=CustomAgentResponse)
async def get_custom_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a custom agent by ID."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(CustomAgent).where(
        CustomAgent.id == agent_id,
        CustomAgent.user_id == user_id,
    )
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return CustomAgentResponse(
        id=agent.id,
        name=agent.name,
        llm=agent.llm,
        description=agent.description,
        tools=agent.tools or [],
        skills=agent.skills or [],
        departments=agent.departments or [],
        version=agent.version,
        is_active=agent.is_active,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
    )


@router.put("/custom/{agent_id}", response_model=CustomAgentResponse)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a custom agent."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(CustomAgent).where(
        CustomAgent.id == agent_id,
        CustomAgent.user_id == user_id,
    )
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update only provided fields
    if request.llm is not None:
        agent.llm = request.llm
    if request.description is not None:
        agent.description = request.description
    if request.system_prompt is not None:
        agent.system_prompt = request.system_prompt
    if request.tools is not None:
        agent.tools = request.tools
    if request.skills is not None:
        agent.skills = request.skills
    if request.departments is not None:
        agent.departments = request.departments
    if request.is_active is not None:
        agent.is_active = request.is_active

    await db.commit()
    await db.refresh(agent)

    return CustomAgentResponse(
        id=agent.id,
        name=agent.name,
        llm=agent.llm,
        description=agent.description,
        tools=agent.tools or [],
        skills=agent.skills or [],
        departments=agent.departments or [],
        version=agent.version,
        is_active=agent.is_active,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
    )


@router.delete("/custom/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a custom agent."""
    user_id = current_user.get("sub", "anonymous")
    stmt = delete(CustomAgent).where(
        CustomAgent.id == agent_id,
        CustomAgent.user_id == user_id,
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {"status": "deleted", "id": agent_id}


# ============ Built-in Agent Endpoints ============

@router.get("")
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[AgentResponse]:
    """List all available agents (built-in from YAML + custom from DB)."""
    user_id = current_user.get("sub", "anonymous")

    # YAML built-in agents
    yaml_agents = agent_compiler.get_available_agents()

    # DB custom agents (user's own)
    stmt = select(CustomAgent).where(
        CustomAgent.user_id == user_id,
        CustomAgent.is_active == True,
    )
    result = await db.execute(stmt)
    db_agents = result.scalars().all()

    # Add DB agents to compiler cache
    for db_agent in db_agents:
        agent_compiler.add_custom_agent(db_agent)

    all_agents = yaml_agents + [
        AgentProfile(
            name=a.name,
            llm=a.llm,
            description=a.description or "",
            tools=a.tools or [],
            skills=a.skills or [],
            departments=a.departments or [],
            version=a.version,
            is_custom=True,
        )
        for a in db_agents
    ]

    return [
        AgentResponse(
            name=a.name,
            llm=a.llm,
            tools=a.tools,
            skills=a.skills,
            departments=a.departments,
            version=a.version,
            description=a.description,
        )
        for a in all_agents
    ]


@router.get("/modes")
async def list_thinking_modes() -> list[str]:
    """List all available thinking modes."""
    return [mode.value for mode in thinking_injector.list_modes()]


@router.get("/models")
async def list_models() -> list[str]:
    """List all available models."""
    return model_gateway.list_models()


@router.get("/{name}", response_model=AgentResponse)
async def get_agent(name: str) -> AgentResponse:
    """Get agent details by name."""
    agent = agent_compiler.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    return AgentResponse(
        name=agent.name,
        llm=agent.llm,
        tools=agent.tools,
        skills=agent.skills,
        departments=agent.departments,
        version=agent.version,
        description=agent.description,
    )


@router.post("/{name}/run", response_model=AgentRunResponse)
async def run_agent(
    name: str,
    request: AgentRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AgentRunResponse:
    """Run an agent with given task."""
    agent = agent_compiler.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    # TODO: Implement actual agent execution
    return AgentRunResponse(
        execution_id=f"exec_{name}_{id(request)}",
        status="pending",
        output=None,
        error=None,
    )


@router.get("/{name}/skills", response_model=list[SkillResponse])
async def get_agent_skills(name: str) -> list[SkillResponse]:
    """Get skills available for an agent."""
    agent = agent_compiler.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    skills = []
    for skill_name in agent.skills:
        skills.append(SkillResponse(
            name=skill_name,
            description=f"Skill: {skill_name}",
            thinking_questions=[],
        ))

    return skills


@router.post("/{name}/compile")
async def compile_agent(name: str) -> dict:
    """Recompile an agent from source files."""
    agent_dir = agent_compiler.agents_dir / name
    if not agent_dir.exists():
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    try:
        profile = agent_compiler.compile(agent_dir)
        return {
            "status": "success",
            "name": profile.name,
            "llm": profile.llm,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))