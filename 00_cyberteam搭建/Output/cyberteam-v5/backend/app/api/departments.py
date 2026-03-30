"""
部门管理 API

提供部门的 CRUD 接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.department import Department, DepartmentRegistry

router = APIRouter(prefix="/api/departments", tags=["departments"])

# 全局部门注册表
registry = DepartmentRegistry()


# === Request/Response Models ===

class CreateDepartmentRequest(BaseModel):
    """创建部门请求"""
    name: str
    code: str
    level: int = 1
    parent_id: Optional[str] = None
    description: str = ""
    manager_role: str = ""
    skills: list[str] = []


class UpdateDepartmentRequest(BaseModel):
    """更新部门请求"""
    name: Optional[str] = None
    parent_id: Optional[str] = None
    description: Optional[str] = None
    manager_role: Optional[str] = None
    skills: Optional[list[str]] = None
    status: Optional[str] = None


class DepartmentResponse(BaseModel):
    """部门响应"""
    id: str
    name: str
    code: str
    parent_id: Optional[str] = None
    level: int
    description: str
    manager_role: str
    skills: list[str]
    status: str
    order: int


def dept_to_response(dept: Department) -> DepartmentResponse:
    """转换为响应模型"""
    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        parent_id=dept.parent_id,
        level=dept.level,
        description=dept.description,
        manager_role=dept.manager_role,
        skills=dept.skills,
        status=dept.status,
        order=dept.order
    )


# === API Endpoints ===

@router.get("", response_model=list[DepartmentResponse])
async def list_departments():
    """列出所有部门"""
    depts = registry.list_all()
    return [dept_to_response(d) for d in depts]


@router.get("/tree", response_model=list[dict])
async def get_department_tree():
    """获取部门树"""
    return registry.get_tree()


@router.get("/level/{level}", response_model=list[DepartmentResponse])
async def list_departments_by_level(level: int):
    """按层级列出部门"""
    depts = registry.list_by_level(level)
    return [dept_to_response(d) for d in depts]


@router.get("/{dept_id}", response_model=DepartmentResponse)
async def get_department(dept_id: str):
    """获取部门详情"""
    dept = registry.get(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept_to_response(dept)


@router.get("/code/{code}", response_model=DepartmentResponse)
async def get_department_by_code(code: str):
    """通过代码获取部门"""
    dept = registry.get_by_code(code)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept_to_response(dept)


@router.post("", response_model=DepartmentResponse)
async def create_department(request: CreateDepartmentRequest):
    """创建部门"""
    # 检查code是否已存在
    existing = registry.get_by_code(request.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"Department code '{request.code}' already exists")

    dept = Department.create(
        name=request.name,
        code=request.code,
        level=request.level,
        parent_id=request.parent_id,
        description=request.description,
        manager_role=request.manager_role,
        skills=request.skills
    )

    registry.register(dept)
    return dept_to_response(dept)


@router.put("/{dept_id}", response_model=DepartmentResponse)
async def update_department(dept_id: str, request: UpdateDepartmentRequest):
    """更新部门"""
    # 排除None值
    updates = {k: v for k, v in request.model_dump().items() if v is not None}

    if "code" in updates:
        raise HTTPException(status_code=400, detail="Cannot change department code")

    dept = registry.update(dept_id, **updates)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    return dept_to_response(dept)


@router.delete("/{dept_id}")
async def delete_department(dept_id: str):
    """删除部门"""
    # 检查是否有子部门
    children = registry.list_children(dept_id)
    if children:
        raise HTTPException(status_code=400, detail="Cannot delete department with children")

    success = registry.delete(dept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")

    return {"message": "Department deleted"}


@router.get("/{dept_id}/children", response_model=list[DepartmentResponse])
async def list_children(dept_id: str):
    """列出子部门"""
    children = registry.list_children(dept_id)
    return [dept_to_response(d) for d in children]
