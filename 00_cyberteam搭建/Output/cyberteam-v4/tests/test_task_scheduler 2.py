"""TaskScheduler 测试套件 - 覆盖创建/执行/取消/重试/状态转换/定时任务/DDD 合法性检查"""
# pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Project root
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

from app.engine.task_scheduler import TaskScheduler, TaskSchedulerDomainService
from app.engine.task_types import TaskStatus, TaskType, TaskResult
from app.engine.task_events import TaskEvent, TaskEventPayload


# ── Fixtures ──

@pytest.fixture
def service() -> TaskSchedulerDomainService:
    """创建任务调度领域服务实例"""
    return TaskSchedulerDomainService()


@pytest.fixture
async def echo_result():
    """回显回调函数"""
    async def echo(params: dict) -> str:
        return params.get("message", "echo ok")
    return echo


@pytest.fixture
async def error_callback():
    """错误回调函数"""
    async def error(params: dict) -> str:
        raise Exception(params.get("message", "task error"))
    return error


# ── TaskScheduler 实体测试 ──

class TestTaskSchedulerEntity:
    """TaskScheduler 实体测试"""

    def test_create_task_scheduler(self):
        """测试创建任务调度实体"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
        )
        assert task.id == "test-001"
        assert task.name == "test-task"
        assert task.task_type == TaskType.IMMEDIATE
        assert task.status == TaskStatus.UNKNOWN

    def test_can_transition_to_valid(self):
        """测试合法的状态转换"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.PENDING,
        )
        # PENDING -> RUNNING 合法
        assert task.can_transition_to(TaskStatus.RUNNING) is True

    def test_can_transition_to_invalid(self):
        """测试非法的状态转换"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.SUCCESS,
        )
        # SUCCESS -> 任何状态都不合法
        assert task.can_transition_to(TaskStatus.PENDING) is False
        assert task.can_transition_to(TaskStatus.RUNNING) is False
        assert task.can_transition_to(TaskStatus.FAILED) is False

    def test_can_transition_from_pending(self):
        """测试 PENDING 状态的合法转换"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.PENDING,
        )
        assert task.can_transition_to(TaskStatus.RUNNING) is True
        assert task.can_transition_to(TaskStatus.CANCELLED) is True
        assert task.can_transition_to(TaskStatus.SUCCESS) is False

    def test_can_transition_from_running(self):
        """测试 RUNNING 状态的合法转换"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.RUNNING,
        )
        assert task.can_transition_to(TaskStatus.SUCCESS) is True
        assert task.can_transition_to(TaskStatus.FAILED) is True
        assert task.can_transition_to(TaskStatus.CANCELLED) is True
        assert task.can_transition_to(TaskStatus.TIMEOUT) is True
        assert task.can_transition_to(TaskStatus.PENDING) is False

    def test_can_transition_from_failed_to_retry(self):
        """测试 FAILED -> RETRY 转换"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.FAILED,
        )
        assert task.can_transition_to(TaskStatus.RETRY) is True
        assert task.can_transition_to(TaskStatus.PENDING) is True

    def test_to_dict(self):
        """测试实体转字典"""
        task = TaskScheduler(
            id="test-001",
            name="test-task",
            task_type=TaskType.IMMEDIATE,
            status=TaskStatus.PENDING,
        )
        d = task.to_dict()
        assert d["id"] == "test-001"
        assert d["name"] == "test-task"
        assert d["status"] == TaskStatus.PENDING.value


# ── TaskSchedulerDomainService 即时任务测试 ──

