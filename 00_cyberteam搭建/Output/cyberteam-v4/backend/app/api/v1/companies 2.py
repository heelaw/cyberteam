"""公司管理 API v1。

API 路由：
- POST /api/v1/companies - 创建公司
- GET /api/v1/companies - 列出所有公司（支持分页、搜索）
- GET /api/v1/companies/{company_id} - 获取公司详情
- PUT /api/v1/companies/{company_id} - 更新公司
- DELETE /api/v1/companies/{company_id} - 删除公司（软删除）
- GET /api/v1/companies/{company_id}/departments - 获取公司部门列表
- GET /api/v1/companies/{company_id}/agents - 获取公司Agent列表
- GET /api/v1/companies/{company_id}/stats - 获取公司统计数据
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# 导入审计日志
from .audit import record_audit

# 导入 departments 模块的辅助函数和绑定存储
from . import departments as dept_module

# 导入 agents 模块的 store
from .agents import get_agent_store

router = APIRouter(prefix="/companies", tags=["companies v1"])


# === 内存存储（模拟数据库） ===
_companies: dict[str, dict] = {}
_departments_by_company: dict[str, list] = {}
_agents_by_company: dict[str, list] = {}

# Agent-Skill 绑定记录（用于级联清理）
_agent_skill_records: dict[str, list] = {}  # agent_code -> list of skill_ids


# === Request/Response Models ===

class CompanyCreate(BaseModel):
    """创建公司请求。"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = "active"
    config: Optional[dict] = {}


