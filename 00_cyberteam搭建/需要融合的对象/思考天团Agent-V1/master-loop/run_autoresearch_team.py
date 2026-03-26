#!/usr/bin/env python3
"""
AutoResearch Team 启动脚本
创建完整的Goal-Driven + AutoResearch + PUA系统
"""

import subprocess
import time
import sys
from pathlib import Path

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def log(level: str, message: str):
    color = {
        "INFO": BLUE,
        "SUCCESS": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED
    }.get(level, NC)
    print(f"{color}[{level}]{NC} {message}")


def run_bash(cmd: str, timeout: int = 30) -> tuple:
    """运行bash命令"""
    try:
        full_cmd = f"source ~/.cyberteam-venv/bin/activate && {cmd}"
        result = subprocess.run(
            ["bash", "-c", full_cmd],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def cleanup_team(team_name: str):
    """清理旧团队"""
    log("INFO", f"清理旧团队: {team_name}")
    run_bash(f"cyberteam team cleanup {team_name} <<< 'y'", timeout=10)


def create_team(team_name: str) -> bool:
    """创建团队"""
    log("INFO", f"创建团队: {team_name}")
    returncode, stdout, stderr = run_bash(
        f"cyberteam team spawn-team {team_name} -d 'AutoResearch Goal-Driven Team'"
    )

    if returncode == 0:
        log("SUCCESS", f"团队创建成功: {team_name}")
        return True
    else:
        log("ERROR", f"团队创建失败: {stderr}")
        return False


def create_tasks(team_name: str, goal: str) -> bool:
    """创建任务"""
    log("INFO", "创建任务...")

    # 主任务
    returncode, stdout, stderr = run_bash(
        f"cyberteam task create {team_name} 'AutoResearch: {goal}' -o master"
    )

    if returncode != 0:
        log("ERROR", f"任务创建失败")
        return False

    log("SUCCESS", "任务创建成功")
    return True


def spawn_master(team_name: str, goal: str, criteria: str) -> bool:
    """启动Master Agent"""
    log("INFO", "启动Master Agent...")

    # 构造task描述
    task = f"""Goal-Driven Master控制整个任务:
Goal: {goal}
Criteria: {criteria}

核心职责:
1. 启动AutoResearch Executor执行任务
2. 每30秒检查Executor状态
3. 如果Executor失败或卡住，应用PUA压力
4. 持续循环直到Criteria满足
5. Criteria满足时停止Executor并输出结果"""

    returncode, stdout, stderr = run_bash(
        f"cyberteam spawn --team {team_name} --agent-name master --task '{task}'",
        timeout=30
    )

    if returncode == 0:
        log("SUCCESS", "Master Agent启动成功")
        return True
    else:
        log("ERROR", f"Master启动失败: {stderr}")
        return False


def spawn_executor(team_name: str, goal: str) -> bool:
    """启动Executor Agent"""
    log("INFO", "启动Executor Agent...")

    task = f"""AutoResearch Executor执行任务:
Goal: {goal}

执行步骤:
1. 分析目标，确定执行方法
2. 尝试执行（创建文件/运行脚本等）
3. 失败时自动分析错误
4. 使用WebSearch搜索解决方案
5. 尝试不同方法直到成功或达到最大次数
6. 定期报告状态给Master

关键规则:
- 不放弃：禁止说"无法解决"
- 先行动：工具优先
- 主动报告：定期报告进度"""


    returncode, stdout, stderr = run_bash(
        f"cyberteam spawn --team {team_name} --agent-name executor --task '{task}'",
        timeout=30
    )

    if returncode == 0:
        log("SUCCESS", "Executor Agent启动成功")
        return True
    else:
        log("ERROR", f"Executor启动失败: {stderr}")
        return False


def show_board(team_name: str):
    """显示看板"""
    log("INFO", f"\n{'='*60}")
    log("INFO", f"团队: {team_name}")
    log("INFO", f"{'='*60}")

    returncode, stdout, stderr = run_bash(
        f"cyberteam board show {team_name}",
        timeout=15
    )

    print(stdout)


def main():
    """主函数"""
    team_name = "autoresearch-team"
    goal = "创建一个测试文件 /tmp/test.txt，内容是hello world"
    criteria = "文件存在且内容正确"

    print(f"\n{'='*60}")
    print(f"  AutoResearch Team 启动")
    print(f"{'='*60}\n")

    # 1. 清理旧团队
    cleanup_team(team_name)

    # 2. 创建团队
    if not create_team(team_name):
        sys.exit(1)

    # 3. 创建任务
    if not create_tasks(team_name, goal):
        sys.exit(1)

    # 4. 启动Master
    if not spawn_master(team_name, goal, criteria):
        sys.exit(1)

    # 5. 启动Executor
    if not spawn_executor(team_name, goal):
        sys.exit(1)

    # 6. 显示看板
    time.sleep(3)
    show_board(team_name)

    print(f"\n{'='*60}")
    print(f"  AutoResearch Team 运行中")
    print(f"  查看实时看板: cyberteam board live {team_name}")
    print(f"  查看Executor输出: cyberteam board attach {team_name}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
