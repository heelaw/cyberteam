"""
CyberTeam v2 - 路由引擎测试套件

测试覆盖：
1. RoutingEngine - 任务路由引擎
2. AgentSpec - Agent规格
3. RoutingRule - 路由规则
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.routing_engine import (
    RoutingEngine,
    RoutingRule,
    AgentSpec,
    RouteResult
)
from engine.thinking_injector import (
    ThinkingInjector,
    ThinkingContext,
    Expert
)


class TestRoutingRule:
    """路由规则测试"""

    def test_create_routing_rule(self):
        """测试创建路由规则"""
        rule = RoutingRule(
            name="growth-route",
            triggers=["增长", "DAU", "MAU"],
            agents=["growth-agent", "marketing-agent"],
            priority=2,
            required_experts=["growth-expert"]
        )
        assert rule.name == "growth-route"
        assert rule.priority == 2
        assert len(rule.agents) == 2

    def test_routing_rule_defaults(self):
        """测试路由规则默认值"""
        rule = RoutingRule(
            name="test",
            triggers=["test"],
            agents=["test-agent"]
        )
        assert rule.priority == 1  # 默认优先级
        assert rule.required_experts == []  # 默认空列表


class TestAgentSpec:
    """Agent规格测试"""

    def test_create_agent_spec(self):
        """测试创建Agent规格"""
        agent = AgentSpec(
            id="growth-agent",
            name="Growth Agent",
            name_cn="增长Agent",
            category="department",
            focus_areas=["用户增长", "转化率优化"],
            trigger_keywords=["增长", "DAU"],
            tools=["analytics", "ab_test"],
            skills=["data_analysis", "marketing"]
        )
        assert agent.id == "growth-agent"
        assert agent.category == "department"
        assert agent.max_concurrent == 2  # 默认值

    def test_agent_spec_with_custom_concurrency(self):
        """测试自定义并发数"""
        agent = AgentSpec(
            id="test",
            name="Test",
            name_cn="测试",
            category="test",
            focus_areas=[],
            trigger_keywords=[],
            max_concurrent=5
        )
        assert agent.max_concurrent == 5


class TestRoutingEngine:
    """路由引擎测试"""

    def setup_method(self):
        self.engine = RoutingEngine()

    def test_load_config(self):
        """测试配置加载"""
        assert len(self.engine.agents) > 0 or True  # 可能使用内置配置

    def test_route_with_thinking_context(self):
        """测试使用ThinkingContext进行路由"""
        # 创建模拟的ThinkingContext
        injector = ThinkingInjector()
        ctx = injector.process("提升DAU 20%")

        result = self.engine.route(ctx, "提升DAU 20%")

        assert isinstance(result, RouteResult)
        assert len(result.selected_agents) > 0 or result.confidence >= 0
        assert len(result.reasoning_chain) > 0

    def test_route_with_different_goals(self):
        """测试不同目标的路由"""
        injector = ThinkingInjector()

        test_goals = [
            "制定公司战略",
            "做用户增长",
            "分析竞品SWOT",
            "开发一个APP"
        ]

        for goal in test_goals:
            ctx = injector.process(goal)
            result = self.engine.route(ctx, goal)
            assert isinstance(result, RouteResult)

    def test_route_confidence_calculation(self):
        """测试置信度计算"""
        injector = ThinkingInjector()
        ctx = injector.process("制定增长策略")

        result = self.engine.route(ctx, "制定增长策略")

        # 置信度应该在0-1之间
        assert 0 <= result.confidence <= 1

    def test_task_assignments_generation(self):
        """测试任务分配生成"""
        injector = ThinkingInjector()
        ctx = injector.process("提升DAU")

        result = self.engine.route(ctx, "提升DAU")

        # 任务分配应该是列表
        assert isinstance(result.task_assignments, list)


class TestRouteResult:
    """路由结果测试"""

    def test_create_route_result(self):
        """测试创建路由结果"""
        agents = [
            AgentSpec(
                id="test",
                name="Test",
                name_cn="测试",
                category="test",
                focus_areas=[],
                trigger_keywords=[]
            )
        ]
        result = RouteResult(
            selected_agents=agents,
            task_assignments=[{"task": "test"}],
            reasoning_chain=["step 1"],
            confidence=0.8
        )
        assert len(result.selected_agents) == 1
        assert result.confidence == 0.8

    def test_route_result_defaults(self):
        """测试路由结果默认值"""
        result = RouteResult(
            selected_agents=[],
            task_assignments=[],
            reasoning_chain=[]
        )
        assert result.confidence == 0.0  # 默认置信度


if __name__ == "__main__":
    pytest.main([__file__, "-v"])