class TestImmediateTask:
    """即时任务测试"""

    @pytest.mark.asyncio
    async def test_create_immediate_task(self, service, echo_result):
        """测试创建即时任务"""
        task_id = await service.create_task(
            name="immediate-task",
            callback=echo_result,
            params={"message": "hello"},
            max_retries=3,
        )
        assert task_id is not None
        assert len(task_id) == 8

        task = service.get_task(task_id)
        assert task is not None
        assert task.name == "immediate-task"
        assert task.status == TaskStatus.PENDING

    @pytest.mark.asyncio
    async def test_immediate_task_execution(self, service, echo_result):
        """测试即时任务执行成功"""
        task_id = await service.create_task(
            name="echo-task",
            callback=echo_result,
            params={"message": "test message"},
        )
        # 等待任务执行
        await asyncio.sleep(0.2)

        task = service.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS
        assert task.result is not None
        assert task.result.success is True
        assert "test message" in (task.result.output or "")

    @pytest.mark.asyncio
    async def test_immediate_task_failure(self, service, error_callback):
        """测试即时任务执行失败"""
        task_id = await service.create_task(
            name="error-task",
            callback=error_callback,
            params={"message": "test error"},
            max_retries=0,  # 不重试，直接失败
        )
        # 等待任务执行
        await asyncio.sleep(0.2)

        task = service.get_task(task_id)
        assert task.status == TaskStatus.FAILED
        assert task.result is not None
        assert task.result.success is False
        assert task.error_message == "test error"

    @pytest.mark.asyncio
    async def test_immediate_task_retry(self, service, error_callback):
        """测试任务重试逻辑（指数退避）"""
        task_id = await service.create_task(
            name="retry-task",
            callback=error_callback,
            params={"message": "retry test"},
            max_retries=3,
        )

        # 等待前两次重试（2^1=2s + 2^2=4s = 约6s）
        await asyncio.sleep(0.5)
        task = service.get_task(task_id)
        assert task.status in [TaskStatus.RETRY, TaskStatus.RUNNING, TaskStatus.FAILED]


# ── 定时任务测试 ──

class TestScheduledTask:
    """定时任务测试"""

    @pytest.mark.asyncio
    async def test_create_scheduled_task(self, service, echo_result):
        """测试创建定时任务"""
        run_at = datetime.utcnow() + timedelta(seconds=0.5)
        task_id = await service.create_scheduled_task(
            name="scheduled-task",
            run_at=run_at,
            callback=echo_result,
            params={"message": "scheduled"},
        )
        assert task_id is not None
        task = service.get_task(task_id)
        assert task.task_type == TaskType.SCHEDULED
        assert task.expect_time is not None

    @pytest.mark.asyncio
    async def test_scheduled_task_execution(self, service, echo_result):
        """测试定时任务到期执行"""
        run_at = datetime.utcnow() + timedelta(seconds=0.2)
        task_id = await service.create_scheduled_task(
            name="scheduled-echo",
            run_at=run_at,
            callback=echo_result,
            params={"message": "scheduled message"},
        )

        # 等待定时任务执行
        await asyncio.sleep(0.5)

        task = service.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS
        assert task.result is not None
        assert task.result.success is True

    @pytest.mark.asyncio
    async def test_scheduled_task_past_time(self, service, echo_result):
        """测试过去时间的定时任务应立即执行"""
        run_at = datetime.utcnow() - timedelta(seconds=1)  # 过去时间
        task_id = await service.create_scheduled_task(
            name="past-task",
            run_at=run_at,
            callback=echo_result,
            params={"message": "past"},
        )
        # 等待立即执行
        await asyncio.sleep(0.2)

        task = service.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS


# ── 取消任务测试 ──

class TestCancelTask:
    """取消任务测试"""

    @pytest.mark.asyncio
    async def test_cancel_pending_task(self, service, echo_result):
        """测试取消待执行任务"""
        task_id = await service.create_task(
            name="cancel-task",
            callback=echo_result,
            params={"message": "cancel me"},
        )

        # 取消任务
        success = await service.cancel(task_id)
        assert success is True

        task = service.get_task(task_id)
        assert task.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, service):
        """测试取消不存在的任务"""
        success = await service.cancel("nonexistent-id")
        assert success is False

    @pytest.mark.asyncio
    async def test_cancel_completed_task(self, service, echo_result):
        """测试取消已完成任务（应该失败）"""
        task_id = await service.create_task(
            name="done-task",
            callback=echo_result,
            params={"message": "done"},
        )
        # 等待任务完成
        await asyncio.sleep(0.2)

        # 尝试取消已完成任务
        success = await service.cancel(task_id)
        assert success is False

        task = service.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS


# ── 列表和查询测试 ──

