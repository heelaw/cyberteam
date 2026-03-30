"""Market API — 部门市场（Department Market）。

提供 RESTful API 用于浏览、选择和订阅部门服务。
参考 Magic 的"数字员工市场"，实现部门的展示和选择功能。
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..db import get_db
from ..db.models import Department  # Department from legacy db models
from ..models import ExpertOutput, DepartmentOutput

log = logging.getLogger("cyberteam.api.market")
router = APIRouter()

_backend_path = Path(__file__).parent.parent.parent
for p in [str(_backend_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── 默认部门定义 ──
DEFAULT_DEPARTMENTS = {
    "ceo": {"department_id": "ceo", "name": "CEO",
        "description": "首席执行官，负责整体战略和决策",
        "responsibility": "战略决策", "parent_id": None,
        "skills": ["战略规划", "决策制定", "资源分配", "风险管理"],
        "capability_tags": ["战略决策", "顶层设计", "资源协调"],
        "price_tier": "基础"},
    "product": {"department_id": "product", "name": "产品部",
        "description": "需求分析、产品设计、功能规划",
        "responsibility": "产品规划与设计", "parent_id": "ceo",
        "skills": ["需求分析", "产品规划", "原型设计", "用户研究"],
        "capability_tags": ["产品设计", "需求分析", "用户研究", "原型制作"],
        "price_tier": "基础"},
    "engineering": {"department_id": "engineering", "name": "技术部",
        "description": "技术方案、架构设计，开发实现",
        "responsibility": "技术实现", "parent_id": "ceo",
        "skills": ["系统架构", "后端开发", "前端开发", "测试"],
        "capability_tags": ["后端开发", "前端开发", "架构设计", "DevOps"],
        "price_tier": "专业"},
    "design": {"department_id": "design", "name": "设计部",
        "description": "UI设计、用户体验，品牌视觉",
        "responsibility": "设计创作", "parent_id": "ceo",
        "skills": ["UI设计", "UX设计", "品牌设计", "视觉设计"],
        "capability_tags": ["UI设计", "UX设计", "品牌视觉", "动效设计"],
        "price_tier": "基础"},
    "operations": {"department_id": "operations", "name": "运营部",
        "description": "用户增长、内容运营、活动策划",
        "responsibility": "运营策略", "parent_id": "ceo",
        "skills": ["用户运营", "内容运营", "活动策划", "数据分析"],
        "capability_tags": ["用户增长", "内容运营", "活动策划", "数据分析"],
        "price_tier": "免费"},
    "marketing": {"department_id": "marketing", "name": "市场部",
        "description": "市场营销，品牌推广、渠道拓展",
        "responsibility": "市场拓展", "parent_id": "ceo",
        "skills": ["品牌营销", "效果营销", "内容营销", "渠道推广"],
        "capability_tags": ["品牌营销", "效果广告", "内容营销", "渠道拓展"],
        "price_tier": "基础"},
    "finance": {"department_id": "finance", "name": "财务部",
        "description": "预算规划，成本控制，投资分析",
        "responsibility": "财务规划", "parent_id": "ceo",
        "skills": ["预算管理", "成本控制", "财务分析", "投资决策"],
        "capability_tags": ["预算管理", "成本分析", "投资评估", "风险控制"],
        "price_tier": "专业"},
    "hr": {"department_id": "hr", "name": "人力部",
        "description": "招聘方案、团队激励，文化建设",
        "responsibility": "人力资源", "parent_id": "ceo",
        "skills": ["招聘", "培训", "绩效管理", "团队建设"],
        "capability_tags": ["招聘猎才", "培训发展", "绩效考核", "文化建设"],
        "price_tier": "免费"},
}

# ── 市场订阅记录（内存存储，生产环境应持久化）──
_market_subscriptions: dict = {}

# ── Schemas ──


class MarketDepartment(BaseModel):
    """市场部门视图（MarketDepartment）。"""
    department_id: str
    name: str
    description: str
    capability_tags: List[str] = []
    avg_rating: float = 0.0
    total_tasks: int = 0
    price_tier: str = "免费"
    is_active: bool = True
    skills: List[str] = []
    parent_id: Optional[str] = None


class MarketDepartmentDetail(MarketDepartment):
    """市场部门详情视图。"""
    responsibility: str = ""
    expert_count: int = 0
    completed_task_rate: float = 0.0
    recent_tasks: List[dict] = []


class MarketDepartmentList(BaseModel):
    departments: List[MarketDepartment]
    total: int
    categories: List[str] = []


class SubscribeRequest(BaseModel):
    user_id: str
    tier: Optional[str] = "免费"


class SubscribeResponse(BaseModel):
    department_id: str
    user_id: str
    tier: str
    subscribed_at: str
    message: str


# ── 辅助函数 ──


async def _get_department_stats(db: AsyncSession, department_id: str) -> tuple:
    """获取部门的统计数据：(avg_rating, total_tasks, expert_count)。"""
    # 评分：ExpertOutput.completeness (0-10) 映射到 rating (0-5)
    stmt = select(func.avg(ExpertOutput.completeness)).filter(
        ExpertOutput.expert_id == department_id)
    raw = (await db.execute(stmt)).scalar_one_or_none()
    avg_rating = round((raw or 0) / 2, 2)

    # 完成任务数
    stmt2 = select(func.count(DepartmentOutput.id)).filter(
        and_(DepartmentOutput.department == department_id,
             DepartmentOutput.status == "completed"))
    total_tasks = (await db.execute(stmt2)).scalar_one_or_none() or 0

    # 专家数量：使用 ExpertOutput 中该部门的唯一 expert_id 数量估算
    stmt3 = select(func.count(func.distinct(ExpertOutput.expert_id))).filter(
        ExpertOutput.expert_id == department_id)
    expert_count = (await db.execute(stmt3)).scalar_one_or_none() or 0

    return avg_rating, total_tasks, expert_count


async def _build_market_dept(
    dept_id: str,
    db: AsyncSession,
    default_info: Optional[dict] = None,
    db_dept: Optional[Department] = None,
) -> MarketDepartment:
    avg_rating, total_tasks, _ = await _get_department_stats(db, dept_id)
    if default_info:
        return MarketDepartment(
            department_id=default_info["department_id"],
            name=default_info["name"],
            description=default_info["description"],
            capability_tags=default_info.get("capability_tags", []),
            avg_rating=avg_rating,
            total_tasks=total_tasks,
            price_tier=default_info.get("price_tier", "免费"),
            is_active=True,
            skills=default_info.get("skills", []),
            parent_id=default_info.get("parent_id"),
        )
    elif db_dept:
        skills = db_dept.skills if isinstance(db_dept.skills, list) else []
        return MarketDepartment(
            department_id=db_dept.department_id,
            name=db_dept.name,
            description=db_dept.description,
            capability_tags=skills,
            avg_rating=avg_rating,
            total_tasks=total_tasks,
            price_tier="免费",
            is_active=db_dept.status == "active",
            skills=skills,
            parent_id=db_dept.parent_id,
        )
    raise ValueError(f"No data for department: {dept_id}")


# ── Endpoints ──


@router.get("/departments", response_model=MarketDepartmentList)
async def list_market_departments(
    price_tier: Optional[str] = Query(None),
    capability: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("name"),
    db: AsyncSession = Depends(get_db),
):
    """获取所有可用部门（市场视图）。"""
    market_depts: List[MarketDepartment] = []

    for dept_id, info in DEFAULT_DEPARTMENTS.items():
        if price_tier and info.get("price_tier") != price_tier:
            continue
        if capability and capability not in info.get("capability_tags", []):
            continue
        market_depts.append(await _build_market_dept(dept_id, db, default_info=info))

    stmt = select(Department).filter(Department.status == "active")
    for db_dept in (await db.execute(stmt)).scalars().all():
        if db_dept.department_id in DEFAULT_DEPARTMENTS:
            continue
        market_depts.append(await _build_market_dept(db_dept.department_id, db, db_dept=db_dept))

    if sort_by == "rating":
        market_depts.sort(key=lambda d: d.avg_rating, reverse=True)
    elif sort_by == "tasks":
        market_depts.sort(key=lambda d: d.total_tasks, reverse=True)
    else:
        market_depts.sort(key=lambda d: d.name)

    return MarketDepartmentList(
        departments=market_depts,
        total=len(market_depts),
        categories=sorted({d.price_tier for d in market_depts}),
    )


@router.get("/departments/{dept_id}", response_model=MarketDepartmentDetail)
async def get_department_detail(dept_id: str, db: AsyncSession = Depends(get_db)):
    """获取部门详细信息（包含技能、价格、评分等）。"""
    if dept_id in DEFAULT_DEPARTMENTS:
        info = DEFAULT_DEPARTMENTS[dept_id]
        avg_rating, total_tasks, expert_count = await _get_department_stats(db, dept_id)

        stmt = select(DepartmentOutput).filter(
            DepartmentOutput.department == dept_id
        ).order_by(DepartmentOutput.created_at.desc()).limit(5)
        recent = (await db.execute(stmt)).scalars().all()

        total_count = (await db.execute(
            select(func.count(DepartmentOutput.id)).filter(
                DepartmentOutput.department == dept_id)
        )).scalar_one_or_none() or 0

        return MarketDepartmentDetail(
            department_id=info["department_id"],
            name=info["name"],
            description=info["description"],
            capability_tags=info.get("capability_tags", []),
            avg_rating=avg_rating,
            total_tasks=total_tasks,
            price_tier=info.get("price_tier", "免费"),
            is_active=True,
            skills=info.get("skills", []),
            parent_id=info.get("parent_id"),
            responsibility=info.get("responsibility", ""),
            expert_count=expert_count,
            completed_task_rate=round(total_tasks / total_count, 2) if total_count > 0 else 0.0,
            recent_tasks=[{"task_id": t.task_id, "status": t.status,
                           "created_at": t.created_at.isoformat() if t.created_at else None}
                          for t in recent],
        )

    stmt = select(Department).filter(
        (Department.id == dept_id) | (Department.department_id == dept_id))
    db_dept = (await db.execute(stmt)).scalar_one_or_none()
    if not db_dept:
        raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")

    avg_rating, total_tasks, expert_count = await _get_department_stats(db, dept_id)
    recent = (await db.execute(
        select(DepartmentOutput).filter(DepartmentOutput.department == db_dept.department_id)
        .order_by(DepartmentOutput.created_at.desc()).limit(5)
    )).scalars().all()
    total_count = (await db.execute(
        select(func.count(DepartmentOutput.id)).filter(
            DepartmentOutput.department == db_dept.department_id)
    )).scalar_one_or_none() or 0
    skills = db_dept.skills if isinstance(db_dept.skills, list) else []

    return MarketDepartmentDetail(
        department_id=db_dept.department_id,
        name=db_dept.name,
        description=db_dept.description,
        capability_tags=skills,
        avg_rating=avg_rating,
        total_tasks=total_tasks,
        price_tier="免费",
        is_active=db_dept.status == "active",
        skills=skills,
        parent_id=db_dept.parent_id,
        responsibility=db_dept.responsibility,
        expert_count=expert_count,
        completed_task_rate=round(total_tasks / total_count, 2) if total_count > 0 else 0.0,
        recent_tasks=[{"task_id": t.task_id, "status": t.status,
                       "created_at": t.created_at.isoformat() if t.created_at else None}
                      for t in recent],
    )


@router.post("/departments/{dept_id}/subscribe",
              response_model=SubscribeResponse, status_code=201)
async def subscribe_department(
    dept_id: str,
    body: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
):
    """订阅部门。"""
    if dept_id not in DEFAULT_DEPARTMENTS:
        db_dept = (await db.execute(
            select(Department).filter(
                (Department.id == dept_id) | (Department.department_id == dept_id))
        )).scalar_one_or_none()
        if not db_dept:
            raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")
        price_tier = "免费"
    else:
        price_tier = DEFAULT_DEPARTMENTS[dept_id].get("price_tier", "免费")

    tier = body.tier or price_tier
    subscribed_at = datetime.utcnow().isoformat()
    _market_subscriptions.setdefault(dept_id, {})[body.user_id] = {
        "subscribed_at": subscribed_at, "tier": tier}

    dept_name = DEFAULT_DEPARTMENTS.get(dept_id, {}).get("name", dept_id)
    return SubscribeResponse(
        department_id=dept_id,
        user_id=body.user_id,
        tier=tier,
        subscribed_at=subscribed_at,
        message=f"成功订阅 {dept_name}，等级：{tier}",
    )


@router.get("/subscriptions")
async def list_user_subscriptions(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    """获取用户的所有部门订阅记录。"""
    subs = []
    for dept_id, users in _market_subscriptions.items():
        if user_id in users:
            info = users[user_id]
            name = DEFAULT_DEPARTMENTS.get(dept_id, {}).get("name", dept_id)
            if name == dept_id:
                db_dept = (await db.execute(
                    select(Department).filter(
                        (Department.id == dept_id) | (Department.department_id == dept_id))
                )).scalar_one_or_none()
                name = db_dept.name if db_dept else dept_id
            subs.append({"department_id": dept_id, "name": name,
                         "tier": info["tier"], "subscribed_at": info["subscribed_at"]})
    return {"user_id": user_id, "subscriptions": subs, "total": len(subs)}


@router.delete("/subscriptions/{dept_id}")
async def unsubscribe_department(dept_id: str, user_id: str = Query(...)):
    """取消订阅部门。"""
    if dept_id in _market_subscriptions and user_id in _market_subscriptions[dept_id]:
        del _market_subscriptions[dept_id][user_id]
        return {"message": f"成功取消订阅部门 {dept_id}"}
    raise HTTPException(status_code=404,
                        detail=f"Subscription not found: user={user_id}, department={dept_id}")
