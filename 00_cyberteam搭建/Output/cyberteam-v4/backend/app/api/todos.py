"""TODO API — 简单的待办事项管理。

提供 RESTful API 用于创建、读取、更新、删除待办事项。
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from ..db import get_db
from ..models import TodoItem, TodoItemState, TodoItemPriority

log = logging.getLogger("cyberteam.api.todos")
router = APIRouter()


# ── Schemas (请求/响应模型) ──

class TodoItemCreate(BaseModel):
    """创建待办事项请求。"""
    title: str = Field(..., min_length=1, max_length=500, description="待办事项标题")
    description: Optional[str] = Field(None, max_length=5000, description="详细描述")
    priority: TodoItemPriority = Field(default=TodoItemPriority.MEDIUM, description="优先级")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    due_date: Optional[str] = Field(None, description="截止日期 (ISO 8601 格式)")


class TodoItemUpdate(BaseModel):
    """更新待办事项请求。"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    state: Optional[TodoItemState] = None
    priority: Optional[TodoItemPriority] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None


class TodoItemOut(BaseModel):
    """待办事项响应。"""
    id: str
    title: str
    description: Optional[str]
    state: str
    priority: str
    category: Optional[str]
    tags: List[str]
    due_date: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class TodoListResponse(BaseModel):
    """待办事项列表响应。"""
    items: List[TodoItemOut]
    total: int
    limit: int
    offset: int


class StatsResponse(BaseModel):
    """统计信息响应。"""
    total: int
    by_state: dict
    by_priority: dict


# ── Helper Functions ──

def _parse_due_date(due_date_str: Optional[str]) -> Optional[datetime]:
    """解析 ISO 8601 日期字符串。"""
    if not due_date_str:
        return None
    try:
        return datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid due_date format: {due_date_str}. Use ISO 8601 format."
        )


# ── Endpoints ──

@router.get("", response_model=TodoListResponse)
async def list_todos(
    state: Optional[TodoItemState] = Query(None, description="按状态筛选"),
    priority: Optional[TodoItemPriority] = Query(None, description="按优先级筛选"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    search: Optional[str] = Query(None, description="搜索标题或描述"),
    limit: int = Query(default=50, ge=1, le=200, description="每页数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
):
    """获取待办事项列表。

    支持按状态、优先级、分类筛选，支持关键词搜索。
    """
    # 构建查询
    stmt = select(TodoItem)

    # 应用筛选条件
    if state:
        stmt = stmt.filter(TodoItem.state == state)
    if priority:
        stmt = stmt.filter(TodoItem.priority == priority)
    if category:
        stmt = stmt.filter(TodoItem.category == category)
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.filter(
            (TodoItem.title.ilike(search_pattern)) |
            (TodoItem.description.ilike(search_pattern))
        )

    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()

    # 分页和排序
    stmt = stmt.order_by(TodoItem.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return TodoListResponse(
        items=[TodoItemOut.model_validate(item.to_dict()) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=StatsResponse)
async def get_todo_stats(db: AsyncSession = Depends(get_db)):
    """获取待办事项统计信息。

    返回总数、按状态分组、按优先级分组的统计。
    """
    # 按状态统计
    state_stmt = select(TodoItem.state, func.count(TodoItem.id)).group_by(TodoItem.state)
    state_result = await db.execute(state_stmt)
    by_state = {row[0].value: row[1] for row in state_result.all()}

    # 按优先级统计
    priority_stmt = select(TodoItem.priority, func.count(TodoItem.id)).group_by(TodoItem.priority)
    priority_result = await db.execute(priority_stmt)
    by_priority = {row[0].value: row[1] for row in priority_result.all()}

    total = sum(by_state.values())

    return StatsResponse(
        total=total,
        by_state=by_state,
        by_priority=by_priority,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TodoItemOut)
async def create_todo(
    body: TodoItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新的待办事项。"""
    todo_id = str(uuid.uuid4())
    due_date = _parse_due_date(body.due_date)

    todo = TodoItem(
        id=todo_id,
        title=body.title,
        description=body.description,
        state=TodoItemState.TODO,
        priority=body.priority,
        category=body.category,
        tags=body.tags,
        due_date=due_date,
    )

    db.add(todo)
    await db.commit()
    await db.refresh(todo)

    log.info(f"Todo created: {todo_id}")

    return TodoItemOut.model_validate(todo.to_dict())


@router.get("/{todo_id}", response_model=TodoItemOut)
async def get_todo(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个待办事项详情。"""
    stmt = select(TodoItem).filter(TodoItem.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item not found: {todo_id}"
        )

    return TodoItemOut.model_validate(todo.to_dict())


@router.patch("/{todo_id}", response_model=TodoItemOut)
async def update_todo(
    todo_id: str,
    body: TodoItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新待办事项。

    支持部分更新，只更新提供的字段。
    """
    stmt = select(TodoItem).filter(TodoItem.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item not found: {todo_id}"
        )

    # 更新字段
    if body.title is not None:
        todo.title = body.title
    if body.description is not None:
        todo.description = body.description
    if body.state is not None:
        todo.state = body.state
        # 如果状态变为完成，记录完成时间
        if body.state == TodoItemState.DONE and not todo.completed_at:
            todo.completed_at = datetime.utcnow()
        # 如果状态从完成变回其他状态，清除完成时间
        elif body.state != TodoItemState.DONE:
            todo.completed_at = None
    if body.priority is not None:
        todo.priority = body.priority
    if body.category is not None:
        todo.category = body.category
    if body.tags is not None:
        todo.tags = body.tags
    if body.due_date is not None:
        todo.due_date = _parse_due_date(body.due_date)

    await db.commit()
    await db.refresh(todo)

    log.info(f"Todo updated: {todo_id}")

    return TodoItemOut.model_validate(todo.to_dict())


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除待办事项。"""
    stmt = select(TodoItem).filter(TodoItem.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item not found: {todo_id}"
        )

    await db.delete(todo)
    await db.commit()

    log.info(f"Todo deleted: {todo_id}")

    return None


@router.post("/{todo_id}/complete", response_model=TodoItemOut)
async def complete_todo(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """标记待办事项为完成。"""
    stmt = select(TodoItem).filter(TodoItem.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item not found: {todo_id}"
        )

    todo.state = TodoItemState.DONE
    todo.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(todo)

    log.info(f"Todo completed: {todo_id}")

    return TodoItemOut.model_validate(todo.to_dict())


@router.post("/{todo_id}/reopen", response_model=TodoItemOut)
async def reopen_todo(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """重新打开已完成的待办事项。"""
    stmt = select(TodoItem).filter(TodoItem.id == todo_id)
    result = await db.execute(stmt)
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo item not found: {todo_id}"
        )

    todo.state = TodoItemState.TODO
    todo.completed_at = None

    await db.commit()
    await db.refresh(todo)

    log.info(f"Todo reopened: {todo_id}")

    return TodoItemOut.model_validate(todo.to_dict())


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有使用的分类列表。"""
    stmt = select(TodoItem.category).filter(
        TodoItem.category.isnot(None)
    ).distinct()
    result = await db.execute(stmt)
    categories = [row[0] for row in result.all() if row[0]]

    return {"categories": categories}


@router.get("/tags/list")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """获取所有使用的标签列表。"""
    stmt = select(TodoItem).filter(
        TodoItem.tags.isnot(None)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    # 收集所有标签并去重
    all_tags = set()
    for item in items:
        if isinstance(item.tags, list):
            all_tags.update(item.tags)

    return {"tags": sorted(all_tags)}
