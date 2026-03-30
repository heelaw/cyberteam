"""Agent 管理 API v1 - 抄 Magic。

核心功能：
- 列出所有可用 Agent
- 获取 Agent 详情
- 编译 Agent
- 执行 Agent
- 查看 Agent 执行历史

API 路由：
- GET /api/v1/agents - 列出所有 Agent
- GET /api/v1/agents/{code} - 获取 Agent 详情
- POST /api/v1/agents/compile - 编译 Agent
- POST /api/v1/agents/{code}/execute - 执行 Agent
- GET /api/v1/agents/{code}/executions - 执行历史
"""

from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db import get_db
from ...auth import get_current_user
from ...engine import AgentCompiler, AgentProfile
from app.models import AgentExecution

router = APIRouter(prefix="/agents", tags=["agents v1"])


# === Request/Response Models ===

class AgentResponse(BaseModel):
    """Agent 响应。"""
    code: str
    name: str
    llm: str
    tools: List[str]
    departments: List[str]
    metadata: dict


class CompileRequest(BaseModel):
    """编译请求。"""
    agent_dir: str
    use_cache: bool = True


class ExecuteRequest(BaseModel):
    """执行请求。"""
    input: str
    context: dict = Field(default_factory=dict)
    thinking_modes: List[str] = Field(default_factory=list)


class ExecutionResponse(BaseModel):
    """执行响应。"""
    execution_id: str
    agent_code: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


# === Routes ===

@router.get("", response_model=List[AgentResponse])
async def list_agents(
    department: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """列出所有可用 Agent。"""
    # TODO: 从 AGENTS/ 目录扫描
    return []


@router.get("/{agent_code}", response_model=AgentResponse)
async def get_agent(
    agent_code: str,
    user: dict = Depends(get_current_user),
):
    """获取 Agent 详情。"""
    # TODO: 读取 Agent 配置文件
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")


@router.post("/compile")
async def compile_agent(
    request: CompileRequest,
    user: dict = Depends(get_current_user),
):
    """编译 Agent。"""
    compiler = AgentCompiler()

    try:
        agent_dir = Path(request.agent_dir)
        profile = await compiler.compile(agent_dir, use_cache=request.use_cache)

        return {
            "status": "ok",
            "agent_code": profile.code,
            "name": profile.name,
            "llm": profile.llm,
            "tools": profile.tools,
            "skills_count": len(profile.skills),
            "system_prompt_length": len(profile.system_prompt),
        }

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent directory not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{agent_code}/execute", response_model=ExecutionResponse)
async def execute_agent(
    agent_code: str,
    request: ExecuteRequest,
    user: dict = Depends(get_current_user),
):
    """执行 Agent。"""
    import uuid

    execution_id = str(uuid.uuid4())

    # TODO: 实际执行 Agent
    # 1. 加载 Agent 配置
    # 2. 注入思维模式
    # 3. 调用 LLM
    # 4. 记录执行日志

    return ExecutionResponse(
        execution_id=execution_id,
        agent_code=agent_code,
        status="completed",
        result={"output": "placeholder"},
    )


@router.get("/{agent_code}/executions")
async def get_agent_executions(
    agent_code: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取 Agent 执行历史。"""
    stmt = (
        select(AgentExecution)
        .where(AgentExecution.agent_name == agent_code)
        .order_by(AgentExecution.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    executions = list(result.scalars().all())

    return [
        {
            "id": e.id,
            "task_id": e.task_id,
            "agent_name": e.agent_name,
            "department": e.department,
            "status": e.status,
            "model_id": e.model_id,
            "input_tokens": e.input_tokens,
            "output_tokens": e.output_tokens,
            "cost_usd": e.cost_usd,
            "duration_ms": e.duration_ms,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in executions
    ]
