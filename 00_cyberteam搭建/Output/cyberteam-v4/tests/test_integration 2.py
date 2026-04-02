"""
CyberTeam V4 集成测试套件

覆盖：
- ModelGateway + ToolFactory 集成
- TaskScheduler + ExpertAgentRegistry 集成
- ApprovalGate + TaskScheduler 集成（高危任务触发审批）
- StreamSessionManager 模拟测试

运行方式:
    python -m pytest tests/test_integration.py -v
    python -m pytest tests/test_integration.py::TestModelGatewayToolFactory -v
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.engine.model_gateway import ModelGateway, model_gateway
from backend.app.models.expert_agent import ExpertAgentRegistry, ExpertAgentProfile
from backend.app.engine.task_scheduler import TaskScheduler, TaskSchedulerDomainService
from backend.app.engine.task_types import TaskStatus, TaskType
from backend.app.engine.approval_gate import (
    ApprovalGate, ApprovalLevel, ApprovalStatus, get_approval_gate
)


# =============================================================================
# ToolFactory 模拟（用于 ModelGateway 集成测试）
# =============================================================================

class MockTool:
    """模拟工具"""
    def __init__(self, name: str, provider: str = "mock"):
        self.name = name
        self.provider = provider

    async def execute(self, **kwargs):
        return {"result": f"executed {self.name}", **kwargs}


class ToolFactory:
    """
    工具工厂（模拟实现）

    实际项目中应从 backend/app/engine/tool_factory.py 导入
    这里提供模拟实现用于集成测试
    """
    _instance: Optional['ToolFactory'] = None

    def __init__(self):
        self._tools: dict[str, MockTool] = {}

    @classmethod
    def get_instance(cls) -> 'ToolFactory':
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._seed_defaults()
        return cls._instance

    def _seed_defaults(self):
        """预置默认工具"""
        defaults = [
            MockTool("web_search", "search_provider"),
            MockTool("code_execute", "code_provider"),
            MockTool("image_gen", "image_provider"),
            MockTool("file_operate", "fs_provider"),
        ]
        for tool in defaults:
            self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[MockTool]:
        return self._tools.get(name)

    def register_tool(self, tool: MockTool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


# =============================================================================
# StreamSessionManager 模拟（用于流式会话管理测试）
# =============================================================================

class StreamEvent:
    """流式事件"""
    def __init__(self, event_type: str, data: dict):
        self.event_type = event_type
        self.data = data


class StreamSession:
    """流式会话"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events: list[StreamEvent] = []
        self._closed = False

    def emit(self, event_type: str, data: dict) -> None:
        if self._closed:
            raise RuntimeError("Session closed")
        self.events.append(StreamEvent(event_type, data))

    async def close(self) -> None:
        self._closed = True


class StreamSessionManager:
    """
    流式会话管理器（模拟实现）

    实际项目中应从 backend/app/engine/stream_session_manager.py 导入
    这里提供模拟实现用于集成测试
    """
    _instance: Optional['StreamSessionManager'] = None

    def __init__(self):
        self._sessions: dict[str, StreamSession] = {}

    @classmethod
    def get_instance(cls) -> 'StreamSessionManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_session(self, session_id: str) -> StreamSession:
        if session_id in self._sessions:
            raise ValueError(f"Session {session_id} already exists")
        session = StreamSession(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[StreamSession]:
        return self._sessions.get(session_id)

    def close_session(self, session_id: str) -> bool:
        session = self._sessions.pop(session_id, None)
        if session:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(session.close())
            except RuntimeError:
                # No running event loop, close synchronously
                session._closed = True
            return True
        return False

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())


# =============================================================================
# 集成测试类
# =============================================================================

