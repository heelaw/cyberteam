#!/usr/bin/env python3
# CyberTeam v2.0.1 - 一键启动器 (融合版)

"""
CyberTeam v2.0.1 CLI 启动器 (融合版)

集成: thinking_injector + routing_engine + dev_qa_engine + quality_gate_engine

用法：
    python launcher.py --goal "你的目标"
    python launcher.py --goal "你想做一个在线教育平台" --team minimal
    python launcher.py --interactive
    python launcher.py --test-engines    # 测试所有引擎
    python launcher.py --check <agent-id> # Dev-QA检查Agent定义

示例：
    python launcher.py --goal "我想做一个在线教育平台，目标是一年内10万付费用户"
    python launcher.py --goal "制定抖音内容运营策略" --team growth
    python launcher.py --check investor-agent
    python launcher.py --interactive
"""

import argparse
import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.thinking_injector import ThinkingInjector, CEOThinkingEngine
from engine.routing_engine import RoutingEngine
from engine.dev_qa_engine import DevQAEngine
from engine.quality_gate_engine import QualityGateEngine, GateLevel
from integration.clawteam_adapter import ClawTeamAdapter, CyberTeamLauncher, TEAM_PRESETS
from integration.pua_adapter import PUAAdapter, PUAIntegration
from integration.goal_driver_adapter import GoalDriverAdapter, MasterAgent
from integration.agency_adapter import AgencyAdapter


