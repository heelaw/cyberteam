"""数字员工市场 REST API

核心功能：
- 列出所有专家 Agent（数字员工市场）
- 搜索/发现专家（关键词匹配）
- 获取专家详情
- 注册新专家
- 注销专家
- 调用专家 Agent 执行任务

API 路由：
- GET /api/expert-agents — 获取市场列表
- GET /api/expert-agents/discover?q=xxx — 搜索专家
- GET /api/expert-agents/{agent_id} — 获取专家详情
- POST /api/expert-agents — 注册新专家
- DELETE /api/expert-agents/{agent_id} — 注销专家
- POST /api/expert-agents/{agent_id}/invoke — 调用专家 Agent
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from pydantic import BaseModel, Field

from app.models.expert_agent import ExpertAgentProfile, ExpertAgentRegistry

router = APIRouter(prefix="/api/expert-agents", tags=["expert-agents"])


# === Request/Response Models ===

class ExpertAgentCreate(BaseModel):
    """创建专家 Agent 请求"""
    agent_id: str = Field(..., description="唯一标识")
    name: str = Field(..., description="名称")
    department: str = Field(..., description="所属部门")
    description: str = Field(default="", description="详细描述")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")
    keywords: list[str] = Field(default_factory=list, description="搜索关键词")
    avatar: str = Field(default="🤖", description="头像 emoji")


class ExpertAgentResponse(BaseModel):
    """专家 Agent 响应"""
    agent_id: str
    name: str
    department: str
    description: str
    capabilities: list[str]
    keywords: list[str]
    avatar: str
    rating: float
    call_count: int
    avg_response_time_ms: float
    status: str
    created_at: str
    updated_at: str


class InvokeRequest(BaseModel):
    """调用专家请求"""
    task: str = Field(..., description="任务描述")
    context: dict = Field(default_factory=dict, description="上下文")


class InvokeResponse(BaseModel):
    """调用专家响应"""
    success: bool
    agent_id: str
    agent_name: str
    result: Optional[dict] = None
    error: Optional[str] = None


def _profile_to_response(profile: ExpertAgentProfile) -> ExpertAgentResponse:
    """将 Profile 转换为响应模型"""
    return ExpertAgentResponse(
        agent_id=profile.agent_id,
        name=profile.name,
        department=profile.department,
        description=profile.description,
        capabilities=profile.capabilities,
        keywords=profile.keywords,
        avatar=profile.avatar,
        rating=profile.rating,
        call_count=profile.call_count,
        avg_response_time_ms=profile.avg_response_time_ms,
        status=profile.status,
        created_at=profile.created_at.isoformat() if profile.created_at else "",
        updated_at=profile.updated_at.isoformat() if profile.updated_at else "",
    )


# === Routes ===

@router.get("", response_model=list[ExpertAgentResponse])
async def list_expert_agents(
    department: Optional[str] = Query(None, description="按部门筛选"),
):
    """获取数字员工市场列表（按调用次数排序）"""
    registry = ExpertAgentRegistry.get_instance()
    agents = registry.get_market(department=department)
    return [_profile_to_response(agent) for agent in agents]


@router.get("/discover", response_model=list[ExpertAgentResponse])
async def discover_expert_agents(
    q: str = Query(..., description="搜索关键词"),
    department: Optional[str] = Query(None, description="按部门筛选"),
):
    """搜索专家（关键词匹配）"""
    registry = ExpertAgentRegistry.get_instance()
    agents = registry.discover(query=q, department=department)
    return [_profile_to_response(agent) for agent in agents]


@router.get("/{agent_id}", response_model=ExpertAgentResponse)
async def get_expert_agent(agent_id: str):
    """获取专家详情"""
    registry = ExpertAgentRegistry.get_instance()
    agent = registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Expert agent not found")
    return _profile_to_response(agent)


@router.post("", response_model=ExpertAgentResponse)
async def register_expert_agent(profile: ExpertAgentCreate):
    """注册新专家"""
    registry = ExpertAgentRegistry.get_instance()

    # 检查是否已存在
    if registry.get(profile.agent_id):
        raise HTTPException(status_code=409, detail="Expert agent already exists")

    # 创建新专家
    new_profile = ExpertAgentProfile(
        agent_id=profile.agent_id,
        name=profile.name,
        department=profile.department,
        description=profile.description,
        capabilities=profile.capabilities,
        keywords=profile.keywords,
        avatar=profile.avatar,
    )

    registry.register(new_profile)
    return _profile_to_response(new_profile)


@router.delete("/{agent_id}")
async def unregister_expert_agent(agent_id: str):
    """注销专家"""
    registry = ExpertAgentRegistry.get_instance()
    success = registry.unregister(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expert agent not found")
    return {"status": "ok", "message": f"Expert agent {agent_id} unregistered"}


@router.post("/{agent_id}/invoke", response_model=InvokeResponse)
async def invoke_expert_agent(agent_id: str, request: InvokeRequest):
    """调用专家 Agent 执行任务

    注意：TaskSchedulerDomainService 是未来的集成点，
    当前返回模拟响应。
    """
    import time
    import uuid

    registry = ExpertAgentRegistry.get_instance()
    agent = registry.get(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Expert agent not found")

    if agent.status != "online":
        raise HTTPException(status_code=400, detail=f"Expert agent is {agent.status}")

    # 记录调用
    start_time = time.time()

    # TODO: 集成 TaskSchedulerDomainService 进行实际调用
    # 目前返回模拟响应
    result = {
        "execution_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "agent_name": agent.name,
        "task": request.task,
        "status": "completed",
        "output": f"[模拟响应] 已执行任务: {request.task}",
    }

    response_time_ms = (time.time() - start_time) * 1000
    registry.record_call(agent_id, response_time_ms)

    return InvokeResponse(
        success=True,
        agent_id=agent_id,
        agent_name=agent.name,
        result=result,
    )