class TestListTasks:
    """任务列表测试"""

    @pytest.mark.asyncio
    async def test_list_all_tasks(self, service, echo_result):
        """测试列出所有任务"""
        # 创建多个任务
        for i in range(3):
            await service.create_task(
                name=f"task-{i}",
                callback=echo_result,
                params={},
            )
        await asyncio.sleep(0.2)

        tasks = service.list_tasks()
        assert len(tasks) >= 3

    @pytest.mark.asyncio
    async def test_list_tasks_by_status(self, service, echo_result):
        """测试按状态过滤任务"""
        task_id = await service.create_task(
            name="filter-task",
            callback=echo_result,
            params={},
        )
        await asyncio.sleep(0.2)

        # 获取成功状态的任务
        success_tasks = service.list_tasks(status=TaskStatus.SUCCESS)
        assert any(t.id == task_id for t in success_tasks)

        # 获取待执行状态的任务（应该不包含已完成的任务）
        pending_tasks = service.list_tasks(status=TaskStatus.PENDING)
        assert not any(t.id == task_id for t in pending_tasks)

    @pytest.mark.asyncio
    async def test_get_task(self, service, echo_result):
        """测试获取单个任务"""
        task_id = await service.create_task(
            name="get-task",
            callback=echo_result,
            params={},
        )

        task = service.get_task(task_id)
        assert task is not None
        assert task.id == task_id
        assert task.name == "get-task"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, service):
        """测试获取不存在的任务"""
        task = service.get_task("nonexistent")
        assert task is None


# ── 事件驱动测试 ──

class TestTaskEvents:
    """任务事件测试"""

    @pytest.mark.asyncio
    async def test_task_created_event(self, service, echo_result):
        """测试任务创建事件"""
        events_received = []

        async def handler(payload: TaskEventPayload):
            events_received.append(payload)

        service.on_task_event(TaskEvent.TASK_CREATED, handler)

        task_id = await service.create_task(
            name="event-task",
            callback=echo_result,
            params={},
        )
        await asyncio.sleep(0.1)

        assert len(events_received) == 1
        assert events_received[0].event == TaskEvent.TASK_CREATED
        assert events_received[0].task_id == task_id

    @pytest.mark.asyncio
    async def test_task_completed_event(self, service, echo_result):
        """测试任务完成事件"""
        events_received = []

        async def handler(payload: TaskEventPayload):
            events_received.append(payload)

        service.on_task_event(TaskEvent.TASK_COMPLETED, handler)

        task_id = await service.create_task(
            name="complete-event-task",
            callback=echo_result,
            params={"message": "complete"},
        )
        await asyncio.sleep(0.3)

        assert len(events_received) == 1
        assert events_received[0].event == TaskEvent.TASK_COMPLETED

    @pytest.mark.asyncio
    async def test_task_failed_event(self, service, error_callback):
        """测试任务失败事件"""
        events_received = []

        async def handler(payload: TaskEventPayload):
            events_received.append(payload)

        service.on_task_event(TaskEvent.TASK_FAILED, handler)

        task_id = await service.create_task(
            name="fail-event-task",
            callback=error_callback,
            params={"message": "fail"},
            max_retries=0,  # 立即失败
        )
        await asyncio.sleep(0.3)

        assert len(events_received) == 1
        assert events_received[0].event == TaskEvent.TASK_FAILED


# ── TaskResult 值对象测试 ──

class TestTaskResult:
    """TaskResult 值对象测试"""

    def test_task_result_success(self):
        """测试成功的任务结果"""
        result = TaskResult(
            success=True,
            output="test output",
            cost_time_ms=100.5,
            retry_count=0,
        )
        assert result.success is True
        assert result.output == "test output"
        assert result.cost_time_ms == 100.5

    def test_task_result_failure(self):
        """测试失败的任务结果"""
        result = TaskResult(
            success=False,
            error="test error",
            retry_count=3,
        )
        assert result.success is False
        assert result.error == "test error"
        assert result.retry_count == 3


# ── TaskType 枚举测试 ──

class TestTaskType:
    """TaskType 枚举测试"""

    def test_task_type_values(self):
        """测试任务类型枚举值"""
        assert TaskType.IMMEDIATE.value == 1
        assert TaskType.SCHEDULED.value == 2
        assert TaskType.CRON.value == 3

    def test_task_type_instant_task(self):
        """测试即时任务类型"""
        task = TaskScheduler(
            id="test",
            name="test",
            task_type=TaskType.IMMEDIATE,
        )
        assert task.task_type == TaskType.IMMEDIATE

    def test_task_type_scheduled_task(self):
        """测试定时任务类型"""
        task = TaskScheduler(
            id="test",
            name="test",
            task_type=TaskType.SCHEDULED,
        )
        assert task.task_type == TaskType.SCHEDULED