class TestModelGatewayToolFactory:
    """ModelGateway + ToolFactory 集成测试"""

    def setup_method(self):
        """每个测试方法前重置单例"""
        self.gateway = ModelGateway()
        self.factory = ToolFactory.get_instance()

    def test_model_resolve_for_execution(self):
        """测试执行层任务模型解析"""
        model = self.gateway.resolve("dept_execution")
        assert model == "claude-haiku-4-5"

    def test_model_resolve_for_decision(self):
        """测试决策层任务模型解析"""
        model = self.gateway.resolve("ceo_route")
        assert model == "claude-opus-4-6"

    def test_model_resolve_economy_mode(self):
        """测试经济模式模型降级"""
        model = self.gateway.resolve("ceo_route", budget_tier="economy")
        assert model == "claude-sonnet-4-6"

    def test_tool_factory_registration(self):
        """测试工具工厂工具注册"""
        new_tool = MockTool("custom_tool", "custom_provider")
        self.factory.register_tool(new_tool)
        retrieved = self.factory.get_tool("custom_tool")
        assert retrieved is not None
        assert retrieved.name == "custom_tool"
        assert retrieved.provider == "custom_provider"

    def test_tool_execution_integration(self):
        """测试工具执行集成"""
        tool = self.factory.get_tool("web_search")
        assert tool is not None
        # 验证工具可以执行（同步模拟）
        result = asyncio.get_event_loop().run_until_complete(
            tool.execute(query="test query")
        )
        assert "result" in result
        assert result["query"] == "test query"

    def test_gateway_with_custom_mapping(self):
        """测试自定义模型映射"""
        self.gateway.set_custom("dept_execution", "claude-opus-4-6", "normal")
        model = self.gateway.resolve("dept_execution")
        assert model == "claude-opus-4-6"

    def test_gateway_default_fallback(self):
        """测试默认模型回退"""
        model = self.gateway.resolve("unknown_task_type")
        assert model == self.gateway.DEFAULT_MODEL


class TestTaskSchedulerExpertRegistry:
    """TaskScheduler + ExpertAgentRegistry 集成测试"""

    def setup_method(self):
        """每个测试方法前重置"""
        self.scheduler_service = TaskSchedulerDomainService()
        self.registry = ExpertAgentRegistry.get_instance()

    @pytest.mark.asyncio
    async def test_task_creates_expert_call(self):
        """测试任务调度触发专家调用"""
        # 注册一个异步回调
        async def mock_expert_task(params: dict) -> str:
            expert_id = params.get("expert_id", "ops-expert-01")
            # 模拟专家执行
            await asyncio.sleep(0.01)
            self.registry.record_call(expert_id, 150.0)
            return f"Expert {expert_id} completed"

        # 创建任务
        task_id = await self.scheduler_service.create_task(
            name="测试专家任务",
            callback=mock_expert_task,
            params={"expert_id": "ops-expert-01"},
        )

        # 等待任务完成
        await asyncio.sleep(0.1)

        # 验证任务状态
        task = self.scheduler_service.get_task(task_id)
        assert task is not None
        assert task.status == TaskStatus.SUCCESS

        # 验证专家调用记录
        expert = self.registry.get("ops-expert-01")
        assert expert is not None
        assert expert.call_count >= 1

    @pytest.mark.asyncio
    async def test_expert_discovery_after_task(self):
        """测试任务后专家发现"""
        # 先调用一次专家
        async def mock_task(params: dict) -> str:
            await asyncio.sleep(0.01)
            self.registry.record_call("marketing-expert-01", 200.0)
            return "done"

        await self.scheduler_service.create_task(
            name="营销任务",
            callback=mock_task,
            params={}
        )
        await asyncio.sleep(0.1)

        # 验证专家按调用次数排序
        market = self.registry.get_market()
        assert len(market) > 0
        # 验证 marketing-expert-01 在列表中
        expert_ids = [a.agent_id for a in market]
        assert "marketing-expert-01" in expert_ids

    @pytest.mark.asyncio
    async def test_task_with_department_filter(self):
        """测试部门筛选任务"""
        async def mock_task(params: dict) -> str:
            await asyncio.sleep(0.01)
            return "done"

        # 创建多个部门的任务
        await self.scheduler_service.create_task(
            name="运营任务",
            callback=mock_task,
            params={}
        )
        await asyncio.sleep(0.05)

        # 验证市场筛选
        ops_market = self.registry.get_market(department="运营部")
        assert all(a.department == "运营部" for a in ops_market)

    @pytest.mark.asyncio
    async def test_expert_discover_keywords(self):
        """测试专家关键词发现"""
        # 发现运营专家
        results = self.registry.discover("运营 增长")
        assert len(results) > 0
        # 第一个结果应该是评分最高的
        if len(results) > 1:
            assert results[0].rating >= results[1].rating


