"""Company API — 公司组织架构管理。

提供 RESTful API 用于：
- 公司创建与管理
- 部门订阅与实例化
- Agent分配与管理
- 技能激活与管理
- CEO → 部门Leader → Agent 执行链路
"""

import uuid
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..db import get_db
from ..models import Company, CompanyDepartment, CompanyAgent, CompanySkill, Subscription, Agent, Department

log = logging.getLogger("cyberteam.api.company")
router = APIRouter()

_backend_path = Path(__file__).parent.parent.parent
for p in [str(_backend_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Agent模板定义 (市场Agent) ──

DEFAULT_AGENTS = {
    "strategy": {
        "agent_id": "strategy",
        "name": "战略专家",
        "role": "战略总监",
        "level": 2,
        "description": "负责战略规划、竞争分析、商业模式设计",
        "skills": ["战略规划", "竞争分析", "商业模式", "投资分析"],
        "department_id": "ceo",
    },
    "product": {
        "agent_id": "product",
        "name": "产品专家",
        "role": "产品总监",
        "level": 2,
        "description": "负责需求分析、产品设计、功能规划",
        "skills": ["需求分析", "产品规划", "原型设计", "用户研究"],
        "department_id": "product",
    },
    "engineering": {
        "agent_id": "engineering",
        "name": "技术专家",
        "role": "技术总监",
        "level": 2,
        "description": "负责技术方案、架构设计、开发实现",
        "skills": ["系统架构", "后端开发", "前端开发", "测试", "DevOps"],
        "department_id": "engineering",
    },
    "design": {
        "agent_id": "design",
        "name": "设计专家",
        "role": "设计总监",
        "level": 2,
        "description": "负责UI设计、用户体验、品牌视觉",
        "skills": ["UI设计", "UX设计", "品牌设计", "视觉设计"],
        "department_id": "design",
    },
    "operations": {
        "agent_id": "operations",
        "name": "运营专家",
        "role": "运营总监",
        "level": 2,
        "description": "负责用户增长、内容运营、活动策划",
        "skills": ["用户运营", "内容运营", "活动策划", "数据分析"],
        "department_id": "operations",
    },
    "marketing": {
        "agent_id": "marketing",
        "name": "营销专家",
        "role": "市场总监",
        "level": 2,
        "description": "负责市场营销、品牌推广、渠道拓展",
        "skills": ["品牌营销", "效果营销", "内容营销", "渠道推广"],
        "department_id": "marketing",
    },
    "finance": {
        "agent_id": "finance",
        "name": "财务专家",
        "role": "财务总监",
        "level": 2,
        "description": "负责预算规划、成本控制、投资分析",
        "skills": ["预算管理", "成本控制", "财务分析", "投资决策"],
        "department_id": "finance",
    },
    "hr": {
        "agent_id": "hr",
        "name": "人力专家",
        "role": "人力总监",
        "level": 2,
        "description": "负责招聘方案、团队激励、文化建设",
        "skills": ["招聘", "培训", "绩效管理", "团队建设"],
        "department_id": "hr",
    },
}

# ── CEO Agent定义 (内置，不可变) ──

CEO_AGENT = {
    "agent_id": "ceo",
    "name": "CEO",
    "role": "首席执行官",
    "level": 1,
    "description": "内置CEO Agent，负责整体战略协调和任务分配",
    "skills": ["战略规划", "决策制定", "资源分配", "风险管理", "任务协调"],
    "department_id": "ceo",
    "is_built_in": True,
}

# ── Schemas ──


class CompanyCreate(BaseModel):
    """创建公司请求。"""
    company_id: str = Field(..., description="公司唯一标识 (如 com_xxx)")
    name: str = Field(..., description="公司名称")
    description: Optional[str] = Field(None, description="公司描述")
    industry: Optional[str] = Field(None, description="行业")
    scale: Optional[str] = Field(None, description="规模: 小型/中型/大型")


class CompanyUpdate(BaseModel):
    """更新公司请求。"""
    name: Optional[str] = Field(None, description="公司名称")
    description: Optional[str] = Field(None, description="公司描述")
    industry: Optional[str] = Field(None, description="行业")
    scale: Optional[str] = Field(None, description="规模")
    config: Optional[dict] = Field(None, description="自定义配置")


class CompanyOut(BaseModel):
    """公司信息响应。"""
    id: str
    company_id: str
    name: str
    description: Optional[str]
    industry: Optional[str]
    scale: Optional[str]
    config: dict
    ceo_agent_id: str
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class CompanyDepartmentCreate(BaseModel):
    """订阅部门请求。"""
    company_id: str = Field(..., description="公司ID")
    department_id: str = Field(..., description="要订阅的部门模板ID (如 operations)")
    name: Optional[str] = Field(None, description="自定义部门名称")
    parent_id: Optional[str] = Field(None, description="上级部门实例ID")


class CompanyDepartmentUpdate(BaseModel):
    """更新公司部门请求。"""
    name: Optional[str] = Field(None, description="部门名称")
    description: Optional[str] = Field(None, description="部门描述")
    leader_agent_id: Optional[str] = Field(None, description="部门Leader Agent ID")
    status: Optional[str] = Field(None, description="状态")


class CompanyDepartmentOut(BaseModel):
    """公司部门响应。"""
    id: str
    company_id: str
    source_department_id: str
    department_id: str
    name: str
    description: Optional[str]
    responsibility: Optional[str]
    parent_id: Optional[str]
    leader_agent_id: Optional[str]
    subscribed_at: Optional[str]
    subscription_tier: str
    status: str


class CompanyAgentCreate(BaseModel):
    """分配Agent请求。"""
    company_id: str = Field(..., description="公司ID")
    agent_id: str = Field(..., description="Agent模板ID")
    department_id: str = Field(..., description="归属部门实例ID")
    name: Optional[str] = Field(None, description="自定义名称")
    role: Optional[str] = Field(None, description="角色")
    skills: Optional[List[str]] = Field(None, description="激活的技能列表")


class CompanyAgentUpdate(BaseModel):
    """更新Agent请求。"""
    name: Optional[str] = Field(None, description="名称")
    department_id: Optional[str] = Field(None, description="归属部门")
    is_leader: Optional[bool] = Field(None, description="设为部门Leader")
    skills: Optional[List[str]] = Field(None, description="技能列表")
    status: Optional[str] = Field(None, description="状态")


class CompanyAgentOut(BaseModel):
    """CompanyAgent响应。"""
    id: str
    company_id: str
    source_agent_id: str
    agent_id: str
    name: str
    department_id: str
    is_leader: bool
    role: Optional[str]
    level: int
    skills: List[str]
    status: str


class SubscriptionCreate(BaseModel):
    """订阅请求。"""
    user_id: str = Field(..., description="用户ID")
    company_id: str = Field(..., description="公司ID")
    subscription_type: str = Field(..., description="类型: department/agent/skill")
    target_id: str = Field(..., description="目标ID")
    tier: str = Field(default="免费", description="订阅等级")
    price: Optional[float] = Field(None, description="价格")


class ExecuteTaskRequest(BaseModel):
    """CEO执行任务请求。"""
    task: str = Field(..., description="任务描述")
    target_department_id: Optional[str] = Field(None, description="指定执行部门")
    priority: str = Field(default="中", description="优先级")
    context: Optional[dict] = Field(None, description="执行上下文")


class RouteTestRequest(BaseModel):
    """路由测试请求。"""
    task: str = Field(..., description="要测试的任务描述")
    context: Optional[dict] = Field(None, description="上下文信息")


class RouteTestResponse(BaseModel):
    """路由测试响应。"""
    target_department: str
    match_score: float
    reasoning: str
    alternative_departments: List[dict]
    department_metadata: Optional[dict] = None


class SubscriptionOut(BaseModel):
    """订阅响应。"""
    id: str
    user_id: str
    company_id: str
    subscription_type: str
    target_id: str
    tier: str
    price: Optional[float]
    instance_id: Optional[str]
    status: str
    subscribed_at: Optional[str]


class OrgChartOut(BaseModel):
    """组织架构图响应。"""
    company: CompanyOut
    departments: List[CompanyDepartmentOut]
    agents: List[CompanyAgentOut]
    ceo: dict = Field(default_factory=dict)


# ── 辅助函数 ──


async def _create_company_department(
    db: AsyncSession,
    company: Company,
    source_dept_id: str,
    parent_id: Optional[str] = None,
    custom_name: Optional[str] = None,
) -> CompanyDepartment:
    """创建公司部门实例 (从市场订阅)。"""
    # 获取模板部门信息
    from .departments import DEFAULT_DEPARTMENTS

    if source_dept_id in DEFAULT_DEPARTMENTS:
        template = DEFAULT_DEPARTMENTS[source_dept_id]
    else:
        stmt = select(Department).filter(Department.department_id == source_dept_id)
        result = await db.execute(stmt)
        db_dept = result.scalar_one_or_none()
        if not db_dept:
            raise ValueError(f"Department not found: {source_dept_id}")
        template = db_dept.to_dict()

    # 生成公司部门实例ID
    dept_instance_id = f"c{company.id[:8]}_{source_dept_id}"

    # 创建部门实例
    dept = CompanyDepartment(
        id=str(uuid.uuid4()),
        company_id=company.company_id,
        source_department_id=source_dept_id,
        department_id=dept_instance_id,
        name=custom_name or template.get("name", source_dept_id),
        description=template.get("description", ""),
        responsibility=template.get("responsibility", ""),
        parent_id=parent_id,
        subscribed_at=datetime.utcnow(),
        subscription_tier="免费",
        status="active",
    )
    db.add(dept)
    return dept


async def _create_company_agents(
    db: AsyncSession,
    company: Company,
    department: CompanyDepartment,
) -> List[CompanyAgent]:
    """为部门创建默认Agent实例。"""
    # 从市场Agent模板创建立即可用的Agent
    # 实际场景中应该从Agent市场获取模板
    agents = []

    # 为每个部门创建部门Leader
    leader = CompanyAgent(
        id=str(uuid.uuid4()),
        company_id=company.company_id,
        source_agent_id=f"{department.source_department_id}_leader",
        agent_id=f"c{company.id[:8]}_{department.source_department_id}_leader",
        name=f"{department.name}总监",
        department_id=department.department_id,
        is_leader=True,
        role="部门总监",
        level=2,
        skills=department.responsibility.split(",") if department.responsibility else [],
        status="active",
    )
    db.add(leader)
    agents.append(leader)

    # 创建执行Agent
    executor = CompanyAgent(
        id=str(uuid.uuid4()),
        company_id=company.company_id,
        source_agent_id=f"{department.source_department_id}_executor",
        agent_id=f"c{company.id[:8]}_{department.source_department_id}_executor",
        name=f"{department.name}专家",
        department_id=department.department_id,
        is_leader=False,
        role="执行专家",
        level=3,
        skills=[],
        status="active",
    )
    db.add(executor)
    agents.append(executor)

    return agents


# ── Endpoints ──

# ── 公司管理 ──


@router.post("/companies", status_code=status.HTTP_201_CREATED, response_model=CompanyOut)
async def create_company(body: CompanyCreate, db: AsyncSession = Depends(get_db)):
    """创建公司。

    用户注册后创建公司，自动绑定CEO Agent。
    """
    # 检查公司ID是否已存在
    stmt = select(Company).filter(Company.company_id == body.company_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"Company already exists: {body.company_id}")

    company = Company(
        id=str(uuid.uuid4()),
        company_id=body.company_id,
        name=body.name,
        description=body.description,
        industry=body.industry,
        scale=body.scale,
        ceo_agent_id=CEO_AGENT["agent_id"],
        status="active",
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)

    log.info(f"Company created: {body.company_id}")
    return CompanyOut(**company.to_dict())


@router.get("/companies/{company_id}", response_model=CompanyOut)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """获取公司详情。"""
    stmt = select(Company).filter(Company.company_id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    return CompanyOut(**company.to_dict())


@router.put("/companies/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新公司信息。"""
    stmt = select(Company).filter(Company.company_id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(company, field, value)

    await db.commit()
    await db.refresh(company)

    return CompanyOut(**company.to_dict())


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """删除公司 (软删除)。"""
    stmt = select(Company).filter(Company.company_id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    company.status = "inactive"
    await db.commit()


@router.get("/companies/{company_id}/org-chart", response_model=OrgChartOut)
async def get_org_chart(company_id: str, db: AsyncSession = Depends(get_db)):
    """获取公司组织架构图。

    返回完整的三层架构:
    1. CEO (内置)
    2. 部门Leader
    3. 执行Agent
    """
    # 获取公司
    stmt = select(Company).filter(Company.company_id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    # 获取所有部门
    stmt = select(CompanyDepartment).filter(
        and_(CompanyDepartment.company_id == company_id, CompanyDepartment.status == "active")
    )
    depts = (await db.execute(stmt)).scalars().all()

    # 获取所有Agent
    stmt = select(CompanyAgent).filter(
        and_(CompanyAgent.company_id == company_id, CompanyAgent.status == "active")
    )
    agents = (await db.execute(stmt)).scalars().all()

    return OrgChartOut(
        company=CompanyOut(**company.to_dict()),
        departments=[CompanyDepartmentOut(**d.to_dict()) for d in depts],
        agents=[CompanyAgentOut(**a.to_dict()) for a in agents],
        ceo=CEO_AGENT,
    )

# ── 公司部门管理 ──


@router.post("/departments", status_code=status.HTTP_201_CREATED, response_model=CompanyDepartmentOut)
async def subscribe_department(body: CompanyDepartmentCreate, db: AsyncSession = Depends(get_db)):
    """订阅部门市场中的部门。

    订阅后:
    1. 在公司中创建部门实例
    2. 自动创建部门Leader Agent
    3. 自动创建执行Agent
    """
    # 验证公司存在
    stmt = select(Company).filter(Company.company_id == body.company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {body.company_id}")

    # 创建部门实例
    try:
        dept = await _create_company_department(
            db, company, body.department_id, body.parent_id, body.name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.add(dept)
    await db.flush()

    # 为部门创建Agent
    agents = await _create_company_agents(db, company, dept)
    await db.flush()

    # 如果有父部门，更新当前部门的parent_id
    if body.parent_id:
        stmt = select(CompanyDepartment).filter(
            CompanyDepartment.department_id == body.parent_id
        )
        parent = (await db.execute(stmt)).scalar_one_or_none()
        if parent and parent.company_id == company.company_id:
            dept.parent_id = body.parent_id

    await db.commit()
    await db.refresh(dept)

    log.info(f"Department subscribed: company={body.company_id}, dept={body.department_id}")

    return CompanyDepartmentOut(**dept.to_dict())


@router.get("/companies/{company_id}/departments", response_model=List[CompanyDepartmentOut])
async def list_company_departments(company_id: str, db: AsyncSession = Depends(get_db)):
    """获取公司的所有部门。"""
    stmt = select(CompanyDepartment).filter(
        and_(CompanyDepartment.company_id == company_id, CompanyDepartment.status == "active")
    )
    depts = (await db.execute(stmt)).scalars().all()
    return [CompanyDepartmentOut(**d.to_dict()) for d in depts]


# ── 部门Metadata API (必须在 /departments/{id} 之前) ──

@router.get("/departments/metadata")
async def list_department_metadata():
    """获取所有部门的Metadata定义。

    返回8个内置部门的完整路由规则和技能矩阵。
    """
    from ..engine.ceo_metadata import ceo_router

    departments = ceo_router.list_all_departments()
    return {
        "departments": departments,
        "total": len(departments),
    }


@router.get("/departments/metadata/{department_id}")
async def get_department_metadata_by_id(department_id: str):
    """获取指定部门的Metadata定义。"""
    from ..engine.ceo_metadata import ceo_router

    metadata = ceo_router.get_department_metadata(department_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Department metadata not found: {department_id}")

    return metadata


# ── 公司部门CRUD ──

@router.get("/departments/{department_id}", response_model=CompanyDepartmentOut)
async def get_company_department(department_id: str, db: AsyncSession = Depends(get_db)):
    """获取公司部门详情。"""
    stmt = select(CompanyDepartment).filter(CompanyDepartment.department_id == department_id)
    result = await db.execute(stmt)
    dept = result.scalar_one_or_none()

    if not dept:
        raise HTTPException(status_code=404, detail=f"Department not found: {department_id}")

    return CompanyDepartmentOut(**dept.to_dict())


@router.put("/departments/{department_id}", response_model=CompanyDepartmentOut)
async def update_company_department(
    department_id: str,
    body: CompanyDepartmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新公司部门。"""
    stmt = select(CompanyDepartment).filter(CompanyDepartment.department_id == department_id)
    result = await db.execute(stmt)
    dept = result.scalar_one_or_none()

    if not dept:
        raise HTTPException(status_code=404, detail=f"Department not found: {department_id}")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(dept, field, value)

    await db.commit()
    await db.refresh(dept)

    return CompanyDepartmentOut(**dept.to_dict())


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_department(department_id: str, db: AsyncSession = Depends(get_db)):
    """取消订阅部门 (软删除)。"""
    stmt = select(CompanyDepartment).filter(CompanyDepartment.department_id == department_id)
    result = await db.execute(stmt)
    dept = result.scalar_one_or_none()

    if not dept:
        raise HTTPException(status_code=404, detail=f"Department not found: {department_id}")

    dept.status = "inactive"

    # 同时停用该部门的所有Agent
    stmt = select(CompanyAgent).filter(
        and_(CompanyAgent.department_id == department_id, CompanyAgent.status == "active")
    )
    agents = (await db.execute(stmt)).scalars().all()
    for agent in agents:
        agent.status = "inactive"

    await db.commit()

# ── 公司Agent管理 ──


@router.post("/agents", status_code=status.HTTP_201_CREATED, response_model=CompanyAgentOut)
async def create_company_agent(body: CompanyAgentCreate, db: AsyncSession = Depends(get_db)):
    """为公司的部门分配Agent。

    从Agent市场选择Agent，分配到公司部门。
    """
    # 验证公司存在
    stmt = select(Company).filter(Company.company_id == body.company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {body.company_id}")

    # 验证部门存在
    stmt = select(CompanyDepartment).filter(
        and_(CompanyDepartment.department_id == body.department_id, CompanyDepartment.status == "active")
    )
    dept = (await db.execute(stmt)).scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department not found: {body.department_id}")

    # 获取Agent模板 (使用本地定义的模板)
    template = DEFAULT_AGENTS.get(body.agent_id, {})
    agent_instance_id = f"c{company.id[:8]}_{body.agent_id}"

    # 创建Agent实例
    agent = CompanyAgent(
        id=str(uuid.uuid4()),
        company_id=body.company_id,
        source_agent_id=body.agent_id,
        agent_id=agent_instance_id,
        name=body.name or template.get("name", body.agent_id),
        department_id=body.department_id,
        is_leader=False,
        role=body.role or template.get("role", ""),
        level=template.get("level", 3),
        skills=body.skills or template.get("skills", []),
        status="active",
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    log.info(f"Agent assigned: company={body.company_id}, agent={body.agent_id}, dept={body.department_id}")

    return CompanyAgentOut(**agent.to_dict())


@router.get("/companies/{company_id}/agents", response_model=List[CompanyAgentOut])
async def list_company_agents(
    company_id: str,
    department_id: Optional[str] = Query(None, description="按部门过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取公司的所有Agent。"""
    stmt = select(CompanyAgent).filter(
        and_(CompanyAgent.company_id == company_id, CompanyAgent.status == "active")
    )
    if department_id:
        stmt = stmt.filter(CompanyAgent.department_id == department_id)

    agents = (await db.execute(stmt)).scalars().all()
    return [CompanyAgentOut(**a.to_dict()) for a in agents]


@router.get("/agents/{agent_id}", response_model=CompanyAgentOut)
async def get_company_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """获取Agent详情。"""
    stmt = select(CompanyAgent).filter(CompanyAgent.agent_id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    return CompanyAgentOut(**agent.to_dict())


@router.put("/agents/{agent_id}", response_model=CompanyAgentOut)
async def update_company_agent(
    agent_id: str,
    body: CompanyAgentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新Agent信息。"""
    stmt = select(CompanyAgent).filter(CompanyAgent.agent_id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    update_data = body.model_dump(exclude_unset=True)

    # 如果设置is_leader，需要取消该部门其他Agent的leader身份
    if update_data.get("is_leader") is True:
        stmt = select(CompanyAgent).filter(
            and_(
                CompanyAgent.department_id == agent.department_id,
                CompanyAgent.is_leader == True,
                CompanyAgent.agent_id != agent_id,
            )
        )
        other_leaders = (await db.execute(stmt)).scalars().all()
        for other in other_leaders:
            other.is_leader = False

    for field, value in update_data.items():
        if value is not None:
            setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)

    return CompanyAgentOut(**agent.to_dict())


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """删除Agent (软删除)。"""
    stmt = select(CompanyAgent).filter(CompanyAgent.agent_id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    agent.status = "inactive"
    await db.commit()

# ── CEO执行链路 ──


@router.post("/execute/{company_id}", response_model=dict)
async def execute_task(
    company_id: str,
    body: ExecuteTaskRequest,
    db: AsyncSession = Depends(get_db),
):
    """CEO执行任务。

    任务流转链路:
    1. CEO接收任务 -> 创建Task记录
    2. CEO智能路由分析 -> 确定目标部门
    3. 下发给部门Leader (DepartmentOutput)
    4. 部门Leader分配给Agent执行
    5. 结果汇总 + 封驳审核 (如需要)

    Returns:
        任务执行结果和状态
    """
    from ..models import Task, TaskState, DepartmentOutput
    from ..engine.ceo_metadata import ceo_router

    # 验证公司存在
    stmt = select(Company).filter(Company.company_id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    # 获取公司已订阅的部门
    stmt = select(CompanyDepartment).filter(
        and_(CompanyDepartment.company_id == company_id, CompanyDepartment.status == "active")
    )
    depts = (await db.execute(stmt)).scalars().all()

    if not depts:
        raise HTTPException(status_code=400, detail="No active departments in company")

    # CEO智能路由
    target_department_id = body.target_department_id
    routing_result = None

    if not target_department_id:
        # 调用CEO路由引擎
        routing_result = ceo_router.route(body.task, body.context)

        # 从公司已订阅部门中找最佳匹配
        subscribed_dept_ids = {d.source_department_id for d in depts}

        if routing_result["target_department"] not in subscribed_dept_ids:
            # 如果最佳匹配部门未订阅，尝试备选部门
            for alt in routing_result.get("alternative_departments", []):
                if alt["department_id"] in subscribed_dept_ids:
                    routing_result["target_department"] = alt["department_id"]
                    routing_result["match_score"] = alt["score"]
                    break
            else:
                # 没有已订阅的匹配部门，默认第一个
                routing_result["target_department"] = depts[0].source_department_id

        target_department_id = routing_result["target_department"]

    # 找到目标公司部门实例
    target_dept = None
    for dept in depts:
        if dept.source_department_id == target_department_id:
            target_dept = dept
            break

    if not target_dept:
        raise HTTPException(status_code=404, detail=f"Department not found: {target_department_id}")

    # 获取部门Leader
    leader = None
    if target_dept.leader_agent_id:
        stmt = select(CompanyAgent).filter(CompanyAgent.agent_id == target_dept.leader_agent_id)
        leader = (await db.execute(stmt)).scalar_one_or_none()

    # 获取执行Agent
    stmt = select(CompanyAgent).filter(
        and_(
            CompanyAgent.department_id == target_dept.department_id,
            CompanyAgent.is_leader == False,
            CompanyAgent.status == "active",
        )
    )
    executors = (await db.execute(stmt)).scalars().all()

    # 获取部门Metadata用于生成执行指令
    dept_metadata = ceo_router.get_department_metadata(target_department_id)

    # 创建Task记录
    task_id = str(uuid.uuid4())
    new_task = Task(
        task_id=task_id,
        trace_id=str(uuid.uuid4()),
        title=body.task[:200] if len(body.task) > 200 else body.task,
        description="",
        user_input=body.task,
        state=TaskState.PENDING,
        priority=body.priority,
        assignee_org=company_id,
        creator=CEO_AGENT["agent_id"],
        meta={
            "company_id": company_id,
            "department_id": target_dept.department_id,
            "routing": routing_result,
        },
    )
    db.add(new_task)

    # 创建部门输出记录
    dept_output = DepartmentOutput(
        task_id=task_id,
        department=target_dept.department_id,
        output=body.task,
        status="pending",
    )
    db.add(dept_output)

    await db.commit()
    await db.refresh(new_task)

    return {
        "task_id": task_id,
        "company_id": company_id,
        "task": body.task,
        "priority": body.priority,
        "routing": routing_result or {
            "target_department": target_department_id,
            "match_score": None,
            "reasoning": "手动指定部门",
        },
        "target_department": {
            "department_id": target_dept.department_id,
            "source_id": target_dept.source_department_id,
            "name": target_dept.name,
            "responsibility": target_dept.responsibility or (dept_metadata.get("responsibility") if dept_metadata else ""),
        },
        "execution_path": {
            "ceo": CEO_AGENT["agent_id"],
            "department_leader": {
                "agent_id": leader.agent_id if leader else None,
                "name": leader.name if leader else None,
            } if leader else None,
            "executors": [{"agent_id": e.agent_id, "name": e.name} for e in executors],
        },
        "department_metadata": dept_metadata,
        "context": body.context or {},
        "status": "dispatched",
    }


@router.get("/ceo/status")
async def get_ceo_status(company_id: str, db: AsyncSession = Depends(get_db)):
    """获取CEO Agent状态。

    返回公司CEO的实时状态和关键指标。
    """
    # 验证公司存在
    stmt = select(Company).filter(Company.company_id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {company_id}")

    # 统计部门数、Agent数
    dept_count = (await db.execute(
        select(func.count()).select_from(CompanyDepartment).filter(
            and_(CompanyDepartment.company_id == company_id, CompanyDepartment.status == "active")
        )
    )).scalar()

    agent_count = (await db.execute(
        select(func.count()).select_from(CompanyAgent).filter(
            and_(CompanyAgent.company_id == company_id, CompanyAgent.status == "active")
        )
    )).scalar()

    return {
        "company_id": company_id,
        "ceo_agent_id": CEO_AGENT["agent_id"],
        "name": CEO_AGENT["name"],
        "role": CEO_AGENT["role"],
        "status": "active",
        "departments_count": dept_count,
        "agents_count": agent_count,
        "capabilities": CEO_AGENT["skills"],
    }


@router.post("/route/test", response_model=RouteTestResponse)
async def test_ceo_route(body: RouteTestRequest):
    """测试CEO智能路由。

    输入任务描述，返回CEO路由分析结果。
    不创建实际Task，仅用于验证路由效果。
    """
    from ..engine.ceo_metadata import ceo_router

    result = ceo_router.route(body.task, body.context)

    # 获取目标部门的metadata
    dept_metadata = ceo_router.get_department_metadata(result["target_department"])

    return RouteTestResponse(
        target_department=result["target_department"],
        match_score=result["match_score"],
        reasoning=result["reasoning"],
        alternative_departments=result.get("alternative_departments", []),
        department_metadata=dept_metadata,
    )


# ── 订阅管理 ──


@router.post("/subscriptions", status_code=status.HTTP_201_CREATED, response_model=SubscriptionOut)
async def create_subscription(body: SubscriptionCreate, db: AsyncSession = Depends(get_db)):
    """创建订阅记录。

    记录用户对部门/Agent/技能的订阅。
    """
    # 验证公司存在
    stmt = select(Company).filter(Company.company_id == body.company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found: {body.company_id}")

    # 检查是否已订阅
    stmt = select(Subscription).filter(
        and_(
            Subscription.company_id == body.company_id,
            Subscription.target_id == body.target_id,
            Subscription.subscription_type == body.subscription_type,
            Subscription.status == "active",
        )
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")

    # 创建订阅记录
    subscription = Subscription(
        id=str(uuid.uuid4()),
        user_id=body.user_id,
        company_id=body.company_id,
        subscription_type=body.subscription_type,
        target_id=body.target_id,
        tier=body.tier,
        price=body.price,
        status="active",
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    log.info(f"Subscription created: user={body.user_id}, type={body.subscription_type}, target={body.target_id}")

    return SubscriptionOut(**subscription.to_dict())


@router.get("/subscriptions")
async def list_subscriptions(
    company_id: str = Query(..., description="公司ID"),
    subscription_type: Optional[str] = Query(None, description="过滤类型"),
    db: AsyncSession = Depends(get_db),
):
    """获取公司的所有订阅记录。"""
    stmt = select(Subscription).filter(
        and_(Subscription.company_id == company_id, Subscription.status == "active")
    )
    if subscription_type:
        stmt = stmt.filter(Subscription.subscription_type == subscription_type)

    subs = (await db.execute(stmt)).scalars().all()
    return {"subscriptions": [SubscriptionOut(**s.to_dict()) for s in subs], "total": len(subs)}


@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_subscription(subscription_id: str, db: AsyncSession = Depends(get_db)):
    """取消订阅。"""
    stmt = select(Subscription).filter(Subscription.id == subscription_id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub.status = "cancelled"
    sub.cancelled_at = datetime.utcnow()
    await db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# 跨部门协作API
# ═══════════════════════════════════════════════════════════════════════════════


class CollaborationPlanRequest(BaseModel):
    """协作规划请求。"""
    task: str = Field(..., description="任务描述")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class CollaborationPlanResponse(BaseModel):
    """协作规划响应。"""
    task_id: str
    original_task: str
    status: str
    primary_department: str
    collaborating_departments: List[str]
    execution_chain: List[Dict[str, Any]]
    match_scores: Dict[str, float]


class HandoffExecuteRequest(BaseModel):
    """Handoff执行请求。"""
    handoff_id: str = Field(..., description="Handoff ID")
    result: Dict[str, Any] = Field(default_factory=dict, description="执行结果")


@router.post("/collaboration/plan", response_model=CollaborationPlanResponse)
async def plan_collaboration(request: CollaborationPlanRequest):
    """规划跨部门协作链路。

    智能识别需要多部门协作的任务，生成执行链路。
    """
    # 延迟导入避免循环依赖
    from ..engine.collaboration import collaboration_engine

    collab_task = collaboration_engine.plan_collaboration(request.task, request.context)

    return CollaborationPlanResponse(
        task_id=collab_task.task_id,
        original_task=collab_task.original_task,
        status=collab_task.status.value,
        primary_department=collab_task.primary_department,
        collaborating_departments=collab_task.collaborating_departments,
        execution_chain=[
            {
                "handoff_id": h.handoff_id,
                "from_department": h.from_department,
                "to_department": h.to_department,
                "status": h.status.value,
                "expected_output": h.context.get("expected_output", ""),
            }
            for h in collab_task.execution_chain
        ],
        match_scores=collab_task.match_scores,
    )


@router.post("/collaboration/handoff")
async def execute_handoff(request: HandoffExecuteRequest):
    """执行部门间Handoff。

    部门完成后调用此接口，将结果移交给下一部门。
    """
    from ..engine.collaboration import collaboration_engine

    handoff = collaboration_engine.execute_handoff(request.handoff_id, request.result)

    return {
        "handoff_id": handoff.handoff_id,
        "status": handoff.status.value,
        "from_department": handoff.from_department,
        "to_department": handoff.to_department,
        "message": f"结果已移交给{handoff.to_department}",
    }


@router.get("/collaboration/{task_id}/status")
async def get_collaboration_status(task_id: str):
    """获取协作任务状态。"""
    from ..engine.collaboration import collaboration_engine

    status_info = collaboration_engine.get_task_status(task_id)
    if not status_info:
        raise HTTPException(status_code=404, detail="Task not found")

    return status_info


@router.post("/collaboration/{task_id}/aggregate")
async def aggregate_collaboration_results(task_id: str):
    """汇总协作结果。

    所有部门执行完成后，调用此接口汇总结果。
    """
    from ..engine.collaboration import collaboration_engine

    try:
        result = collaboration_engine.aggregate_results(task_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/collaboration/{task_id}/result")
async def get_collaboration_result(task_id: str):
    """获取协作最终结果。"""
    from ..engine.collaboration import collaboration_engine

    task = collaboration_engine.active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.final_output:
        return {"status": "pending", "message": "Results not yet aggregated"}

    return task.final_output


@router.get("/collaboration/dashboard")
async def collaboration_dashboard():
    """协作链路仪表盘 - 查看所有活跃任务状态。"""
    from ..engine.collaboration import collaboration_engine, TaskStatus

    tasks = collaboration_engine.active_tasks

    # 按状态分组
    by_status = {status.value: [] for status in TaskStatus}
    for task in tasks.values():
        by_status[task.status.value].append({
            "task_id": task.task_id,
            "original_task": task.original_task,
            "primary_department": task.primary_department,
            "departments_count": len(task.execution_chain) if task.execution_chain else 1,
            "created_at": task.created_at.isoformat(),
        })

    # 统计
    total = len(tasks)
    completed = len([t for t in tasks.values() if t.status == TaskStatus.COMPLETED])
    in_progress = len([t for t in tasks.values() if t.status == TaskStatus.COLLABORATING])

    return {
        "total_tasks": total,
        "completed": completed,
        "in_progress": in_progress,
        "by_status": {k: v for k, v in by_status.items() if v},
    }


@router.post("/collaboration/execute")
async def execute_collaboration(request: CollaborationPlanRequest):
    """一键执行协作链路 - 规划+执行+汇总。"""
    from ..engine.collaboration import collaboration_engine

    result = collaboration_engine.execute_full_collaboration(request.task, request.context)

    return {
        "task_id": result["task_id"],
        "status": "completed",
        "primary_department": result["primary_department"],
        "collaboration_summary": result["collaboration_summary"],
        "final_recommendation": result["final_recommendation"],
        "departments_participated": result["collaboration_summary"]["departments_involved"],
    }
