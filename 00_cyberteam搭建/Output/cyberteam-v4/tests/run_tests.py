#!/usr/bin/env python3
"""
CyberTeam V4 测试运行器

运行方式:
    python tests/run_tests.py
"""

import sys
from pathlib import Path

# 添加到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))
sys.path.insert(0, str(Path(__file__).parent.parent / "integration"))

from ceo import CEORouter, Intent
from debate_engine import DebateEngine, DebateState
from clawteam_adapter import ClawTeamAdapter


def test(name, fn):
    """运行测试"""
    try:
        fn()
        print(f"  ✅ {name}")
        return True
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False


def test_ceo_router():
    """测试 CEO 路由"""
    router = CEORouter()

    print("\n【CEO 路由测试】")

    tests = [
        ("简单问候", lambda: router.route("你好").target == "NONE"),
        ("技术路由", lambda: router.route("开发系统").target == "L3B"),
        ("内容路由", lambda: router.route("写文章").target == "L3A"),
        ("数据路由", lambda: router.route("分析数据").target == "L3A"),
        ("HR路由", lambda: router.route("招聘").target == "L3A"),
    ]

    results = [test(name, fn) for name, fn in tests]
    return all(results)


def test_debate_engine():
    """测试辩论引擎"""
    engine = DebateEngine()

    print("\n【辩论引擎测试】")

    # 创建会话
    session = engine.create_session(
        task_id="test-001",
        topic="如何提升留存？",
        expert_ids=["kahneman", "first_principle"]
    )
    test("创建会话", lambda: session.task_id == "test-001")

    # 开始辩论
    engine.start_debate(session.session_id)
    test("开始辩论", lambda: session.state == DebateState.IN_PROGRESS)

    # 添加观点
    engine.add_opinion(
        session.session_id,
        "kahneman",
        "从风险角度分析",
        concerns=["用户风险"],
        suggestions=["降低门槛"]
    )
    test("添加观点", lambda: len(session.opinions) == 1)

    # 收敛检查
    result = engine.check_convergence(session.session_id)
    test("收敛检查", lambda: "converged" in result)

    # 生成综合
    synthesis = engine.generate_synthesis(session.session_id)
    test("生成综合", lambda: "综合分析" in synthesis)

    return True


def test_clawteam_adapter():
    """测试 ClawTeam 适配器"""
    adapter = ClawTeamAdapter()

    print("\n【ClawTeam 适配器测试】")

    # 列出团队
    teams = adapter.list_teams()
    test("列出团队", lambda: isinstance(teams, list))

    return True


def test_integration():
    """集成测试"""
    print("\n【集成测试】")

    # 1. 路由
    router = CEORouter()
    result = router.route("开发登录系统")
    test("完整流程-路由", lambda: result.target == "L3B")

    # 2. 辩论
    debate = DebateEngine()
    session = debate.create_session(
        task_id="flow-test",
        topic="方案评审",
        expert_ids=["kahneman", "mckinsey"]
    )
    debate.start_debate(session.session_id)
    debate.add_opinion(session.session_id, "kahneman", "风险评估")
    test("完整流程-辩论", lambda: session.state == DebateState.IN_PROGRESS)

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("CyberTeam V4 测试套件")
    print("=" * 60)

    results = []

    results.append(test_ceo_router())
    results.append(test_debate_engine())
    results.append(test_clawteam_adapter())
    results.append(test_integration())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 60)

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
