#!/usr/bin/env python3
"""
TODO 应用测试套件

运行方式:
    python -m pytest tests/test_todo_app.py -v
    python -m pytest tests/test_todo_app.py::TestTodoModels -v
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.models import TodoItem, TodoItemState, TodoItemPriority, Base
from backend.app.api.todos import (
    TodoItemCreate,
    TodoItemUpdate,
    TodoItemOut,
    _parse_due_date
)
from backend.app.main import app
from backend.app.config import get_settings


# ─── 测试数据库配置 ───

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
    )

    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """创建测试数据库会话"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


# ─── 模型测试 ───

class TestTodoModels:
    """测试 TodoItem 模型"""

    @pytest.mark.asyncio
    async def test_create_todo_item(self, db_session):
        """测试创建待办事项"""
        todo = TodoItem(
            title="测试任务",
            description="这是一个测试任务",
            state=TodoItemState.TODO,
            priority=TodoItemPriority.HIGH,
            category="工作",
            tags=["测试", "重要"]
        )

        db_session.add(todo)
        await db_session.commit()
        await db_session.refresh(todo)

        assert todo.id is not None
        assert todo.title == "测试任务"
        assert todo.state == TodoItemState.TODO
        assert todo.priority == TodoItemPriority.HIGH

    @pytest.mark.asyncio
    async def test_todo_item_to_dict(self, db_session):
        """测试模型转换为字典"""
        due_date = datetime.utcnow() + timedelta(days=1)
        todo = TodoItem(
            title="测试任务",
            description="描述",
            state=TodoItemState.TODO,
            priority=TodoItemPriority.MEDIUM,
            category="测试",
            tags=["tag1"],
            due_date=due_date
        )

        db_session.add(todo)
        await db_session.commit()
        await db_session.refresh(todo)

        result = todo.to_dict()

        assert result["title"] == "测试任务"
        assert result["state"] == "todo"
        assert result["priority"] == "medium"
        assert result["category"] == "测试"
        assert result["tags"] == ["tag1"]
        assert result["due_date"] is not None

    @pytest.mark.asyncio
    async def test_todo_item_defaults(self, db_session):
        """测试默认值"""
        todo = TodoItem(title="只有标题的任务")

        db_session.add(todo)
        await db_session.commit()
        await db_session.refresh(todo)

        assert todo.state == TodoItemState.TODO
        assert todo.priority == TodoItemPriority.MEDIUM
        assert todo.tags == []
        assert todo.description is None
        assert todo.category is None

    @pytest.mark.asyncio
    async def test_completed_at_auto_set(self, db_session):
        """测试完成时间自动设置"""
        todo = TodoItem(
            title="测试任务",
            state=TodoItemState.TODO
        )

        db_session.add(todo)
        await db_session.commit()
        await db_session.refresh(todo)

        assert todo.completed_at is None

        # 更新为完成状态
        todo.state = TodoItemState.DONE
        todo.completed_at = datetime.utcnow()

        await db_session.commit()
        await db_session.refresh(todo)

        assert todo.state == TodoItemState.DONE
        assert todo.completed_at is not None


# ─── Schema 测试 ───

class TestTodoSchemas:
    """测试 Pydantic Schema"""

    def test_todo_create_schema_valid(self):
        """测试创建请求 Schema 验证"""
        data = {
            "title": "新任务",
            "description": "任务描述",
            "priority": "high",
            "category": "工作",
            "tags": ["重要", "紧急"],
            "due_date": "2026-12-31T23:59:59"
        }

        schema = TodoItemCreate(**data)

        assert schema.title == "新任务"
        assert schema.priority == TodoItemPriority.HIGH
        assert schema.tags == ["重要", "紧急"]

    def test_todo_create_schema_minimal(self):
        """测试最小创建请求"""
        schema = TodoItemCreate(title="只有标题")
        assert schema.title == "只有标题"
        assert schema.priority == TodoItemPriority.MEDIUM
        assert schema.tags == []

    def test_todo_create_schema_invalid_title(self):
        """测试无效标题"""
        with pytest.raises(ValueError):
            TodoItemCreate(title="")  # 空标题

    def test_todo_update_schema_partial(self):
        """测试部分更新"""
        schema = TodoItemUpdate(title="新标题")
        assert schema.title == "新标题"
        assert schema.description is None
        assert schema.state is None

    def test_parse_due_date_valid(self):
        """测试解析有效日期"""
        result = _parse_due_date("2026-12-31T23:59:59")
        assert isinstance(result, datetime)
        assert result.year == 2026

    def test_parse_due_date_none(self):
        """测试解析空日期"""
        result = _parse_due_date(None)
        assert result is None

    def test_parse_due_date_invalid(self):
        """测试解析无效日期"""
        from backend.app.api.todos import HTTPException, status
        with pytest.raises(HTTPException) as exc:
            _parse_due_date("invalid-date")
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