class CyberTeamCLI:
    """CyberTeam v2 CLI"""

    def __init__(self):
        self.thinking_injector = ThinkingInjector()
        self.ceo_engine = CEOThinkingEngine(self.thinking_injector)
        self.routing_engine = RoutingEngine()
        self.dev_qa_engine = DevQAEngine(max_attempts=3)
        self.quality_gate = QualityGateEngine()
        self.clawteam = ClawTeamAdapter()
        self.pua = PUAIntegration()
        self.goal_driver = GoalDriverAdapter()
        self.agency = AgencyAdapter()

    def analyze_goal(self, goal: str) -> dict:
        """分析目标"""
        print("\n" + "=" * 60)
        print("CEO 目标分析")
        print("=" * 60)

        result = self.ceo_engine.decompose(goal)

        # 5W1H 拆解
        print("\n【5W1H1Y 拆解】")
        for key, value in result["decomposition"].items():
            status = "✓" if value["status"] == "extracted" else "?"
            print(f"  {status} {key}: {value['content'] or '(需要澄清)'}")
            if value.get("questions"):
                for q in value["questions"]:
                    print(f"      → {q}")

        # MECE 分类
        print("\n【MECE 分类】")
        for cat in result["mece"]["categories"]:
            print(f"\n  【{cat['name']}】")
            for item in cat["items"]:
                print(f"    - {item}")

        # 思维专家
        ctx = result["thinking_context"]
        print(f"\n【激活的思维专家】 ({len(ctx.selected_experts)}个)")
        for e in ctx.selected_experts:
            print(f"  - {e.name_cn} ({e.category})")

        # 推荐团队
        print("\n【推荐管理团队】")
        team = result["management_team_suggestion"]
        from integration.clawteam_adapter import MANAGEMENT_ROLES
        for role in team:
            if role in MANAGEMENT_ROLES:
                print(f"  - {MANAGEMENT_ROLES[role]['name']}: {MANAGEMENT_ROLES[role]['focus']}")

        # 执行计划
        print("\n【执行计划】")
        for phase, info in result["execution_plan"].items():
            print(f"\n  【{phase.upper()}】{info['name']} ({info['duration']})")
            for task in info["tasks"]:
                print(f"    - {task}")

        return result

    def launch(self, goal: str, team_type: str = "full"):
        """启动 CyberTeam"""

        # 分析目标
        analysis = self.analyze_goal(goal)

        # 选择团队配置
        if team_type == "custom":
            management_roles = analysis["management_team_suggestion"]
        else:
            management_roles = TEAM_PRESETS.get(team_type, TEAM_PRESETS["full"])

        print("\n" + "=" * 60)
        print(f"启动 CyberTeam v2")
        print(f"团队类型: {team_type}")
        print(f"管理层: {', '.join(management_roles)}")
        print("=" * 60)

        # 检查 ClawTeam 是否可用
        status = self.clawteam._run_command(["--version"])
        if not status["success"]:
            print("\n⚠️  ClawTeam 未安装或不可用")
            print("   请先安装: npm install -g clawteam")
            print("\n   或者使用本地模式继续...")
            print("\n" + "-" * 60)
            print("本地模式启动（无 ClawTeam）")
            print("-" * 60)

            # 本地模式
            self._local_mode(goal, management_roles, analysis)
            return

        # ClawTeam 模式
        import datetime
        team_name = f"cyber-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"
        launcher = CyberTeamLauncher(self.clawteam)
        result = launcher.launch(
            goal=goal,
            team_name=team_name,
            management_roles=management_roles,
            auto_tasks=True
        )

        if result.get("success"):
            print(f"\n✅ CyberTeam 已启动!")
            print(f"   团队名称: {result['team_name']}")
            print(f"   管理团队: {', '.join(result.get('management_team', []))}")
            print(f"   任务数量: {len(result.get('tasks', []))}")
            print(f"\n   查看团队: clawteam team status --team {result['team_name']}")
            print(f"   查看任务: clawteam task list --team {result['team_name']}")
        else:
            print(f"\n❌ 启动失败: {result.get('error')}")

        return result

    def check_agent(self, agent_id: str):
        """Dev-QA 检查 Agent 定义"""
        print(f"\n{'='*60}")
        print(f"Dev-QA 检查: {agent_id}")
        print(f"{'='*60}")

        # 尝试从 layers/ 加载
        agent_paths = [
            Path(__file__).parent.parent / "layers" / "management" / "management-agents.md",
            Path(__file__).parent.parent / "layers" / "ceo" / "ceo-agent.md",
            Path(__file__).parent.parent / "layers" / "execution" / "execution-agents.md",
        ]

        for path in agent_paths:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if agent_id in content:
                    # 提取Agent定义
                    agent_def = {"name": agent_id, "content": content}
                    result = self.dev_qa_engine.execute(
                        target_type="agent",
                        target_name=agent_id,
                        target=agent_def
                    )
                    print(self.dev_qa_engine.generate_report(result))

                    # 质量门控
                    print("\n" + "-"*60)
                    print("三级质量门控:")
                    qa_result = self.quality_gate.evaluate_all(agent_def)
                    print(self.quality_gate.generate_report(qa_result))
                    return

        print(f"未找到 Agent: {agent_id}")

    def test_engines(self):
        """测试所有引擎"""
        print(f"\n{'='*60}")
        print("CyberTeam v2.0.1 引擎测试")
        print(f"{'='*60}")

        # 1. 测试思维注入引擎
        print("\n【1/4】思维注入引擎")
        test_goals = [
            "我想做一个在线教育平台，目标是一年内10万付费用户",
            "帮我分析竞争对手的SWOT",
            "制定抖音内容运营策略",
        ]
        for goal in test_goals:
            ctx = self.thinking_injector.process(goal)
            print(f"  目标: {goal[:30]}...")
            print(f"  激活专家: {len(ctx.selected_experts)}个")
            for e in ctx.selected_experts:
                print(f"    - {e.name_cn}")

        # 2. 测试路由引擎
        print("\n【2/4】路由引擎")
        for goal in test_goals:
            ctx = self.thinking_injector.process(goal)
            result = self.routing_engine.route(ctx, goal)
            print(f"  目标: {goal[:30]}...")
            print(f"  路由置信度: {result.confidence:.1%}")
            print(f"  选中Agent: {[a.name_cn for a in result.selected_agents[:3]]}")

        # 3. 测试Dev-QA引擎
        print("\n【3/4】Dev-QA引擎")
        test_agent = {
            "name": "test-agent",
            "id": "test-agent",
            "Identity": "测试身份定义",
            "能力": "测试能力列表",
            "输出格式": "JSON格式",
            "trigger": ["测试"]
        }
        result = self.dev_qa_engine.execute(
            target_type="agent",
            target_name="test-agent",
            target=test_agent
        )
        print(f"  测试Agent评分: {result.score_result.overall_score:.1f}分")
        print(f"  状态: {result.status.value}")

        # 4. 测试质量门控
        print("\n【4/4】质量门控引擎")
        test_output = {
            "goal": "做一个教育平台",
            "result": "分析完成",
            "plan": "三阶段计划",
            "kpi": "10万用户",
            "content": "我们用SWOT分析，根据数据显示某平台的增长路径..."
        }
        qa_result = self.quality_gate.evaluate_all(test_output)
        print(f"  L1完整度: {qa_result['summary']['l1']}")
        print(f"  L2专业度: {qa_result['summary']['l2']}")
        print(f"  L3可执行性: {qa_result['summary']['l3']}")
        print(f"  通过: {'✅' if qa_result['passed'] else '❌'}")

        print("\n" + "="*60)
        print("引擎测试完成 ✅")

    def _local_mode(self, goal: str, roles: list, analysis: dict):
        """本地模式（无 ClawTeam）"""

        from integration.clawteam_adapter import MANAGEMENT_ROLES

        print(f"\n📋 目标: {goal}")
        print(f"📋 团队: {', '.join(roles)}")

        # 打印管理层信息
        print(f"\n📋 管理层配置:")
        for role in roles:
            if role in MANAGEMENT_ROLES:
                config = MANAGEMENT_ROLES[role]
                print(f"  [{role}] {config['name']}")
                print(f"      焦点: {config['focus']}")

        # 推荐执行 Agent
        recommended = self.agency.recommend_agents(goal, top_k=5)
        print(f"\n🔧 推荐执行专家:")
        for agent in recommended:
            print(f"  - {agent.name_cn}: {agent.description}")

        # 思维专家
        ctx = analysis["thinking_context"]
        print(f"\n🧠 激活的思维专家 ({len(ctx.selected_experts)}个):")
        for e in ctx.selected_experts[:5]:
            print(f"  - {e.name_cn}")

        # PUA 测试
        print(f"\n😤 PUA 机制:")
        pua_test = self.pua.get_adapter("test")
        for i in range(3):
            context = {"failure_count": i + 1}
            if pua_test.should_trigger(context):
                result = pua_test.escalate(context)
                print(f"  失败{i+1}次 → L{result['level']}: {result['phrase'][:50]}...")

        print(f"\n✅ 本地分析完成!")
        print(f"\n💡 要使用完整功能，请安装 ClawTeam:")
        print(f"   npm install -g clawteam")


