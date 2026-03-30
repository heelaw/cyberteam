"""
数字员工 API 接口

提供数字员工的 CRUD 和任务执行接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from app.engine.employee_engine import (
    EmployeeMarketplace,
    DigitalEmployee,
    DigitalEmployeeConfig,
    TaskResult
)

router = APIRouter(prefix="/api/employees", tags=["employees"])

# 全局实例
marketplace = EmployeeMarketplace()


# === Request/Response Models ===

class CreateEmployeeRequest(BaseModel):
    """创建数字员工请求"""
    template_id: str
    name: Optional[str] = None


class TaskRequest(BaseModel):
    """任务请求"""
    task: str
    employee_id: Optional[str] = None
    template_id: Optional[str] = None


class EmployeeResponse(BaseModel):
    """数字员工响应"""
    id: str
    name: str
    role: str
    description: str
    skills: list[str]
    status: str


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    content: str = ""


# === API Endpoints ===

@router.get("/templates", response_model=list[EmployeeResponse])
async def list_templates():
    """列出可用的数字员工模板"""
    templates = marketplace.registry.list_templates()
    return [
        EmployeeResponse(
            id=t.id,
            name=t.name,
            role=t.role,
            description=t.description,
            skills=t.skills,
            status="template"
        )
        for t in templates
    ]


@router.get("", response_model=list[EmployeeResponse])
async def list_employees():
    """列出所有已创建的数字员工"""
    employees = marketplace.registry.list_all()
    return [
        EmployeeResponse(
            id=emp.config.id,
            name=emp.config.name,
            role=emp.config.role,
            description=emp.config.description,
            skills=emp.config.skills,
            status=emp.status
        )
        for emp in employees
    ]


@router.post("", response_model=EmployeeResponse)
async def create_employee(request: CreateEmployeeRequest):
    """创建新的数字员工"""
    try:
        emp = await marketplace.create_employee(
            template_id=request.template_id,
            name=request.name
        )
        return EmployeeResponse(
            id=emp.config.id,
            name=emp.config.name,
            role=emp.config.role,
            description=emp.config.description,
            skills=emp.config.skills,
            status=emp.status
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str):
    """获取数字员工详情"""
    emp = marketplace.registry.get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return EmployeeResponse(
        id=emp.config.id,
        name=emp.config.name,
        role=emp.config.role,
        description=emp.config.description,
        skills=emp.config.skills,
        status=emp.status
    )


@router.delete("/{employee_id}")
async def delete_employee(employee_id: str):
    """删除数字员工"""
    emp = marketplace.registry.get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    del marketplace.registry.employees[employee_id]
    return {"message": "Employee deleted"}


@router.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """执行任务"""
    try:
        task_id = await marketplace.execute_task(
            task=request.task,
            employee_id=request.employee_id,
            template_id=request.template_id
        )

        # 等待任务完成（简化处理，生产环境应使用 WebSocket/SSE）
        import asyncio
        await asyncio.sleep(1)

        result = marketplace.task_queue.get_task_status(task_id)
        if result:
            return TaskResponse(
                task_id=result.task_id,
                status=result.status,
                content=result.content
            )

        return TaskResponse(
            task_id=task_id,
            status="running",
            content=""
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    result = marketplace.task_queue.get_task_status(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        task_id=result.task_id,
        status=result.status,
        content=result.content
    )