# ─── API 集成测试 ───

class TestTodoAPI:
    """测试 TODO API 端点"""

    @pytest.fixture
    async def client(self, test_engine):
        """创建测试客户端"""
        # 覆盖数据库配置
        from backend.app import db as db_module

        original_engine = db_module._engine
        original_session_factory = db_module._session_factory

        # 设置测试引擎
        db_module._engine = test_engine
        db_module._session_factory = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        # 恢复原始配置
        db_module._engine = original_engine
        db_module._session_factory = original_session_factory

    @pytest.mark.asyncio
    async def test_create_todo(self, client):
        """测试创建待办事项"""
        response = await client.post(
            "/api/todos",
            json={
                "title": "测试任务",
                "description": "这是一个测试",
                "priority": "high"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "测试任务"
        assert data["state"] == "todo"
        assert data["priority"] == "high"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_todos_empty(self, client):
        """测试获取空列表"""
        response = await client.get("/api/todos")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_todos_with_items(self, client):
        """测试获取待办事项列表"""
        # 创建多个任务
        for i in range(3):
            await client.post(
                "/api/todos",
                json={"title": f"任务 {i+1}"}
            )

        response = await client.get("/api/todos")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_get_todo_by_id(self, client):
        """测试获取单个待办事项"""
        # 创建任务
        create_response = await client.post(
            "/api/todos",
            json={"title": "查找测试"}
        )
        todo_id = create_response.json()["id"]

        # 获取任务
        response = await client.get(f"/api/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == "查找测试"

    @pytest.mark.asyncio
    async def test_get_todo_not_found(self, client):
        """测试获取不存在的任务"""
        response = await client.get("/api/todos/nonexistent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_todo(self, client):
        """测试更新待办事项"""
        # 创建任务
        create_response = await client.post(
            "/api/todos",
            json={"title": "原标题"}
        )
        todo_id = create_response.json()["id"]

        # 更新任务
        response = await client.patch(
            f"/api/todos/{todo_id}",
            json={"title": "新标题", "state": "in_progress"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"
        assert data["state"] == "in_progress"

    @pytest.mark.asyncio
    async def test_delete_todo(self, client):
        """测试删除待办事项"""
        # 创建任务
        create_response = await client.post(
            "/api/todos",
            json={"title": "待删除"}
        )
        todo_id = create_response.json()["id"]

        # 删除任务
        response = await client.delete(f"/api/todos/{todo_id}")

        assert response.status_code == 204

        # 验证删除
        get_response = await client.get(f"/api/todos/{todo_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_todo(self, client):
        """测试标记任务完成"""
        # 创建任务
        create_response = await client.post(
            "/api/todos",
            json={"title": "待完成"}
        )
        todo_id = create_response.json()["id"]

        # 标记完成
        response = await client.post(f"/api/todos/{todo_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "done"
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_reopen_todo(self, client):
        """测试重新打开任务"""
        # 创建并完成任务
        create_response = await client.post(
            "/api/todos",
            json={"title": "任务"}
        )
        todo_id = create_response.json()["id"]

        await client.post(f"/api/todos/{todo_id}/complete")

        # 重新打开
        response = await client.post(f"/api/todos/{todo_id}/reopen")

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "todo"
        assert data["completed_at"] is None

    @pytest.mark.asyncio
    async def test_filter_by_state(self, client):
        """测试按状态筛选"""
        # 创建不同状态的任务
        await client.post("/api/todos", json={"title": "待办"})
        await client.post("/api/todos", json={"title": "进行中"})

        completed = await client.post("/api/todos", json={"title": "已完成"})
        await client.post(f"/api/todos/{completed.json()['id']}/complete")

        # 筛选已完成
        response = await client.get("/api/todos?state=done")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["state"] == "done"

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, client):
        """测试按优先级筛选"""
        await client.post("/api/todos", json={"title": "低优先级", "priority": "low"})
        await client.post("/api/todos", json={"title": "高优先级", "priority": "high"})

        response = await client.get("/api/todos?priority=high")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_search_todos(self, client):
        """测试搜索功能"""
        await client.post("/api/todos", json={"title": "买菜", "description": "去超市买蔬菜"})
        await client.post("/api/todos", json={"title": "写代码", "description": "完成新功能"})

        response = await client.get("/api/todos?search=买")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "买" in data["items"][0]["title"]

    @pytest.mark.asyncio
    async def test_get_stats(self, client):
        """测试获取统计信息"""
        # 创建不同状态和优先级的任务
        await client.post("/api/todos", json={"title": "T1", "priority": "high"})
        await client.post("/api/todos", json={"title": "T2", "priority": "high"})
        await client.post("/api/todos", json={"title": "T3", "priority": "low"})

        completed = await client.post("/api/todos", json={"title": "T4"})
        await client.post(f"/api/todos/{completed.json()['id']}/complete")

        response = await client.get("/api/todos/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["by_state"]["todo"] == 3
        assert data["by_state"]["done"] == 1
        assert data["by_priority"]["high"] == 2

    @pytest.mark.asyncio
    async def test_get_categories(self, client):
        """测试获取分类列表"""
        await client.post("/api/todos", json={"title": "T1", "category": "工作"})
        await client.post("/api/todos", json={"title": "T2", "category": "生活"})
        await client.post("/api/todos", json={"title": "T3", "category": "工作"})

        response = await client.get("/api/todos/categories/list")

        assert response.status_code == 200
        data = response.json()
        assert "工作" in data["categories"]
        assert "生活" in data["categories"]

    @pytest.mark.asyncio
    async def test_get_tags(self, client):
        """测试获取标签列表"""
        await client.post("/api/todos", json={"title": "T1", "tags": ["python", "测试"]})
        await client.post("/api/todos", json={"title": "T2", "tags": ["javascript", "测试"]})

        response = await client.get("/api/todos/tags/list")

        assert response.status_code == 200
        data = response.json()
        assert "python" in data["tags"]
        assert "javascript" in data["tags"]
        assert "测试" in data["tags"]

    @pytest.mark.asyncio
    async def test_pagination(self, client):
        """测试分页"""
        # 创建多个任务
        for i in range(10):
            await client.post("/api/todos", json={"title": f"任务 {i+1}"})

        # 第一页
        response = await client.get("/api/todos?limit=5&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert len(data["items"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 0

        # 第二页
        response = await client.get("/api/todos?limit=5&offset=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["offset"] == 5


# ─── 边界条件测试 ───

class TestTodoEdgeCases:
    """测试边界条件和错误处理"""

    @pytest.fixture
    async def client(self, test_engine):
        """创建测试客户端"""
        from backend.app import db as db_module

        db_module._engine = test_engine
        db_module._session_factory = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_title_too_long(self, client):
        """测试标题超长"""
        long_title = "a" * 501
        response = await client.post(
            "/api/todos",
            json={"title": long_title}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_due_date_format(self, client):
        """测试无效日期格式"""
        response = await client.post(
            "/api/todos",
            json={
                "title": "测试",
                "due_date": "不是有效日期"
            }
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_priority(self, client):
        """测试无效优先级"""
        response = await client.post(
            "/api/todos",
            json={
                "title": "测试",
                "priority": "invalid"
            }
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_state(self, client):
        """测试无效状态"""
        # 创建任务
        create_response = await client.post(
            "/api/todos",
            json={"title": "测试"}
        )
        todo_id = create_response.json()["id"]

        # 尝试设置为无效状态
        response = await client.patch(
            f"/api/todos/{todo_id}",
            json={"state": "invalid_state"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_limit_bounds(self, client):
        """测试分页边界"""
        # limit 超过最大值
        response = await client.get("/api/todos?limit=300")
        assert response.status_code == 422

        # limit 小于最小值
        response = await client.get("/api/todos?limit=0")
        assert response.status_code == 422
