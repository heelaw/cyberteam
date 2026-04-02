"""ExpertAgentRegistry 测试套件

覆盖：
- 预置专家验证
- 注册/获取/发现/市场/统计更新
- 关键词搜索评分
- 部门筛选
- 调用记录
"""

import pytest
import sys
from pathlib import Path

# 确保 backend/app/models 在 path 中
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.models.expert_agent import (
    ExpertAgentProfile,
    ExpertAgentRegistry,
)


class TestPresetExperts:
    """测试预置专家"""

    def test_singleton_instance(self):
        """单例模式验证"""
        registry1 = ExpertAgentRegistry.get_instance()
        registry2 = ExpertAgentRegistry.get_instance()
        assert registry1 is registry2, "单例模式失效"

    def test_preset_experts_count(self):
        """预置 4 个默认专家"""
        registry = ExpertAgentRegistry.get_instance()
        assert len(registry._agents) == 4, f"预期 4 个预置专家，实际 {len(registry._agents)}"

    def test_preset_expert_ids(self):
        """验证预置专家 ID"""
        registry = ExpertAgentRegistry.get_instance()
        expected_ids = {
            "ops-expert-01",
            "design-expert-01",
            "eng-expert-01",
            "marketing-expert-01",
        }
        actual_ids = set(registry._agents.keys())
        assert expected_ids == actual_ids, f"ID 不匹配: {actual_ids}"

    def test_preset_expert_departments(self):
        """验证预置专家部门"""
        registry = ExpertAgentRegistry.get_instance()
        departments = {agent.department for agent in registry._agents.values()}
        expected = {"运营部", "设计部", "开发部", "市场部"}
        assert departments == expected, f"部门不匹配: {departments}"


class TestRegisterAndGet:
    """测试注册和获取"""

    def test_register_new_expert(self):
        """注册新专家"""
        # 创建新实例避免影响其他测试
        registry = ExpertAgentRegistry()
        profile = ExpertAgentProfile(
            agent_id="test-expert-001",
            name="测试专家",
            department="测试部",
            description="用于测试的专家",
            capabilities=["测试能力"],
            keywords=["测试"],
        )
        agent_id = registry.register(profile)
        assert agent_id == "test-expert-001"
        assert registry.get("test-expert-001") is not None

    def test_register_duplicate_id(self):
        """重复 ID 注册应覆盖"""
        registry = ExpertAgentRegistry()
        profile1 = ExpertAgentProfile(
            agent_id="dup-test",
            name="专家1",
            department="测试部",
        )
        profile2 = ExpertAgentProfile(
            agent_id="dup-test",
            name="专家2",
            department="测试部",
        )
        registry.register(profile1)
        registry.register(profile2)
        assert registry.get("dup-test").name == "专家2"

    def test_get_existing_agent(self):
        """获取存在的专家"""
        registry = ExpertAgentRegistry.get_instance()
        agent = registry.get("ops-expert-01")
        assert agent is not None
        assert agent.name == "运营总监"

    def test_get_nonexistent_agent(self):
        """获取不存在的专家返回 None"""
        registry = ExpertAgentRegistry()
        agent = registry.get("non-existent-id")
        assert agent is None


class TestDiscover:
    """测试发现/搜索功能"""

    def test_discover_by_keyword(self):
        """通过关键词发现专家"""
        registry = ExpertAgentRegistry.get_instance()
        results = registry.discover("运营")
        assert len(results) > 0, "搜索'运营'应返回结果"
        assert any(a.name == "运营总监" for a in results)

    def test_discover_by_capability(self):
        """通过能力发现专家"""
        registry = ExpertAgentRegistry.get_instance()
        results = registry.discover("活动策划")
        assert len(results) > 0, "搜索'活动策划'应返回结果"

    def test_discover_with_department_filter(self):
        """带部门筛选的发现"""
        registry = ExpertAgentRegistry.get_instance()
        results = registry.discover("设计", department="设计部")
        assert all(a.department == "设计部" for a in results)

    def test_discover_no_results(self):
        """无结果搜索"""
        registry = ExpertAgentRegistry()
        results = registry.discover("完全不存在的关键词xyz123")
        assert len(results) == 0

    def test_discover_ranking_by_score(self):
        """发现结果按评分排序"""
        registry = ExpertAgentRegistry.get_instance()
        # 搜索包含多个专家的关键词
        results = registry.discover("总监")
        if len(results) > 1:
            # 评分高的应该在前面
            for i in range(len(results) - 1):
                assert results[i].rating >= results[i + 1].rating


