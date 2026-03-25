#!/usr/bin/env python3
"""
CyberTeam V4 - 启动器

用法：
    python launcher.py --goal "你的目标"
    python launcher.py --goal "帮我分析下季度增长策略"
    python launcher.py --interactive
"""

import argparse
import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path

# 添加 engine 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ceo import CEORouter, RoutingResult
from strategy import StrategyEngine, ExecutionPlan
from pm import PMCoordinator, ExecutionMode
from department import DepartmentExecutor
from debate_engine import DebateEngine
from integration.clawteam_adapter import ClawTeamAdapter


class CyberTeamV4:
    """CyberTeam V4 核心引擎"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.router = CEORouter()
        self.strategy = StrategyEngine()
        self.pm = PMCoordinator()
        self.department = DepartmentExecutor()
        self.debate_engine = DebateEngine()
        self.clawteam = ClawTeamAdapter()
        self.task_history = []

    def run(self, user_input: str, context: dict = None) -> dict:
        """运行完整流程"""

        print("\n" + "=" * 60)
        print("CyberTeam V4 核心引擎")
        print("=" * 60)

        result = {
            "task_id": str(uuid.uuid4())[:8],
            "user_input": user_input,
            "start_time": datetime.now().isoformat(),
            "stages": {}
        }

        # Stage 1: CEO 路由
        print("\n【Stage 1】CEO 路由 (L1)")
        print("-" * 40)
        routing = self.router.route(user_input)

        print(f"  意图识别: {routing.intent}")
        print(f"  复杂度: {routing.complexity}")
        print(f"  路由目标: {routing.target} → {routing.target_name}")
        print(f"  理由: {routing.reason}")

        result["stages"]["ceo_routing"] = {
            "intent": routing.intent,
            "complexity": routing.complexity,
            "target": routing.target,
            "target_name": routing.target_name,
            "reason": routing.reason
        }

        # 如果是简单咨询，直接返回
        if routing.target == "NONE":
            result["status"] = "completed"
            result["output"] = "您好！有什么可以帮您的？"
            result["end_time"] = datetime.now().isoformat()
            return result

        # Stage 2: Strategy 方案设计
        print("\n【Stage 2】Strategy 方案设计 (L2)")
        print("-" * 40)

        plan = self.strategy.create_plan(
            result["task_id"],
            user_input,
            routing.intent,
            routing.complexity
        )

        print(f"  任务ID: {plan.task_id}")
        print(f"  思维框架: {plan.framework.value}")
        print(f"  部门: {plan.resources['departments']}")

        result["stages"]["strategy"] = {
            "task_id": plan.task_id,
            "framework": plan.framework.value,
            "departments": plan.resources["departments"],
            "skills": plan.resources["skills"],
            "schedule": plan.schedule
        }

        # Stage 3: PM 协调
        print("\n【Stage 3】PM 协调 (L2)")
        print("-" * 40)

        # 准备执行计划
        exec_plan = {
            "task_id": plan.task_id,
            "title": plan.title,
            "intent": plan.intent,
            "complexity": plan.complexity,
            "resources": plan.resources,
            "context": context or {}
        }

        # 执行 (模拟)
        print(f"  执行模式: {'并行' if plan.complexity == '高' else '串行'}")
        print(f"  任务数量: {len(plan.resources['departments'])}")
        print("  执行中...")

        # Stage 4: 部门执行
        print("\n【Stage 4】部门执行 (L3)")
        print("-" * 40)

        outputs = {}
        for dept in plan.resources["departments"]:
            print(f"  → {dept} 执行中...")
            # TODO: 实际执行
            outputs[dept] = {
                "status": "success",
                "output": f"{dept} 执行完成"
            }

        result["stages"]["execution"] = outputs

        # Stage 5: 结果聚合
        print("\n【Stage 5】结果聚合")
        print("-" * 40)

        aggregated = {
            "summary": {
                "departments": len(outputs),
                "success": sum(1 for o in outputs.values() if o["status"] == "success")
            },
            "outputs": outputs
        }

        print(f"  执行部门: {aggregated['summary']['departments']}")
        print(f"  成功: {aggregated['summary']['success']}")

        result["stages"]["aggregation"] = aggregated

        # 完成
        result["status"] = "completed"
        result["output"] = aggregated
        result["end_time"] = datetime.now().isoformat()

        print("\n" + "=" * 60)
        print("执行完成")
        print("=" * 60)

        return result

    def run_interactive(self):
        """交互模式"""
        print("\n" + "=" * 60)
        print("CyberTeam V4 - 交互模式")
        print("=" * 60)
        print("输入您的目标，按 Enter 执行")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n> ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("再见！")
                    break

                if not user_input:
                    continue

                self.run(user_input)

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {e}")


def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(description="CyberTeam V4 启动器")
    parser.add_argument("--goal", "-g", help="任务目标")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式")

    args = parser.parse_args()

    # 初始化
    ct = CyberTeamV4(debug=args.debug)

    if args.interactive:
        ct.run_interactive()
    elif args.goal:
        result = ct.run(args.goal)
        print("\n【最终结果】")
        print(result)
    else:
        # 默认交互模式
        ct.run_interactive()


if __name__ == "__main__":
    main()