def interactive_mode():
    """交互模式"""
    cli = CyberTeamCLI()

    print("\n" + "=" * 60)
    print("  CyberTeam v2 - 交互模式")
    print("=" * 60)

    print("\n请输入你的目标/问题（输入 'quit' 退出）:\n")

    while True:
        try:
            goal = input("> ").strip()

            if goal.lower() in ["quit", "q", "exit"]:
                print("\n再见!")
                break

            if not goal:
                continue

            # 分析并给出建议
            cli.analyze_goal(goal)

            # 推荐 Agent
            recommended = cli.agency.recommend_agents(goal, top_k=3)
            print("\n【推荐专家】")
            for agent in recommended:
                print(f"  - {agent.name_cn}")

            print("\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\n\n再见!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="CyberTeam v2 - 企业级 AI Agent 协作系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python launcher.py --goal "我想做一个在线教育平台"
  python launcher.py --goal "帮我分析竞争对手" --team minimal
  python launcher.py --goal "提升DAU 10%" --team growth
  python launcher.py --interactive
        """
    )

    parser.add_argument(
        "--goal", "-g",
        type=str,
        help="你的目标或问题"
    )

    parser.add_argument(
        "--team", "-t",
        type=str,
        default="full",
        choices=["full", "minimal", "growth", "product_launch", "technical", "startup", "custom"],
        help="团队类型 (default: full)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="交互模式"
    )

    parser.add_argument(
        "--analyze-only", "-a",
        action="store_true",
        help="仅分析目标，不启动团队"
    )

    parser.add_argument(
        "--check", "-c",
        type=str,
        help="Dev-QA检查指定Agent定义 (agent-id)"
    )

    parser.add_argument(
        "--test-engines", "-e",
        action="store_true",
        help="测试所有引擎"
    )

    args = parser.parse_args()

    cli = CyberTeamCLI()

    # Dev-QA检查模式
    if args.check:
        cli.check_agent(args.check)
        return

    # 引擎测试模式
    if args.test_engines:
        cli.test_engines()
        return

    if args.interactive:
        interactive_mode()
        return

    if args.goal:
        if args.analyze_only:
            cli.analyze_goal(args.goal)
        else:
            cli.launch(args.goal, args.team)
    else:
        parser.print_help()
        print("\n💡 提示: 使用 --interactive 进入交互模式")


if __name__ == "__main__":
    main()
