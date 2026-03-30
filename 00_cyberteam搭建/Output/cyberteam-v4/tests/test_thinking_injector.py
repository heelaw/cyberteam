#!/usr/bin/env python3
"""
CyberTeam V4 - 思维注入系统测试
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.thinking import (
    ThinkingLoader,
    ThinkingInjector,
    ThinkingRouter,
    InjectionContext,
    TaskContext
)


def test_thinking_loader():
    """测试思维模型加载"""
    print("\n" + "="*60)
    print("【测试 1】思维模型加载器")
    print("="*60)

    loader = ThinkingLoader()
    models = loader.load_all()

    print(f"\n✅ 加载了 {len(models)} 个思维模型")

    # 统计分类
    categories = {}
    for model in models.values():
        cat = model.category.value
        categories[cat] = categories.get(cat, 0) + 1

    print("\n分类统计：")
    for cat, count in categories.items():
        print(f"  - {cat}: {count}")

    # 测试获取单个模型
    fp = loader.get_model("first-principle")
    if fp:
        print(f"\n✅ 获取模型成功: {fp.name}")

    # 测试关键词搜索
    results = loader.search_by_keyword("战略")
    print(f"\n✅ 关键词搜索 '战略': 找到 {len(results)} 个模型")

    return len(models) > 0


def test_thinking_router():
    """测试思维路由"""
    print("\n" + "="*60)
    print("【测试 2】思维路由")
    print("="*60)

    loader = ThinkingLoader()
    loader.load_all()
    router = ThinkingRouter(loader)

    # 测试不同意图的路由
    test_cases = [
        TaskContext(
            task_description="分析用户增长策略，制定Q2季度计划",
            intent="数据分析",
            complexity="高",
            domain="增长"
        ),
        TaskContext(
            task_description="撰写产品软文用于小红书推广",
            intent="内容运营",
            complexity="中",
            domain="运营"
        ),
        TaskContext(
            task_description="设计技术架构方案",
            intent="技术研发",
            complexity="高",
            domain="技术"
        ),
    ]

    for ctx in test_cases:
        result = router.route(ctx)
        model_names = [m.name for m in result.combination.models]
        print(f"\n任务: {ctx.task_description[:30]}...")
        print(f"  → 路由: {result.reasoning}")
        print(f"  → 模型: {', '.join(model_names)}")
        print(f"  → 置信度: {result.confidence:.0%}")


def test_thinking_injector():
    """测试思维注入器"""
    print("\n" + "="*60)
    print("【测试 3】思维注入器")
    print("="*60)

    injector = ThinkingInjector()
    injector.load_models()

    # 测试自动注入
    context = InjectionContext(
        agent_name="PM Agent",
        agent_role="产品管理",
        task="设计用户增长策略"
    )

    result = injector.inject_auto(context)

    print(f"\n✅ 注入成功: {result.success}")
    print(f"✅ 使用模型: {', '.join(result.model_names)}")
    print(f"✅ 路由理由: {result.routing_reasoning}")
    print(f"\n【注入的 Prompt】")
    print("-"*60)
    print(result.injected_prompt[:800] + "..." if len(result.injected_prompt) > 800 else result.injected_prompt)
    print("-"*60)


def test_manual_inject():
    """测试手动指定注入"""
    print("\n" + "="*60)
    print("【测试 4】手动指定注入")
    print("="*60)

    injector = ThinkingInjector()
    injector.load_models()

    result = injector.inject_manual(
        agent_name="战略专家",
        agent_role="战略规划",
        task="制定公司三年战略规划",
        model_ids=["first-principle", "swot-tows", "game-theory"],
        intent="战略规划",
        complexity="高"
    )

    print(f"\n✅ 注入成功: {result.success}")
    print(f"✅ 使用模型: {', '.join(result.model_names)}")
    print(f"✅ 置信度: {result.confidence:.0%}")


def test_debate_inject():
    """测试辩论注入"""
    print("\n" + "="*60)
    print("【测试 5】辩论注入")
    print("="*60)

    injector = ThinkingInjector()
    injector.load_models()

    prompt = injector.inject_for_debate(
        task="是否应该进入下沉市场",
        stance="支持进入",
        models=["first-principle", "swot-tows", "game-theory"]
    )

    print(f"\n✅ 辩论 Prompt 生成成功")
    print(f"\n【辩论 Prompt】")
    print("-"*60)
    print(prompt[:600] + "..." if len(prompt) > 600 else prompt)
    print("-"*60)


def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     CyberTeam V4 - 思维注入系统测试                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    results = []

    try:
        results.append(("思维模型加载", test_thinking_loader()))
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        results.append(("思维模型加载", False))

    try:
        results.append(("思维路由", True))
        test_thinking_router()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        results.append(("思维路由", False))

    try:
        results.append(("思维注入", True))
        test_thinking_injector()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        results.append(("思维注入", False))

    try:
        results.append(("手动注入", True))
        test_manual_inject()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        results.append(("手动注入", False))

    try:
        results.append(("辩论注入", True))
        test_debate_inject()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        results.append(("辩论注入", False))

    # 总结
    print("\n" + "="*60)
    print("【测试总结】")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过！思维注入系统工作正常。")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，需要修复。")


if __name__ == "__main__":
    main()
