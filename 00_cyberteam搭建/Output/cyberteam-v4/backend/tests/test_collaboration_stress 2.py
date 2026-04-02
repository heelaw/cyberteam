"""协作引擎压力测试 - 验证高并发和极限情况下的稳定性。

测试场景：
1. 基础并发测试 - 多任务同时路由
2. 大量任务压力测试 - 100+ 并发任务
3. 边界条件测试 - 空任务、极长任务、特殊字符
4. 连续执行稳定性测试 - 1000次连续执行
5. 内存稳定性测试 - 大量任务执行后内存是否正常
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
import time
import tracemalloc
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.engine.collaboration import CollaborationEngine, CEORouter, DEPARTMENT_EXECUTORS
from app.engine.department_registry import DepartmentRegistry, reset_department_registry


# ═══════════════════════════════════════════════════════════════════════════════
# 压力测试配置
# ═══════════════════════════════════════════════════════════════════════════════

# 测试任务样本
SAMPLE_TASKS = [
    "帮我写个小红书推广方案",
    "招聘高级工程师",
    "制定下季度预算",
    "设计微服务架构",
    "撰写PRD产品需求文档",
    "用户增长活动策划",
    "设计App UI界面",
    "制定品牌营销策略",
    "数据分析报告",
    "团队绩效考核",
]

# 边界测试用例
EDGE_CASE_TASKS = [
    "",  # 空任务
    "a",  # 最短任务
    "a" * 1000,  # 极长任务
    "!@#$%^&*()",  # 特殊字符
    "帮我" + "a" * 500,  # 混合长度
    "设计" * 100,  # 重复关键词
    "🎉" * 50,  # emoji
]


# ═══════════════════════════════════════════════════════════════════════════════
# 基础并发测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestConcurrency:
    """基础并发测试。"""

    @pytest.mark.asyncio
    async def test_concurrent_routing_10_tasks(self):
        """测试10个任务并发路由。"""
        router = CEORouter()
        start_time = time.time()

        tasks = [f"测试任务{i}" for i in range(10)]
        results = await asyncio.gather(*[asyncio.to_thread(router.route, task) for task in tasks])

        elapsed = time.time() - start_time

        assert len(results) == 10
        assert all(r.get("target_department") for r in results)
        print(f"\n⏱ 10个并发路由耗时: {elapsed:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_routing_50_tasks(self):
        """测试50个任务并发路由。"""
        router = CEORouter()
        start_time = time.time()

        tasks = [f"测试任务{i}" for i in range(50)]
        results = await asyncio.gather(*[asyncio.to_thread(router.route, task) for task in tasks])

        elapsed = time.time() - start_time

        assert len(results) == 50
        assert all(r.get("target_department") for r in results)
        print(f"\n⏱ 50个并发路由耗时: {elapsed:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_routing_100_tasks(self):
        """测试100个任务并发路由。"""
        router = CEORouter()
        start_time = time.time()

        tasks = [f"测试任务{i}" for i in range(100)]
        results = await asyncio.gather(*[asyncio.to_thread(router.route, task) for task in tasks])

        elapsed = time.time() - start_time

        assert len(results) == 100
        assert all(r.get("target_department") for r in results)
        print(f"\n⏱ 100个并发路由耗时: {elapsed:.3f}s")


# ═══════════════════════════════════════════════════════════════════════════════
# 大量任务压力测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestHighLoad:
    """高负载压力测试。"""

    @pytest.mark.asyncio
    async def test_routing_200_tasks(self):
        """测试200个任务路由性能。"""
        router = CEORouter()
        start_time = time.time()

        tasks = [SAMPLE_TASKS[i % len(SAMPLE_TASKS)] for i in range(200)]
        results = [router.route(task) for task in tasks]

        elapsed = time.time() - start_time
        avg_time = elapsed / 200

        assert len(results) == 200
        print(f"\n⏱ 200个任务路由耗时: {elapsed:.3f}s (平均 {avg_time*1000:.2f}ms/任务)")

        # 性能要求：平均 < 10ms/任务
        assert avg_time < 0.01, f"平均耗时 {avg_time*1000:.2f}ms 超过 10ms 限制"

    @pytest.mark.asyncio
    async def test_execution_50_tasks(self):
        """测试50个任务执行。"""
        engine = CollaborationEngine()
        start_time = time.time()

        tasks = [SAMPLE_TASKS[i % len(SAMPLE_TASKS)] for i in range(50)]
        results = await asyncio.gather(*[
            engine.execute_with_real_agents(task) for task in tasks
        ])

        elapsed = time.time() - start_time
        avg_time = elapsed / 50

        assert len(results) == 50
        print(f"\n⏱ 50个任务执行耗时: {elapsed:.3f}s (平均 {avg_time*1000:.2f}ms/任务)")


# ═══════════════════════════════════════════════════════════════════════════════
# 边界条件测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """边界条件测试。"""

    @pytest.mark.parametrize("task", EDGE_CASE_TASKS)
    def test_edge_case_routing(self, task):
        """测试边界条件的路由。"""
        router = CEORouter()

        # 不应该崩溃
        result = router.route(task)
        assert result is not None
        assert "target_department" in result
        assert "match_score" in result

    def test_empty_string_task(self):
        """测试空字符串任务。"""
        router = CEORouter()
        result = router.route("")
        assert result["target_department"] == "ceo"  # 空任务路由到CEO

    def test_very_long_task(self):
        """测试超长任务。"""
        router = CEORouter()
        long_task = "设计" * 1000  # 非常长的任务
        result = router.route(long_task)
        assert result["target_department"] is not None

    def test_special_characters_task(self):
        """测试特殊字符任务。"""
        router = CEORouter()
        special_task = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = router.route(special_task)
        assert result["target_department"] is not None


# ═══════════════════════════════════════════════════════════════════════════════
# 连续执行稳定性测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestStability:
    """连续执行稳定性测试。"""

    @pytest.mark.asyncio
    async def test_100_consecutive_executions(self):
        """测试100次连续执行。"""
        engine = CollaborationEngine()
        errors = []
        results = []

        start_time = time.time()

        for i in range(100):
            task = SAMPLE_TASKS[i % len(SAMPLE_TASKS)]
            try:
                result = await engine.execute_with_real_agents(task)
                results.append(result)
            except Exception as e:
                errors.append((i, str(e)))

        elapsed = time.time() - start_time

        print(f"\n⏱ 100次连续执行: {elapsed:.3f}s")
        print(f"✅ 成功: {len(results)}")
        print(f"❌ 失败: {len(errors)}")

        if errors:
            print(f"前3个错误: {errors[:3]}")

        # 成功率要求 > 95%
        success_rate = len(results) / 100
        assert success_rate > 0.95, f"成功率 {success_rate*100:.1f}% 低于 95%"

    @pytest.mark.asyncio
    async def test_500_consecutive_routing(self):
        """测试500次连续路由（不执行）。"""
        router = CEORouter()
        errors = []

        start_time = time.time()

        for i in range(500):
            task = SAMPLE_TASKS[i % len(SAMPLE_TASKS)]
            try:
                router.route(task)
            except Exception as e:
                errors.append((i, str(e)))

        elapsed = time.time() - start_time

        print(f"\n⏱ 500次连续路由: {elapsed:.3f}s")
        print(f"✅ 成功: {500 - len(errors)}")
        print(f"❌ 失败: {len(errors)}")

        # 成功率要求 > 99%
        success_rate = (500 - len(errors)) / 500
        assert success_rate > 0.99, f"成功率 {success_rate*100:.1f}% 低于 99%"


# ═══════════════════════════════════════════════════════════════════════════════
# 内存稳定性测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryStability:
    """内存稳定性测试。"""

    @pytest.mark.asyncio
    async def test_memory_after_100_executions(self):
        """测试100次执行后内存状态。"""
        engine = CollaborationEngine()

        tracemalloc.start()

        # 记录初始内存
        initial_memory = tracemalloc.get_traced_memory()[0] / 1024 / 1024  # MB

        # 执行100次任务
        for i in range(100):
            task = SAMPLE_TASKS[i % len(SAMPLE_TASKS)]
            await engine.execute_with_real_agents(task)

        # 记录最终内存
        final_memory, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        final_memory_mb = final_memory / 1024 / 1024
        peak_mb = peak / 1024 / 1024
        memory_increase_mb = final_memory_mb - initial_memory

        print(f"\n💾 初始内存: {initial_memory:.1f} MB")
        print(f"💾 最终内存: {final_memory_mb:.1f} MB")
        print(f"💾 内存峰值: {peak_mb:.1f} MB")
        print(f"💾 内存增长: {memory_increase_mb:.1f} MB")

        # 内存增长应该 < 100MB
        assert memory_increase_mb < 100, f"内存增长 {memory_increase_mb:.1f}MB 超过 100MB 限制"

    def test_tracemalloc_peak_during_routing(self):
        """测试路由过程中的内存峰值。"""
        router = CEORouter()

        tracemalloc.start()

        # 执行大量路由
        for _ in range(1000):
            router.route("测试任务")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024

        print(f"\n📈 内存峰值: {peak_mb:.2f} MB")

        # 峰值应该 < 50MB
        assert peak_mb < 50, f"内存峰值 {peak_mb:.2f}MB 超过 50MB 限制"


# ═══════════════════════════════════════════════════════════════════════════════
# 部门注册表压力测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestDepartmentRegistryStress:
    """部门注册表压力测试。"""

    def test_register_100_custom_departments(self):
        """测试注册100个自定义部门。"""
        reset_department_registry()
        registry = DepartmentRegistry()

        start_time = time.time()

        for i in range(100):
            registry.register_department(
                department_id=f"custom_dept_{i}",
                name=f"自定义部门{i}",
                description=f"测试部门{i}",
                responsibility="测试",
            )

        elapsed = time.time() - start_time

        print(f"\n⏱ 注册100个部门耗时: {elapsed:.3f}s")
        print(f"📊 当前部门总数: {len(registry.list_departments())}")

        assert len(registry.list_departments()) >= 108  # 8内置 + 100自定义

    def test_rapid_register_unregister(self):
        """测试快速注册和注销。"""
        registry = DepartmentRegistry()

        for i in range(50):
            dept_id = f"rapid_test_{i}"
            registry.register_department(
                department_id=dept_id,
                name=f"快速测试部门{i}",
                description="测试",
                responsibility="测试",
            )
            registry.unregister_department(dept_id)

        # 所有快速创建的部门应该被清理
        remaining = [d for d in registry.list_departments() if d.department_id.startswith("rapid_test_")]
        assert len(remaining) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 路由一致性测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestRoutingConsistency:
    """路由一致性测试。"""

    def test_same_task_same_result(self):
        """测试相同任务产生相同结果。"""
        router = CEORouter()
        task = "帮我写个小红书推广方案"

        results = [router.route(task) for _ in range(100)]

        # 所有结果应该相同
        first_result = results[0]["target_department"]
        assert all(r["target_department"] == first_result for r in results)

    @pytest.mark.parametrize("task,expected_dept", [
        ("帮我写个小红书文案", "operations"),  # 文案 → 运营部
        ("招聘工程师", "hr"),
        ("制定预算", "finance"),
        ("设计架构", "engineering"),
        ("撰写PRD", "product"),
    ])
    def test_routing_consistency(self, task, expected_dept):
        """测试路由一致性。"""
        router = CEORouter()

        # 执行10次验证一致性
        for _ in range(10):
            result = router.route(task)
            assert result["target_department"] == expected_dept


# ═══════════════════════════════════════════════════════════════════════════════
# 性能基准测试
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformanceBenchmark:
    """性能基准测试。"""

    def test_routing_benchmark(self):
        """路由性能基准测试。"""
        router = CEORouter()

        # 预热
        for _ in range(10):
            router.route("测试任务")

        # 基准测试
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            router.route("帮我写个小红书文案")

        elapsed = time.time() - start_time
        avg_time_ms = (elapsed / iterations) * 1000

        print(f"\n📊 路由基准测试 ({iterations}次):")
        print(f"⏱ 总耗时: {elapsed:.3f}s")
        print(f"⏱ 平均: {avg_time_ms:.3f}ms/任务")
        print(f"📈 QPS: {iterations/elapsed:.1f}")

        # 基准要求
        assert avg_time_ms < 1.0, f"平均耗时 {avg_time_ms:.3f}ms 超过 1ms 基准"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
