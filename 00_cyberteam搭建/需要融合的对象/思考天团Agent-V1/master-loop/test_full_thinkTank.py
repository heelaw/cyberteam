#!/usr/bin/env python3
"""思考天团 AutoResearch 完整测试"""
import asyncio
import sys
import importlib.util
from pathlib import Path

work_dir = Path("/Users/cyberwiz/Library/Mobile Documents/iCloud~md~obsidian/Documents/01_Project/02_Skill研发/Output/思考天团-可运行版")

# 直接加载模块
spec1 = importlib.util.spec_from_file_location("expert_registry", work_dir / "master-loop/expert_registry_full.py")
expert_registry = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(expert_registry)

spec2 = importlib.util.spec_from_file_location("thinktank", work_dir / "master-loop/thinkTank_master_final.py")
thinktank_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(thinktank_module)

ThinkTankAutoResearchMaster = thinktank_module.ThinkTankAutoResearchMaster
ThinkTankConfig = thinktank_module.ThinkTankConfig


async def test_think_tank():
    """测试思考天团"""
    config = ThinkTankConfig(
        goal="我应该选择工作A（高薪但重复）还是工作B（低薪但有成长）？",
        criteria="至少3个专家分析，给出明确建议",
        mode="parallel",
        max_experts=4,
        check_interval=5,
        max_iterations=3
    )

    master = ThinkTankAutoResearchMaster(config, work_dir)

    print("\n" + "="*70)
    print("  思考天团 AutoResearch 完整测试")
    print("="*70)
    print(f"\n问题: {config.goal}")
    print(f"Criteria: {config.criteria}")
    print(f"最大专家数: {config.max_experts}\n")

    return await master.run_loop()


if __name__ == "__main__":
    result = asyncio.run(test_think_tank())
    print("\n" + "="*70)
    print("  测试完成!" if result else "  测试未完全达成目标")
    print("="*70)
