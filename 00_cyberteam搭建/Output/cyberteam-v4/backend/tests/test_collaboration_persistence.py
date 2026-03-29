"""协作引擎持久化测试 - 验证 Handoff 和 CollaborationTask 的数据库操作。"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.engine.collaboration_repository import CollaborationRepository
from app.models import HandoffStatus, CollaborationTaskState, Base


# 测试数据库 URL（使用 SQLite 内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    """创建测试数据库引擎。"""
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def session(engine):
    """创建测试数据库会话。"""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


class TestCollaborationRepository:
    """测试 CollaborationRepository 的所有方法。"""

    @pytest.mark.asyncio
    async def test_create_collaboration_task(self, session):
        """测试创建协作任务。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="制定市场推广方案",
            primary_department="marketing",
            collaborating_departments=["operations", "design"],
            match_scores={"marketing": 0.95, "operations": 0.75, "design": 0.60},
        )

        assert task.task_id is not None
        assert task.original_task == "制定市场推广方案"
        assert task.primary_department == "marketing"
        # collaborating_departments 只包含协作部门，不包含 primary_department
        assert len(task.collaborating_departments) == 2  # operations + design
        assert task.status == CollaborationTaskState.PENDING

    @pytest.mark.asyncio
    async def test_get_collaboration_task(self, session):
        """测试获取协作任务。"""
        repo = CollaborationRepository(session)

        # 创建任务
        created = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="hr",
        )

        # 获取任务
        fetched = await repo.get_collaboration_task(created.task_id)

        assert fetched is not None
        assert fetched.task_id == created.task_id
        assert fetched.original_task == "测试任务"
        assert fetched.primary_department == "hr"

    @pytest.mark.asyncio
    async def test_update_collaboration_task_status(self, session):
        """测试更新协作任务状态。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="engineering",
        )

        # 更新状态为 IN_PROGRESS
        updated = await repo.update_collaboration_task_status(
            task.task_id,
            CollaborationTaskState.IN_PROGRESS,
        )

        assert updated is not None
        assert updated.status == CollaborationTaskState.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_update_collaboration_task_results(self, session):
        """测试更新协作任务结果。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="finance",
        )

        # 更新结果
        results = {
            "finance": {"status": "success", "output": "预算方案已制定"},
        }
        final_output = {"summary": "任务完成"}

        updated = await repo.update_collaboration_task_results(
            task.task_id,
            results=results,
            final_output=final_output,
        )

        assert updated is not None
        assert updated.results == results
        assert updated.final_output == final_output

    @pytest.mark.asyncio
    async def test_create_handoff(self, session):
        """测试创建 Handoff。"""
        repo = CollaborationRepository(session)

        # 先创建任务
        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="marketing",
        )

        # 创建 Handoff
        handoff = await repo.create_handoff(
            task_id=task.task_id,
            from_department="marketing",
            to_department="operations",
            context={"reason": "需要运营配合"},
            notes="测试移交",
        )

        assert handoff.handoff_id is not None
        assert handoff.task_id == task.task_id
        assert handoff.from_department == "marketing"
        assert handoff.to_department == "operations"
        assert handoff.status == HandoffStatus.PENDING
        assert handoff.context["reason"] == "需要运营配合"

        # 验证任务的 total_handoffs 计数增加
        updated_task = await repo.get_collaboration_task(task.task_id)
        assert updated_task.total_handoffs == 1

    @pytest.mark.asyncio
    async def test_get_handoff(self, session):
        """测试获取 Handoff。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="product",
        )

        created = await repo.create_handoff(
            task_id=task.task_id,
            from_department="product",
            to_department="engineering",
            context={},
        )

        fetched = await repo.get_handoff(created.handoff_id)

        assert fetched is not None
        assert fetched.handoff_id == created.handoff_id
        assert fetched.from_department == "product"
        assert fetched.to_department == "engineering"

    @pytest.mark.asyncio
    async def test_list_handoffs_by_task(self, session):
        """测试列出任务的所有 Handoff。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="design",
        )

        # 创建多个 Handoff
        await repo.create_handoff(
            task_id=task.task_id,
            from_department="design",
            to_department="marketing",
            context={},
        )
        await repo.create_handoff(
            task_id=task.task_id,
            from_department="marketing",
            to_department="operations",
            context={},
        )

        # 列出所有 Handoff
        handoffs = await repo.list_handoffs_by_task(task.task_id)

        assert len(handoffs) == 2
        assert handoffs[0].from_department == "design"
        assert handoffs[1].from_department == "marketing"

    @pytest.mark.asyncio
    async def test_update_handoff_status(self, session):
        """测试更新 Handoff 状态。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="ceo",
        )

        handoff = await repo.create_handoff(
            task_id=task.task_id,
            from_department="ceo",
            to_department="hr",
            context={},
        )

        # 更新状态为 IN_PROGRESS
        updated = await repo.update_handoff_status(
            handoff.handoff_id,
            HandoffStatus.IN_PROGRESS,
        )

        assert updated is not None
        assert updated.status == HandoffStatus.IN_PROGRESS

        # 更新状态为 COMPLETED，带结果
        result = {"status": "success", "output": "招聘完成"}
        updated = await repo.update_handoff_status(
            handoff.handoff_id,
            HandoffStatus.COMPLETED,
            result=result,
        )

        assert updated.status == HandoffStatus.COMPLETED
        assert updated.completed_at is not None
        assert updated.result == result

        # 验证任务的 completed_handoffs 计数增加
        updated_task = await repo.get_collaboration_task(task.task_id)
        assert updated_task.completed_handoffs == 1

    @pytest.mark.asyncio
    async def test_update_handoff_result(self, session):
        """测试更新 Handoff 结果。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="hr",
        )

        handoff = await repo.create_handoff(
            task_id=task.task_id,
            from_department="hr",
            to_department="finance",
            context={},
        )

        # 更新结果
        result = {"budget": 100000, "approved": True}
        updated = await repo.update_handoff_result(
            handoff.handoff_id,
            result=result,
        )

        assert updated is not None
        assert updated.result == result

    @pytest.mark.asyncio
    async def test_delete_handoff(self, session):
        """测试删除 Handoff。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="operations",
        )

        handoff = await repo.create_handoff(
            task_id=task.task_id,
            from_department="operations",
            to_department="design",
            context={},
        )

        # 删除
        success = await repo.delete_handoff(handoff.handoff_id)
        assert success is True

        # 验证已删除
        fetched = await repo.get_handoff(handoff.handoff_id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_list_collaboration_tasks(self, session):
        """测试列出协作任务。"""
        repo = CollaborationRepository(session)

        # 创建多个任务
        await repo.create_collaboration_task(
            original_task="任务1",
            primary_department="marketing",
        )
        await repo.create_collaboration_task(
            original_task="任务2",
            primary_department="engineering",
        )
        await repo.create_collaboration_task(
            original_task="任务3",
            primary_department="hr",
        )

        # 列出所有任务
        tasks = await repo.list_collaboration_tasks()
        assert len(tasks) == 3

        # 按状态过滤
        pending_tasks = await repo.list_collaboration_tasks(
            status=CollaborationTaskState.PENDING
        )
        assert len(pending_tasks) == 3

        # 分页
        page1 = await repo.list_collaboration_tasks(limit=2, offset=0)
        assert len(page1) == 2

    @pytest.mark.asyncio
    async def test_get_collaboration_statistics(self, session):
        """测试获取协作统计信息。"""
        repo = CollaborationRepository(session)

        task = await repo.create_collaboration_task(
            original_task="测试任务",
            primary_department="ceo",
            collaborating_departments=["hr", "finance"],
        )

        # 创建多个 Handoff
        handoff1 = await repo.create_handoff(
            task_id=task.task_id,
            from_department="ceo",
            to_department="hr",
            context={},
        )

        handoff2 = await repo.create_handoff(
            task_id=task.task_id,
            from_department="hr",
            to_department="finance",
            context={},
        )

        # 完成一个 Handoff
        await repo.update_handoff_status(
            handoff1.handoff_id,
            HandoffStatus.COMPLETED,
        )

        # 获取统计信息
        stats = await repo.get_collaboration_statistics(task.task_id)

        assert stats["task_id"] == task.task_id
        assert stats["total_handoffs"] == 2
        assert stats["completed_handoffs"] == 1
        assert stats["pending_handoffs"] == 1
        assert stats["completion_rate"] == 0.5


@pytest.mark.parametrize("original_task,primary_dept,expected_status", [
    ("制定营销方案", "marketing", CollaborationTaskState.PENDING),
    ("招聘工程师", "hr", CollaborationTaskState.PENDING),
    ("设计架构", "engineering", CollaborationTaskState.PENDING),
])
@pytest.mark.asyncio
async def test_parametrized_task_creation(
    session,
    original_task,
    primary_dept,
    expected_status,
):
    """参数化测试：创建不同类型的协作任务。"""
    repo = CollaborationRepository(session)

    task = await repo.create_collaboration_task(
        original_task=original_task,
        primary_department=primary_dept,
    )

    assert task.original_task == original_task
    assert task.primary_department == primary_dept
    assert task.status == expected_status


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
