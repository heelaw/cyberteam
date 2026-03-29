"""部门管理 API v1 - 动态部门 Metadata 配置。

API 路由：
- GET /api/v1/departments - 列出所有部门
- GET /api/v1/departments/{id} - 获取部门详情
- POST /api/v1/departments - 注册新部门
- PUT /api/v1/departments/{id} - 更新部门
- DELETE /api/v1/departments/{id} - 删除自定义部门
- GET /api/v1/departments/statistics - 获取部门统计
- POST /api/v1/departments/export - 导出部门配置
- POST /api/v1/departments/import - 导入部门配置
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...engine.department_registry import (
    get_department_registry,
    DepartmentRegistry,
    BUILTIN_DEPARTMENT_IDS,
)

router = APIRouter(prefix="/departments", tags=["departments v1"])


# === Request/Response Models ===

class RegisterDepartmentRequest(BaseModel):
    """注册新部门请求。"""
    department_id: str = Field(..., description="部门唯一标识（英文）")
    name: str = Field(..., description="部门中文名称")
    description: str = Field(..., description="部门描述")
    responsibility: str = Field(..., description="核心职责")
    skills: List[dict] = Field(default_factory=list, description="技能列表")
    routing_rules: List[dict] = Field(default_factory=list, description="路由规则")
    leader_role: str = Field(default="部门负责人", description="Leader角色")
    leader_skills: List[str] = Field(default_factory=list, description="Leader技能")
    executor_role: str = Field(default="部门专家", description="执行器角色")
    executor_skills: List[str] = Field(default_factory=list, description="执行器技能")
    parent_id: Optional[str] = Field(default=None, description="上级部门")
    price_tier: str = Field(default="免费", description="价格层级")
    tags: List[str] = Field(default_factory=list, description="标签")


class UpdateDepartmentRequest(BaseModel):
    """更新部门请求。"""
    name: Optional[str] = None
    description: Optional[str] = None
    responsibility: Optional[str] = None
    skills: Optional[List[dict]] = None
    routing_rules: Optional[List[dict]] = None
    leader_role: Optional[str] = None
    leader_skills: Optional[List[str]] = None
    executor_role: Optional[str] = None
    executor_skills: Optional[List[str]] = None
    parent_id: Optional[str] = None
    price_tier: Optional[str] = None
    tags: Optional[List[str]] = None


class DepartmentResponse(BaseModel):
    """部门响应。"""
    department_id: str
    name: str
    description: str
    responsibility: str
    skills: List[dict]
    routing_rules: List[dict]
    leader: dict
    executor: dict
    parent_id: Optional[str]
    price_tier: str
    tags: List[str]
    is_builtin: bool


class StatisticsResponse(BaseModel):
    """统计信息响应。"""
    total_count: int
    builtin_count: int
    custom_count: int
    builtin_departments: List[str]
    custom_departments: List[str]


class ExportImportRequest(BaseModel):
    """导入配置请求。"""
    config: dict


# === Routes ===

@router.get("", response_model=List[DepartmentResponse])
async def list_departments(
    include_builtin: bool = True,
    include_custom: bool = True,
):
    """列出所有部门。"""
    registry = get_department_registry()
    departments = registry.list_departments(
        include_builtin=include_builtin,
        include_custom=include_custom,
    )

    return [
        {**dept.to_dict(), "is_builtin": registry.is_builtin(dept.department_id)}
        for dept in departments
    ]


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """获取部门统计信息。"""
    registry = get_department_registry()
    stats = registry.get_statistics()
    return StatisticsResponse(**stats)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: str):
    """获取部门详情。"""
    registry = get_department_registry()
    dept = registry.get_department(department_id)

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部门 {department_id} 不存在",
        )

    return {
        **dept.to_dict(),
        "is_builtin": registry.is_builtin(department_id),
    }


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def register_department(request: RegisterDepartmentRequest):
    """注册新部门。"""
    registry = get_department_registry()

    try:
        dept = registry.register_department(
            department_id=request.department_id,
            name=request.name,
            description=request.description,
            responsibility=request.responsibility,
            skills=request.skills,
            routing_rules=request.routing_rules,
            leader_role=request.leader_role,
            leader_skills=request.leader_skills,
            executor_role=request.executor_role,
            executor_skills=request.executor_skills,
            parent_id=request.parent_id,
            price_tier=request.price_tier,
            tags=request.tags,
        )
        return {
            **dept.to_dict(),
            "is_builtin": False,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    request: UpdateDepartmentRequest,
):
    """更新部门。"""
    registry = get_department_registry()

    # 检查是否为内置部门（内置部门只能更新部分字段）
    if department_id in BUILTIN_DEPARTMENT_IDS:
        # 内置部门只允许更新部分元数据
        allowed_updates = {
            "leader_role": request.leader_role,
            "leader_skills": request.leader_skills,
            "executor_role": request.executor_role,
            "executor_skills": request.executor_skills,
        }
        filtered_updates = {k: v for k, v in allowed_updates.items() if v is not None}
    else:
        # 自定义部门可以更新所有字段
        filtered_updates = {
            "name": request.name,
            "description": request.description,
            "responsibility": request.responsibility,
            "skills": request.skills,
            "routing_rules": request.routing_rules,
            "leader_role": request.leader_role,
            "leader_skills": request.leader_skills,
            "executor_role": request.executor_role,
            "executor_skills": request.executor_skills,
            "parent_id": request.parent_id,
            "price_tier": request.price_tier,
            "tags": request.tags,
        }
        filtered_updates = {k: v for k, v in filtered_updates.items() if v is not None}

    dept = registry.update_department(department_id, **filtered_updates)

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部门 {department_id} 不存在",
        )

    return {
        **dept.to_dict(),
        "is_builtin": registry.is_builtin(department_id),
    }


@router.delete("/{department_id}")
async def delete_department(department_id: str):
    """删除自定义部门。"""
    registry = get_department_registry()

    if department_id in BUILTIN_DEPARTMENT_IDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"内置部门 {department_id} 无法删除",
        )

    success = registry.unregister_department(department_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部门 {department_id} 不存在",
        )

    return {"status": "ok", "department_id": department_id}


@router.post("/export")
async def export_departments():
    """导出部门配置。"""
    registry = get_department_registry()
    config = registry.export_config()
    return {"status": "ok", "config": config}


@router.post("/import")
async def import_departments(request: ExportImportRequest):
    """导入部门配置。"""
    registry = get_department_registry()
    imported = registry.import_config(request.config)
    return {"status": "ok", "imported_count": imported}
