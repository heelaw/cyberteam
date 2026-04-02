"""collaboration.py 单元测试 - 跨部门协作引擎完整覆盖。"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
from app.engine.collaboration import (
    CollaborationEngine,
    TaskStatus,
    HandoffStatus,
    DEPARTMENT_EXECUTORS,
    AgentExecutor,
    ExecutionResult,
)
from app.engine.ceo_metadata import CEORouter


def pytest_configure(config):
    """Configure pytest for async tests."""
    config.addinivalue_hook(
        "asyncio_mode",
        lambda mode, config: "auto",
    )


class TestCEORouter:
    """测试CEO智能路由。"""

    def test_router_singleton(self):
        """测试路由器单例。"""
        router = CEORouter()
        assert router is not None

    def test_single_department_routing(self):
        """测试单部门路由。"""
        router = CEORouter()
        result = router.route("帮我写一个小红书推广方案")
        assert result["target_department"] == "marketing"
        assert result["match_score"] > 0

    def test_product_routing(self):
        """测试产品部路由。"""
        router = CEORouter()
        result = router.route("撰写产品需求文档PRD")
        assert result["target_department"] == "product"

    def test_engineering_routing(self):
        """测试技术部路由。"""
        router = CEORouter()
        result = router.route("设计微服务架构")
        assert result["target_department"] == "engineering"

    def test_hr_routing(self):
        """测试人力部路由。"""
        router = CEORouter()
        result = router.route("招聘高级工程师")
        assert result["target_department"] == "hr"

    def test_finance_routing(self):
        """测试财务部路由。"""
        router = CEORouter()
        result = router.route("制定下季度预算")
        assert result["target_department"] in ["finance", "operations"]

    def test_department_metadata(self):
        """测试部门元数据。"""
        from app.engine.ceo_metadata import DEPARTMENT_METADATA
        assert "ceo" in DEPARTMENT_METADATA
        assert "marketing" in DEPARTMENT_METADATA
        assert len(DEPARTMENT_METADATA) == 8


class TestDepartmentExecutors:
    """测试部门执行器。"""

    @pytest.mark.asyncio
    async def test_marketing_executor(self):
        """测试市场部执行器。"""
        from app.engine.collaboration import MarketingAgentExecutor
        executor = MarketingAgentExecutor()
        result = await executor.execute("测试任务", {})
        assert result.department_id == "marketing"
        assert result.status == "success"
        assert "brand_strategy" in result.output

    @pytest.mark.asyncio
    async def test_operations_executor(self):
        """测试运营部执行器。"""
        from app.engine.collaboration import OperationsAgentExecutor
        executor = OperationsAgentExecutor()
        result = await executor.execute("测试任务", {})
        assert result.department_id == "operations"
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_design_executor(self):
        """测试设计部执行器。"""
        from app.engine.collaboration import DesignAgentExecutor
        executor = DesignAgentExecutor()
        result = await executor.execute("测试任务", {})
        assert result.department_id == "design"
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_hr_executor(self):
        """测试人力部执行器。"""
        from app.engine.collaboration import HRAgentExecutor
        executor = HRAgentExecutor()
        result = await executor.execute("招聘工程师", {})
        assert result.department_id == "hr"
        assert result.status == "success"
        assert "hr_type" in result.output
        assert result.output["hr_type"] == "recruitment"

    @pytest.mark.asyncio
    async def test_finance_executor(self):
        """测试财务部执行器。"""
        from app.engine.collaboration import FinanceAgentExecutor
        executor = FinanceAgentExecutor()
        result = await executor.execute("制定预算", {})
        assert result.department_id == "finance"
        assert result.status == "success"
        assert "finance_type" in result.output
        assert result.output["finance_type"] == "budget_cost"

    @pytest.mark.asyncio
    async def test_product_executor(self):
        """测试产品部执行器。"""
        from app.engine.collaboration import ProductAgentExecutor
        executor = ProductAgentExecutor()
        result = await executor.execute("撰写PRD", {})
        assert result.department_id == "product"
        assert result.status == "success"
        assert "product_type" in result.output

    @pytest.mark.asyncio
    async def test_engineering_executor(self):
        """测试技术部执行器。"""
        from app.engine.collaboration import EngineeringAgentExecutor
        executor = EngineeringAgentExecutor()
        result = await executor.execute("设计架构", {})
        assert result.department_id == "engineering"
        assert result.status == "success"
        assert "engineering_type" in result.output

    @pytest.mark.asyncio
    async def test_ceo_executor(self):
        """测试CEO执行器（协调器）。"""
        from app.engine.collaboration import CEOAgentExecutor
        executor = CEOAgentExecutor()
        result = await executor.execute("测试任务", {})
        assert result.department_id == "ceo"
        assert result.status == "success"
        assert "ceo_role" in result.output
        assert result.output["ceo_role"] == "协调决策"
        assert "primary_department" in result.output


class TestCollaborationEngine:
    """测试协作引擎核心功能。"""

    def test_engine_initialization(self):
        """测试引擎初始化。"""
        engine = CollaborationEngine()
        assert engine.router is not None
        assert isinstance(engine.active_tasks, dict)

    @pytest.mark.asyncio
    async def test_single_department_execution(self):
        """测试单部门执行。"""
        engine = CollaborationEngine()
        result = await engine.execute_with_real_agents("帮我写个小红书文案")
        assert "collaboration_summary" in result
        assert "primary_department" in result
        # "文案"关键词路由到运营部（内容运营），符合预期
        assert result["primary_department"] == "operations"

    @pytest.mark.asyncio
    async def test_multi_department_collaboration(self):
        """测试多部门协作。"""
        engine = CollaborationEngine()
        result = await engine.execute_with_real_agents("制定年度预算并执行市场推广")
        chain = result.get("execution_chain", [])
        assert len(chain) >= 1
        # 验证 handoff 链路
        for step in chain:
            assert "department" in step
            assert "output" in step

    def test_plan_collaboration(self):
        """测试协作规划。"""
        engine = CollaborationEngine()
        task = engine.plan_collaboration("制定产品战略")
        assert task.status == TaskStatus.PENDING
        assert task.primary_department is not None


class TestExecutionResult:
    """测试执行结果格式。"""

    def test_result_to_dict(self):
        """测试结果序列化。"""
        result = ExecutionResult(
            department_id="test",
            output={"key": "value"},
            status="success",
            metrics={"score": 0.9},
        )
        d = result.to_dict()
        assert d["department_id"] == "test"
        assert d["output"]["key"] == "value"
        assert d["status"] == "success"


class TestHandoffRecord:
    """测试Handoff记录。"""

    def test_handoff_creation(self):
        """测试Handoff创建。"""
        from app.engine.collaboration import HandoffRecord
        from datetime import datetime

        handoff = HandoffRecord(
            handoff_id="test-001",
            task_id="task-001",
            from_department="marketing",
            to_department="operations",
            status=HandoffStatus.PENDING,
            context={},
        )
        assert handoff.handoff_id == "test-001"
        assert handoff.status == HandoffStatus.PENDING


class TestExecutorRegistry:
    """测试执行器注册表。"""

    def test_all_departments_registered(self):
        """测试所有部门已注册。"""
        expected = {
            "marketing",
            "operations",
            "design",
            "hr",
            "finance",
            "product",
            "engineering",
            "ceo",
        }
        assert set(DEPARTMENT_EXECUTORS.keys()) == expected

    def test_all_real_executors(self):
        """测试所有部门使用真实执行器（非占位符）。"""
        for dept, executor_cls in DEPARTMENT_EXECUTORS.items():
            assert executor_cls != AgentExecutor, f"{dept} 仍使用占位符 AgentExecutor"


@pytest.mark.parametrize("task,expected_dept", [
    ("帮我写个小红书文案", "operations"),  # "文案"关键词路由到运营部
    ("用户增长活动策划", "operations"),
    ("设计App UI", "design"),
    ("招聘工程师", "hr"),
    ("制定预算", "finance"),
    ("撰写PRD", "product"),
    ("设计架构", "engineering"),
])
@pytest.mark.asyncio
async def test_end_to_end_routing(task, expected_dept):
    """端到端路由测试。"""
    engine = CollaborationEngine()
    result = await engine.execute_with_real_agents(task)
    assert result["primary_department"] == expected_dept