class TestApprovalGateTaskScheduler:
    """ApprovalGate + TaskScheduler 集成测试 - 高危任务触发审批"""

    def setup_method(self):
        """每个测试方法前重置"""
        self.approval_gate = get_approval_gate()
        self.scheduler_service = TaskSchedulerDomainService()

    @pytest.mark.asyncio
    async def test_high_risk_task_triggers_approval(self):
        """测试高危任务触发审批"""
        # 模拟高危操作
        action = "EXECUTE_SQL"
        context = {"sql": "DROP TABLE users", "requester": "test_user"}

        # 请求审批
        approval_req = await self.approval_gate.request_approval(
            action=action,
            context=context,
            requester="test_user"
        )

        # 验证需要 CEO 审批
        assert approval_req.level == ApprovalLevel.HIGH
        assert approval_req.status == ApprovalStatus.PENDING

    @pytest.mark.asyncio
    async def test_auto_approval_low_risk_task(self):
        """测试低风险任务自动通过"""
        action = "READ_DATA"
        context = {"resource": "report"}

        approval_req = await self.approval_gate.request_approval(
            action=action,
            context=context,
            requester="test_user"
        )

        # 低风险操作应该自动通过
        assert approval_req.level == ApprovalLevel.AUTO
        assert approval_req.status == ApprovalStatus.APPROVED

    @pytest.mark.asyncio
    async def test_scheduled_task_with_approval(self):
        """测试需要审批的调度任务"""
        # 先请求审批
        action = "DEPLOY_PRODUCTION"
        context = {"env": "production", "version": "1.0"}

        approval_req = await self.approval_gate.request_approval(
            action=action,
            context=context,
            requester="deployer"
        )

        # 审批级别应为 MEDIUM (COO)
        assert approval_req.level == ApprovalLevel.MEDIUM

        # 手动审批通过
        approved = await self.approval_gate.approve(approval_req.approval_id, "COO")
        assert approved is True

        # 验证状态更新
        pending = self.approval_gate.get_pending()
        approval_ids = [r.approval_id for r in pending]
        assert approval_req.approval_id not in approval_ids

    @pytest.mark.asyncio
    async def test_reject_blocks_execution(self):
        """测试拒绝阻止执行"""
        action = "DELETE_PROJECT"
        context = {"project_id": "proj-123"}

        approval_req = await self.approval_gate.request_approval(
            action=action,
            context=context,
            requester="test_user"
        )

        assert approval_req.level == ApprovalLevel.HIGH

        # 拒绝审批
        rejected = await self.approval_gate.reject(
            approval_req.approval_id,
            "CEO",
            "风险太高"
        )
        assert rejected is True

        # 验证被拒绝
        history = self.approval_gate.get_history()
        recent = [r for r in history if r.approval_id == approval_req.approval_id]
        assert len(recent) > 0
        assert recent[0].status == ApprovalStatus.REJECTED

    @pytest.mark.asyncio
    async def test_bypass_for_emergency(self):
        """测试紧急情况 Bypass"""
        action = "MODIFY_BUDGET"
        context = {"amount": 1000000}

        approval_req = await self.approval_gate.request_approval(
            action=action,
            context=context,
            requester="cfo"
        )

        assert approval_req.level == ApprovalLevel.HIGH

        # CEO bypass
        bypassed = await self.approval_gate.bypass(
            approval_req.approval_id,
            "CEO",
            "紧急情况，立即执行"
        )
        assert bypassed is True

        # 验证 bypass 状态
        history = self.approval_gate.get_history()
        recent = [r for r in history if r.approval_id == approval_req.approval_id]
        assert len(recent) > 0
        assert recent[0].status == ApprovalStatus.BYPASSED

    @pytest.mark.asyncio
    async def test_approval_gate_blocks_action(self):
        """测试审批门控阻止未批准操作"""
        action = "DELETE_PROJECT"
        context = {"project_id": "test"}

        # 未审批的操作应该被阻止
        assert self.approval_gate.is_action_blocked(action) is False

        # 请求审批（但不批准）
        await self.approval_gate.request_approval(action, context)

        # 现在应该被阻止
        assert self.approval_gate.is_action_blocked(action) is True

    @pytest.mark.asyncio
    async def test_approval_rule_registration(self):
        """测试自定义审批规则注册"""
        new_rule_action = "CUSTOM_DANGER"
        self.approval_gate.register_rule(
            new_rule_action,
            ApprovalLevel.MEDIUM,
            "自定义高危操作"
        )

        level = self.approval_gate.get_required_level(new_rule_action)
        assert level == ApprovalLevel.MEDIUM