class TestMarket:
    """测试数字员工市场"""

    def test_get_market_all_agents(self):
        """获取全部市场列表"""
        registry = ExpertAgentRegistry.get_instance()
        market = registry.get_market()
        assert len(market) >= 4, "市场应包含至少 4 个预置专家"

    def test_get_market_by_department(self):
        """按部门筛选市场"""
        registry = ExpertAgentRegistry.get_instance()
        market = registry.get_market(department="运营部")
        assert all(a.department == "运营部" for a in market)

    def test_market_sorted_by_call_count(self):
        """市场按调用次数降序排列"""
        registry = ExpertAgentRegistry.get_instance()
        market = registry.get_market()
        call_counts = [a.call_count for a in market]
        assert call_counts == sorted(call_counts, reverse=True)


class TestRecordCall:
    """测试调用记录"""

    def test_record_call_updates_count(self):
        """记录调用增加计数"""
        registry = ExpertAgentRegistry()
        profile = ExpertAgentProfile(
            agent_id="counter-test",
            name="计数器测试",
            department="测试部",
        )
        registry.register(profile)
        assert registry.get("counter-test").call_count == 0

        registry.record_call("counter-test", 100.0)
        assert registry.get("counter-test").call_count == 1

        registry.record_call("counter-test", 200.0)
        assert registry.get("counter-test").call_count == 2

    def test_record_call_updates_avg_time(self):
        """记录调用更新平均响应时间"""
        registry = ExpertAgentRegistry()
        profile = ExpertAgentProfile(
            agent_id="time-test",
            name="时间测试",
            department="测试部",
        )
        registry.register(profile)

        registry.record_call("time-test", 100.0)
        assert registry.get("time-test").avg_response_time_ms == 100.0

        registry.record_call("time-test", 200.0)
        # (100 + 200) / 2 = 150
        assert registry.get("time-test").avg_response_time_ms == 150.0

    def test_record_call_nonexistent(self):
        """记录不存在的专家调用应静默失败"""
        registry = ExpertAgentRegistry()
        # 不应抛出异常
        registry.record_call("non-existent", 100.0)


class TestUnregister:
    """测试注销功能"""

    def test_unregister_existing(self):
        """注销存在的专家"""
        registry = ExpertAgentRegistry()
        profile = ExpertAgentProfile(
            agent_id="unregister-test",
            name="注销测试",
            department="测试部",
        )
        registry.register(profile)
        assert registry.get("unregister-test") is not None

        success = registry.unregister("unregister-test")
        assert success is True
        assert registry.get("unregister-test") is None

    def test_unregister_nonexistent(self):
        """注销不存在的专家返回 False"""
        registry = ExpertAgentRegistry()
        success = registry.unregister("non-existent-id")
        assert success is False


class TestProfileModel:
    """测试 Profile 模型"""

    def test_profile_defaults(self):
        """测试默认值"""
        profile = ExpertAgentProfile(
            agent_id="defaults-test",
            name="默认测试",
            department="测试部",
        )
        assert profile.description == ""
        assert profile.capabilities == []
        assert profile.keywords == []
        assert profile.avatar == "🤖"
        assert profile.rating == 5.0
        assert profile.call_count == 0
        assert profile.avg_response_time_ms == 0
        assert profile.status == "online"

    def test_profile_rating_bounds(self):
        """评分边界验证"""
        profile = ExpertAgentProfile(
            agent_id="rating-test",
            name="评分测试",
            department="测试部",
            rating=5.0,
        )
        assert profile.rating == 5.0

        # Pydantic 会验证 ge=0, le=5
        with pytest.raises(Exception):
            ExpertAgentProfile(
                agent_id="rating-test2",
                name="评分测试2",
                department="测试部",
                rating=6.0,
            )