class CompanyUpdate(BaseModel):
    """更新公司请求。"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    config: Optional[dict] = None


class CompanyOut(BaseModel):
    """公司响应。"""
    id: str
    name: str
    description: Optional[str]
    status: str
    config: dict
    created_at: datetime
    updated_at: datetime
    department_count: int = 0
    agent_count: int = 0


class CompanyStats(BaseModel):
    """公司统计信息。"""
    company_id: str
    department_count: int
    agent_count: int
    active_department_count: int
    active_agent_count: int


class DepartmentSummary(BaseModel):
    """部门摘要。"""
    id: str
    name: str
    code: str
    description: Optional[str]
    is_active: bool


class AgentSummary(BaseModel):
    """Agent摘要。"""
    id: str
    name: str
    agent_type: str
    status: str
    description: Optional[str]


class PaginatedCompanyResponse(BaseModel):
    """分页公司响应。"""
    items: List[CompanyOut]
    total: int
    skip: int
    limit: int


# === Routes ===

@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED,
            summary="创建公司", tags=["companies"])
async def create_company(request: CompanyCreate):
    """创建新公司。

    - **name**: 公司名称（必填，最大200字符）
    - **description**: 公司描述（可选）
    - **status**: 状态，默认为 active
    - **config**: 公司配置（可选，JSON对象）
    """
    company_id = str(uuid.uuid4())
    now = datetime.utcnow()

    company = {
        "id": company_id,
        "name": request.name,
        "description": request.description,
        "status": request.status,
        "config": request.config or {},
        "created_at": now,
        "updated_at": now,
    }

    _companies[company_id] = company
    _departments_by_company[company_id] = []
    _agents_by_company[company_id] = []

    return CompanyOut(
        **company,
        department_count=0,
        agent_count=0,
    )


@router.get("", response_model=PaginatedCompanyResponse,
           summary="列出公司", tags=["companies"])
async def list_companies(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    q: Optional[str] = Query(None, description="搜索公司名称"),
):
    """列出所有公司（支持分页和搜索）。

    - **skip**: 跳过记录数（默认0）
    - **limit**: 返回记录数（默认50，最大100）
    - **q**: 按公司名称搜索（可选，模糊匹配）
    """
    # 过滤已删除的公司
    filtered = [c for c in _companies.values() if c.get("status") != "deleted"]

    # 名称搜索
    if q:
        q_lower = q.lower()
        filtered = [c for c in filtered if q_lower in c["name"].lower()]

    # 统计
    total = len(filtered)

    # 分页
    items = filtered[skip:skip + limit]

    return PaginatedCompanyResponse(
        items=[
            CompanyOut(
                id=c["id"],
                name=c["name"],
                description=c["description"],
                status=c["status"],
                config=c["config"],
                created_at=c["created_at"],
                updated_at=c["updated_at"],
                department_count=len(_departments_by_company.get(c["id"], [])),
                agent_count=len(_agents_by_company.get(c["id"], [])),
            )
            for c in items
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/stats", summary="全局统计", tags=["companies"])
async def get_global_stats():
    """获取全局公司统计数据。

    返回所有公司的统计信息，包括总数、活跃数、已删除数。
    """
    active = [c for c in _companies.values() if c.get("status") == "active"]
    return {
        "total_companies": len(_companies),
        "active_companies": len(active),
        "deleted_companies": sum(1 for c in _companies.values() if c.get("status") == "deleted"),
    }


@router.get("/{company_id}", response_model=CompanyOut,
            summary="获取公司详情", tags=["companies"])
async def get_company(company_id: str):
    """获取公司详情。

    - **company_id**: 公司ID（路径参数）
    """
    company = _companies.get(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 不存在",
        )

    if company.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 已删除",
        )

    return CompanyOut(
        **company,
        department_count=len(_departments_by_company.get(company_id, [])),
        agent_count=len(_agents_by_company.get(company_id, [])),
    )


@router.put("/{company_id}", response_model=CompanyOut,
           summary="更新公司", tags=["companies"])
async def update_company(company_id: str, request: CompanyUpdate):
    """更新公司信息。

    - **company_id**: 公司ID（路径参数）
    - **name**: 公司名称（可选）
    - **description**: 公司描述（可选）
    - **status**: 状态（可选）
    - **config**: 公司配置（可选）
    """
    company = _companies.get(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 不存在",
        )

    if company.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"公司 {company_id} 已删除，无法更新",
        )

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            company[field] = value

    company["updated_at"] = datetime.utcnow()
    _companies[company_id] = company

    return CompanyOut(
        **company,
        department_count=len(_departments_by_company.get(company_id, [])),
        agent_count=len(_agents_by_company.get(company_id, [])),
    )


@router.delete("/{company_id}", summary="删除公司", tags=["companies"])
async def delete_company(company_id: str):
    """删除公司（软删除 + 级联清理关联数据）。

    级联清理内容：
    - 软删除公司本身
    - 清理公司下的部门-Agent绑定
    - 软删除公司下的Agent
    - 清理Agent-Skill绑定记录

    - **company_id**: 公司ID（路径参数）
    """
    company = _companies.get(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 不存在",
        )

    if company.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"公司 {company_id} 已删除",
        )

    # 记录审计日志
    record_audit(
        company_id=company_id,
        action="DELETE",
        resource_type="company",
        resource_id=company_id,
        resource_name=company.get("name"),
    )

    # 软删除公司
    company["status"] = "deleted"
    company["updated_at"] = datetime.utcnow()
    _companies[company_id] = company

    # 级联清理：删除公司下的部门
    depts = _departments_by_company.get(company_id, [])
    dept_ids = [d.get("id") or d.get("department_id") for d in depts if d.get("id") or d.get("department_id")]
    if dept_ids:
        # 清理部门-Agent绑定
        dept_module.clear_department_agents_by_department_ids(dept_ids)

    # 级联清理：软删除公司下的Agent
    agent_store = get_agent_store()
    agents = _agents_by_company.get(company_id, [])
    for agent in agents:
        agent_code = agent.get("code") or agent.get("agent_code")
        if agent_code:
            agent_store.delete_agent(agent_code)
            # 清理Agent-Skill绑定
            if agent_code in _agent_skill_records:
                del _agent_skill_records[agent_code]

    return {"company_id": company_id, "status": "deleted", "cascaded": True}


@router.get("/{company_id}/departments", response_model=List[DepartmentSummary],
            summary="获取公司部门列表", tags=["companies"])
async def get_company_departments(company_id: str):
    """获取公司部门列表。

    - **company_id**: 公司ID（路径参数）
    """
    company = _companies.get(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 不存在",
        )

    if company.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"公司 {company_id} 已删除",
        )

    departments = _departments_by_company.get(company_id, [])
    return [
        DepartmentSummary(
            id=d["id"],
            name=d["name"],
            code=d["code"],
            description=d.get("description"),
            is_active=d.get("is_active", True),
        )
        for d in departments
    ]


@router.get("/{company_id}/agents", response_model=List[AgentSummary],
            summary="获取公司Agent列表", tags=["companies"])
async def get_company_agents(company_id: str):
    """获取公司Agent列表。

    - **company_id**: 公司ID（路径参数）
    """
    company = _companies.get(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 不存在",
        )

    if company.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"公司 {company_id} 已删除",
        )

    agents = _agents_by_company.get(company_id, [])
    return [
        AgentSummary(
            id=a["id"],
            name=a["name"],
            agent_type=a["agent_type"],
            status=a["status"],
            description=a.get("description"),
        )
        for a in agents
    ]


@router.get("/{company_id}/stats", response_model=CompanyStats,
           summary="获取公司统计", tags=["companies"])
async def get_company_stats(company_id: str):
    """获取公司统计数据。

    - **company_id**: 公司ID（路径参数）
    """
    company = _companies.get(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"公司 {company_id} 不存在",
        )

    if company.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"公司 {company_id} 已删除",
        )

    departments = _departments_by_company.get(company_id, [])
    agents = _agents_by_company.get(company_id, [])

    return CompanyStats(
        company_id=company_id,
        department_count=len(departments),
        agent_count=len(agents),
        active_department_count=sum(1 for d in departments if d.get("is_active", True)),
        active_agent_count=sum(1 for a in agents if a.get("status") == "active"),
    )


# === 辅助函数（用于测试） ===

def clear_all_data():
    """清除所有内存数据（仅用于测试）。"""
    global _companies, _departments_by_company, _agents_by_company
    _companies.clear()
    _departments_by_company.clear()
    _agents_by_company.clear()


def add_department_to_company(company_id: str, department: dict):
    """添加部门到公司（仅用于测试或初始化）。"""
    if company_id not in _departments_by_company:
        _departments_by_company[company_id] = []
    _departments_by_company[company_id].append(department)


def add_agent_to_company(company_id: str, agent: dict):
    """添加Agent到公司（仅用于测试或初始化）。"""
    if company_id not in _agents_by_company:
        _agents_by_company[company_id] = []
    _agents_by_company[company_id].append(agent)