class TestStreamSessionManager:
    """StreamSessionManager 模拟测试"""

    def setup_method(self):
        """每个测试方法前重置"""
        StreamSessionManager._instance = None
        self.manager = StreamSessionManager.get_instance()

    def test_create_session(self):
        """测试创建流式会话"""
        session = self.manager.create_session("session-001")
        assert session is not None
        assert session.session_id == "session-001"
        assert len(session.events) == 0

    def test_get_session(self):
        """测试获取会话"""
        self.manager.create_session("session-002")
        session = self.manager.get_session("session-002")
        assert session is not None
        assert session.session_id == "session-002"

    def test_get_nonexistent_session(self):
        """测试获取不存在的会话"""
        session = self.manager.get_session("nonexistent")
        assert session is None

    def test_emit_event(self):
        """测试发送流式事件"""
        session = self.manager.create_session("session-003")
        session.emit("message", {"content": "Hello"})
        session.emit("done", {"status": "completed"})

        assert len(session.events) == 2
        assert session.events[0].event_type == "message"
        assert session.events[1].data["status"] == "completed"

    def test_close_session(self):
        """测试关闭会话"""
        self.manager.create_session("session-004")
        closed = self.manager.close_session("session-004")
        assert closed is True
        assert self.manager.get_session("session-004") is None

    def test_list_sessions(self):
        """测试列出所有会话"""
        self.manager.create_session("s1")
        self.manager.create_session("s2")
        self.manager.create_session("s3")

        sessions = self.manager.list_sessions()
        assert len(sessions) == 3
        assert "s1" in sessions
        assert "s2" in sessions
        assert "s3" in sessions

    def test_duplicate_session_id_raises(self):
        """测试重复会话ID报错"""
        self.manager.create_session("dup-session")
        with pytest.raises(ValueError):
            self.manager.create_session("dup-session")


class TestFullIntegration:
    """完整集成测试 - 跨模块流程"""

    def setup_method(self):
        """重置所有单例"""
        ModelGateway.__instance = None
        ExpertAgentRegistry._instance = None
        ToolFactory._instance = None
        StreamSessionManager._instance = None

    @pytest.mark.asyncio
    async def test_model_selection_then_expert_invocation(self):
        """测试模型选择 -> 专家调用的完整流程"""
        # 1. ModelGateway 选择模型
        gateway = ModelGateway()
        model = gateway.resolve("marketing")
        assert model == "claude-sonnet-4-6"

        # 2. 获取专家
        registry = ExpertAgentRegistry.get_instance()
        experts = registry.discover("营销")
        assert len(experts) > 0

        # 3. 创建调度任务
        scheduler = TaskSchedulerDomainService()

        async def marketing_task(params: dict) -> str:
            expert_id = params["expert_id"]
            registry.record_call(expert_id, 180.0)
            return f"Marketing task done by {expert_id}"

        task_id = await scheduler.create_task(
            name="营销分析",
            callback=marketing_task,
            params={"expert_id": experts[0].agent_id}
        )

        await asyncio.sleep(0.1)

        # 4. 验证结果
        task = scheduler.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS

        # 5. 验证专家调用统计
        updated_expert = registry.get(experts[0].agent_id)
        assert updated_expert.call_count >= 1

    @pytest.mark.asyncio
    async def test_approval_then_execution_flow(self):
        """测试审批 -> 执行的完整流程"""
        gate = get_approval_gate()
        scheduler = TaskSchedulerDomainService()

        # 1. 请求高危操作审批
        approval = await gate.request_approval(
            action="DEPLOY_PRODUCTION",
            context={"env": "prod", "version": "2.0"},
            requester="dev lead"
        )
        approval_id = approval.approval_id

        # 2. 审批通过
        await gate.approve(approval_id, "COO")

        # 3. 创建调度任务
        async def deploy_task(params: dict) -> str:
            return f"Deployed to {params['env']}"

        task_id = await scheduler.create_task(
            name="生产部署",
            callback=deploy_task,
            params={"env": "production"}
        )

        await asyncio.sleep(0.1)

        # 4. 验证任务完成
        task = scheduler.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS
        assert task.result.success is True

    @pytest.mark.asyncio
    async def test_stream_with_expert_execution(self):
        """测试流式会话与专家执行集成"""
        manager = StreamSessionManager.get_instance()
        registry = ExpertAgentRegistry.get_instance()

        # 1. 创建流式会话
        session = manager.create_session("stream-001")

        # 2. 模拟专家执行并发送流式事件
        expert = registry.get("ops-expert-01")
        session.emit("expert_selected", {
            "expert_id": expert.agent_id,
            "expert_name": expert.name
        })

        async def long_running_task(params: dict) -> str:
            session_id = params["session_id"]
            s = manager.get_session(session_id)
            s.emit("progress", {"percent": 50})
            await asyncio.sleep(0.01)
            s.emit("progress", {"percent": 100})
            s.emit("complete", {"result": "success"})
            return "Done"

        scheduler = TaskSchedulerDomainService()
        task_id = await scheduler.create_task(
            name="流式任务",
            callback=long_running_task,
            params={"session_id": "stream-001"}
        )

        await asyncio.sleep(0.15)

        # 3. 验证流式事件
        assert len(session.events) >= 3

        # 4. 验证任务状态
        task = scheduler.get_task(task_id)
        assert task.status == TaskStatus.SUCCESS


# =============================================================================
# 运行入口
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])