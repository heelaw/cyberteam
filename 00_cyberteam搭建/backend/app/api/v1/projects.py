"""Projects API endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.db.models import Project, BudgetTracking

router = APIRouter()


class ProjectCreateRequest(BaseModel):
    """Request to create a project."""
    name: str
    description: Optional[str] = None
    metadata: Optional[dict] = None


class ProjectResponse(BaseModel):
    """Project response."""
    id: str
    name: str
    description: Optional[str]
    status: str
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime


class BudgetRequest(BaseModel):
    """Budget tracking request."""
    budget_type: str  # daily/monthly/project
    budget_amount: float
    currency: str = "CNY"
    period_start: datetime
    period_end: datetime
    department: Optional[str] = None


class BudgetResponse(BaseModel):
    """Budget tracking response."""
    id: str
    user_id: str
    budget_type: str
    budget_amount: float
    spent_amount: float
    currency: str
    period_start: datetime
    period_end: datetime


@router.post("", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectResponse:
    """Create a new project."""
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        name=request.name,
        description=request.description,
        user_id=current_user.get("sub", "anonymous"),
        metadata=request.metadata,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        metadata=project.metadata,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("")
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[ProjectResponse]:
    """List user's projects."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(Project).where(Project.user_id == user_id)

    if status:
        stmt = stmt.where(Project.status == status)

    stmt = stmt.order_by(Project.updated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    projects = result.scalars().all()

    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            status=p.status,
            metadata=p.metadata,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProjectResponse:
    """Get project details."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == user_id,
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        metadata=project.metadata,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Delete a project."""
    user_id = current_user.get("sub", "anonymous")
    stmt = select(Project).where(
        Project.id == project_id,
        Project.user_id == user_id,
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()

    return {"status": "deleted", "id": project_id}


# Budget endpoints
@router.post("/budget", response_model=BudgetResponse)
async def create_budget(
    request: BudgetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> BudgetResponse:
    """Create a budget tracking record."""
    budget_id = str(uuid.uuid4())
    budget = BudgetTracking(
        id=budget_id,
        user_id=current_user.get("sub", "anonymous"),
        project_id=request.department,  # Using department as project_id
        department=request.department,
        budget_type=request.budget_type,
        budget_amount=request.budget_amount,
        currency=request.currency,
        period_start=request.period_start,
        period_end=request.period_end,
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)

    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        budget_type=budget.budget_type,
        budget_amount=budget.budget_amount,
        spent_amount=budget.spent_amount,
        currency=budget.currency,
        period_start=budget.period_start,
        period_end=budget.period_end,
    )


@router.get("/budget")
async def list_budgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[BudgetResponse]:
    """List user's budget tracking records."""
    user_id = current_user.get("sub", "anonymous")
    stmt = (
        select(BudgetTracking)
        .where(BudgetTracking.user_id == user_id)
        .order_by(BudgetTracking.period_start.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    budgets = result.scalars().all()

    return [
        BudgetResponse(
            id=b.id,
            user_id=b.user_id,
            budget_type=b.budget_type,
            budget_amount=b.budget_amount,
            spent_amount=b.spent_amount,
            currency=b.currency,
            period_start=b.period_start,
            period_end=b.period_end,
        )
        for b in budgets
    ]
