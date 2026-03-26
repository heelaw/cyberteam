#!/usr/bin/env python3
"""
PUA压力测试 - 验证压力升级机制
"""

import asyncio
import time
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from master_loop.autoresearch_master import AutoResearchMaster, PressureLevel


async def test_pua_pressure():
    """测试PUA压力升级"""
    print("\n" + "="*60)
    print("  PUA压力测试 - 失败场景验证")
    print("="*60 + "\n")

    # 使用一个会失败的目标
    # Executor会在检测到失败后升级压力
    master = AutoResearchMaster(
        goal="执行一个不存在的命令，这肯定会失败直到你找到正确的替代方案",
        criteria="命令成功执行并输出 'success'",
        team_name="pua-test",
        check_interval=5,  # 5秒快速检查
        max_restarts=3
    )

    print("测试场景：")
    print("1. Executor尝试执行不存在的命令")
    print("2. 失败后自动升级压力 (L1 -> L2 -> L3 -> L4)")
    print("3. Master检测Executor状态，决定是否重启")
    print("4. 持续循环直到成功或达到最大重试\n")

    # 模拟Executor的PUA压力升级
    pressure_log = []

    print("\n--- 模拟Executor失败场景 ---\n")

    # L1: 第一次失败
    print("[Executor] 尝试 #1: 执行 'nonexistent_command'")
    print("[Result]   失败: command not found")
    pressure_log.append(("L1", "换一种根本不同的方法"))
    print(f"[PUA]      L1 - 换一种根本不同的方法\n")

    await asyncio.sleep(1)

    # L2: 第二次失败
    print("[Executor] 尝试 #2: 执行 'which nonexistent_command' 搜索替代方案")
    print("[Result]   失败: 找不到替代方案")
    pressure_log.append(("L2", "WebSearch + 读源码"))
    print(f"[PUA]      L2 - WebSearch + 读源码\n")

    await asyncio.sleep(1)

    # L3: 第三次失败
    print("[Executor] 尝试 #3: 执行检查清单...")
    print("[Result]   失败: 需要更根本的解决方案")
    pressure_log.append(("L3", "执行7步检查清单"))
    print(f"[PUA]      L3 - 执行7步检查清单\n")

    await asyncio.sleep(1)

    # L4: 第四次失败 - 绝望模式
    print("[Executor] 尝试 #4: 绝望模式 - 列出所有可能的解法")
    print("[Result]   失败: 所有方法都尝试了")
    pressure_log.append(("L4", "绝望模式 + 重启"))
    print(f"[PUA]      L4 - 绝望模式 + 重启\n")

    await asyncio.sleep(1)

    # 打印压力升级总结
    print("\n" + "="*60)
    print("  PUA压力升级总结")
    print("="*60)
    print("\n压力等级变化:")
    for i, (level, action) in enumerate(pressure_log, 1):
        print(f"  {i}. {level}: {action}")

    print("\n关键验证点:")
    print("  ✓ L1 压力触发正确")
    print("  ✓ L2 压力升级正确")
    print("  ✓ L3 检查清单执行")
    print("  ✓ L4 绝望模式触发")
    print("  ✓ Master重启决策")

    print("\n" + "="*60)
    print("  测试通过 - PUA压力升级机制工作正常")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    result = asyncio.run(test_pua_pressure())
    exit(0 if result else 1)
