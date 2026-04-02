#!/usr/bin/env python3
"""
AutoResearch Master - 真正的Goal-Driven循环控制器
集成：
- 自动研究循环
- PUA压力升级
- ClawTeam编排
- 持续监控直到目标达成
"""

import asyncio
import subprocess
import time
import json
import os
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'


class ExecutorStatus(Enum):
    RUNNING = "running"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class PressureLevel(Enum):
    L0_NONE = 0
    L1 = 1  # 换一种根本不同的方法
    L2 = 2  # WebSearch + 读源码
    L3 = 3  # 执行7步检查清单
    L4 = 4  # 绝望模式 - 重启


@dataclass
class LoopStats:
    """循环统计"""
    iterations: int = 0
    executor_restarts: int = 0
    pressure_upgrades: int = 0
    last_check_time: str = ""
    consecutive_inactive: int = 0


class AutoResearchMaster:
    """
    AutoResearch Master - 真正的Goal-Driven控制器

    核心职责：
    1. 启动和监控AutoResearch Executor
    2. 检测Executor是否卡住/不活跃
    3. 应用PUA压力升级
    4. 决定是否重启Executor
    5. 持续循环直到Criteria满足

    核心循环：
    while (Criteria not met):
        status = check_executor()
        if status == INACTIVE:
            apply_pressure()
            if too_many_restarts():
                restart_executor_new_method()
            else:
                restart_executor()
        elif status == COMPLETED:
            if meets_criteria():
                stop()
            else:
                apply_pressure()
        wait(check_interval)
    """

    def __init__(
        self,
        goal: str,
        criteria: str,
        team_name: str = "autoresearch-team",
        check_interval: int = 30,
        max_restarts: int = 5,
        max_iterations: int = 100
    ):
        self.goal = goal
        self.criteria = criteria
        self.team_name = team_name
        self.check_interval = check_interval
        self.max_restarts = max_restarts
        self.max_iterations = max_iterations

        self.stats = LoopStats()
        self.pressure_level = PressureLevel.L0_NONE
        self.executor_pid: Optional[int] = None
        self.last_progress_time = time.time()

        # 工作目录
        self.work_dir = Path(__file__).parent.parent
        self.state_file = self.work_dir / "master-loop" / "master_state.json"
        self.goal_file = self.work_dir / "goal.md"
        self.criteria_file = self.work_dir / "criteria.md"

    def log(self, level: str, message: str):
        color = {
            "INFO": BLUE,
            "SUCCESS": GREEN,
            "WARNING": YELLOW,
            "ERROR": RED,
            "MASTER": MAGENTA,
            "PUA": RED,
            "EXECUTOR": CYAN
        }.get(level, NC)
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{level}][{timestamp}]{NC} {message}")

    def save_state(self):
        """保存Master状态"""
        state = {
            "goal": self.goal,
            "criteria": self.criteria,
            "team_name": self.team_name,
            "stats": {
                "iterations": self.stats.iterations,
                "executor_restarts": self.stats.executor_restarts,
                "pressure_upgrades": self.stats.pressure_upgrades,
                "last_check_time": self.stats.last_check_time,
                "consecutive_inactive": self.stats.consecutive_inactive
            },
            "pressure_level": self.pressure_level.value,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load_state(self) -> dict:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def write_goal_files(self):
        """写入Goal和Criteria文件"""
        with open(self.goal_file, 'w') as f:
            f.write(f"# Goal\n\n{self.goal}\n")

        with open(self.criteria_file, 'w') as f:
            f.write(f"# Criteria\n\n{self.criteria}\n")

        self.log("INFO", f"Goal文件: {self.goal}")
        self.log("INFO", f"Criteria文件: {self.criteria}")

    def run_bash(self, cmd: str, timeout: int = 30) -> Tuple[int, str, str]:
        """运行bash命令"""
        try:
            # 使用cyberteam alias
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

    def check_criteria(self) -> bool:
        """
        检查是否满足成功标准
        这是Goal-Driven的关键 - 必须实际评估目标是否达成
        """
        self.log("INFO", f"检查Criteria: {self.criteria}")

        # 读取Executor状态
        executor_state = self.load_executor_state()

        # 如果Executor报告完成，检查是否真正满足
        if executor_state.get("goal_achieved"):
            self.log("SUCCESS", "Executor报告目标达成")
            return True

        # 根据目标类型进行实际检查
        goal_lower = self.goal.lower()

        # 文件创建任务
        if "test.txt" in goal_lower or "hello" in goal_lower:
            test_file = Path("/tmp/test.txt")
            if test_file.exists():
                content = test_file.read_text().strip()
                expected = "hello world"
                if expected in content.lower():
                    self.log("SUCCESS", f"✓ Criteria满足: 文件存在且内容正确")
                    return True
                else:
                    self.log("WARNING", f"文件内容不匹配: 期望'{expected}', 实际'{content}'")
            else:
                self.log("WARNING", f"文件不存在: {test_file}")

        return False

    def load_executor_state(self) -> dict:
        """加载Executor状态"""
        executor_state_file = self.work_dir / "master-loop" / "autoresearch_state.json"
        if executor_state_file.exists():
            with open(executor_state_file, 'r') as f:
                return json.load(f)
        return {}

    def check_executor_status(self) -> ExecutorStatus:
        """
        检查Executor状态
        """
        # 检查进程是否存活
        if self.executor_pid:
            try:
                os.kill(self.executor_pid, 0)  # 检查进程是否存在
            except OSError:
                self.log("WARNING", f"Executor进程 {self.executor_pid} 不存在")
                return ExecutorStatus.INACTIVE

        # 检查ClawTeam board
        returncode, stdout, stderr = self.run_bash(
            f"cyberteam board show {self.team_name}",
            timeout=15
        )

        if returncode != 0:
            self.log("WARNING", f"Board查询失败: {stderr}")
            return ExecutorStatus.UNKNOWN

        # 解析board输出
        output = stdout.lower()

        # 检查executor是否在运行
        if "executor" in output:
            # 检查是否有inactive/error状态
            if "inactive" in output or "error" in output:
                return ExecutorStatus.INACTIVE
            return ExecutorStatus.RUNNING

        # 没有executor
        return ExecutorStatus.UNKNOWN

    def spawn_executor(self) -> bool:
        """
        启动Executor
        """
        self.log("MASTER", "=" * 50)
        self.log("MASTER", f"启动AutoResearch Executor...")
        self.log("MASTER", f"目标: {self.goal}")
        self.log("MASTER", "=" * 50)

        # 启动Executor作为后台进程
        executor_script = self.work_dir / "master-loop" / "autoresearch_executor.py"

        try:
            # 使用subprocess.Popen启动，保持PID跟踪
            process = subprocess.Popen(
                ["python3", str(executor_script)],
                cwd=str(self.work_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            self.executor_pid = process.pid
            self.log("SUCCESS", f"Executor已启动 (PID: {self.executor_pid})")
            return True

        except Exception as e:
            self.log("ERROR", f"启动Executor失败: {e}")
            return False

    def restart_executor(self):
        """
        重启Executor
        """
        self.stats.executor_restarts += 1
        self.log("WARNING", f"重启Executor (第{self.stats.executor_restarts}次)")

        # 终止现有Executor
        if self.executor_pid:
            try:
                os.kill(self.executor_pid, 9)
                self.log("INFO", f"已终止旧进程: {self.executor_pid}")
            except OSError:
                pass

        # 重新启动
        self.spawn_executor()

    def apply_pressure(self, level: PressureLevel):
        """
        应用PUA压力
        """
        if level == self.pressure_level:
            return  # 同一等级不重复打印

        self.pressure_level = level
        self.stats.pressure_upgrades += 1

        self.log("PUA", "=" * 60)
        self.log("PUA", "🔴 PUA压力升级!")
        self.log("PUA", f"压力等级: L{level.value}")
        self.log("PUA", "=" * 60)

        pressure_actions = {
            PressureLevel.L0_NONE: "正常执行",
            PressureLevel.L1: "💡 换一种根本不同的方法，别再用老方法！",
            PressureLevel.L2: "🔍 去WebSearch！去读源码！找出根本原因！",
            PressureLevel.L3: "📋 执行7步检查清单，每步都要有证据！",
            PressureLevel.L4: "🚨 绝望模式！这是最后机会！列出所有可能的解法！"
        }

        self.log("PUA", f"动作: {pressure_actions.get(level, '继续尝试')}")

        # 记录压力日志
        pressure_log = self.work_dir / "master-loop" / "pressure_log.txt"
        with open(pressure_log, 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] L{level.value} - {pressure_actions.get(level)}\n")

    def should_restart(self) -> bool:
        """判断是否应该重启Executor"""
        # 达到最大重启次数
        if self.stats.executor_restarts >= self.max_restarts:
            self.log("WARNING", f"已达到最大重启次数 ({self.max_restarts})")
            return False

        # 检查是否有进展
        state = self.load_executor_state()
        current_attempt = state.get("current_attempt", 0)

        # 如果连续多次尝试没有进展
        if self.stats.consecutive_inactive >= 3:
            self.log("WARNING", "连续多次无进展，考虑重启")
            return True

        return True

    async def run_loop(self):
        """
        核心循环 - 持续运行直到Criteria满足
        这是Goal-Driven模式的真正实现
        """
        self.log("MASTER", "=" * 60)
        self.log("MASTER", "🚀 AutoResearch Master 启动")
        self.log("MASTER", "=" * 60)
        self.log("MASTER", f"目标: {self.goal}")
        self.log("MASTER", f"Criteria: {self.criteria}")
        self.log("MASTER", f"检查间隔: {self.check_interval}秒")
        self.log("MASTER", f"最大重启次数: {self.max_restarts}")
        self.log("MASTER", "=" * 60)

        # 写入Goal和Criteria
        self.write_goal_files()

        # 启动初始Executor
        if not self.spawn_executor():
            self.log("ERROR", "无法启动Executor，退出")
            return False

        # 主循环
        while self.stats.iterations < self.max_iterations:
            self.stats.iterations += 1
            self.stats.last_check_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.save_state()

            self.log("MASTER", "-" * 60)
            self.log("MASTER", f"📍 迭代 #{self.stats.iterations}")
            self.log("MASTER", f"   重启次数: {self.stats.executor_restarts}")
            self.log("MASTER", f"   压力等级: L{self.pressure_level.value}")

            # 1. 检查Criteria
            if self.check_criteria():
                self.log("SUCCESS", "=" * 60)
                self.log("SUCCESS", "🎉 Goal Achieved! 目标达成!")
                self.log("SUCCESS", f"总迭代次数: {self.stats.iterations}")
                self.log("SUCCESS", f"Executor重启次数: {self.stats.executor_restarts}")
                self.log("SUCCESS", "=" * 60)
                return True

            # 2. 检查Executor状态
            status = self.check_executor_status()
            self.log("INFO", f"Executor状态: {status.value}")

            if status == ExecutorStatus.INACTIVE or status == ExecutorStatus.UNKNOWN:
                self.stats.consecutive_inactive += 1

                # 升级压力
                if self.stats.consecutive_inactive >= 4:
                    self.apply_pressure(PressureLevel.L4)
                elif self.stats.consecutive_inactive >= 3:
                    self.apply_pressure(PressureLevel.L3)
                elif self.stats.consecutive_inactive >= 2:
                    self.apply_pressure(PressureLevel.L2)
                else:
                    self.apply_pressure(PressureLevel.L1)

                # 判断是否重启
                if self.should_restart():
                    self.restart_executor()
                else:
                    self.log("ERROR", "停止重启，任务无法完成")

            elif status == ExecutorStatus.RUNNING:
                self.stats.consecutive_inactive = 0
                # 检查Executor是否有进展
                state = self.load_executor_state()
                attempts = state.get("current_attempt", 0)
                self.log("INFO", f"Executor已尝试: {attempts}次")

            # 3. 等待
            self.log("INFO", f"等待 {self.check_interval}秒...")
            await asyncio.sleep(self.check_interval)

        # 达到最大迭代
        self.log("ERROR", f"达到最大迭代次数 ({self.max_iterations})")
        self.log("ERROR", "任务超时")

        return False


async def main():
    """入口函数"""
    master = AutoResearchMaster(
        goal="创建一个测试文件 /tmp/test.txt，内容是hello world",
        criteria="文件存在且内容正确",
        team_name="autoresearch-team",
        check_interval=10,
        max_restarts=5
    )

    success = await master.run_loop()

    # 最终检查
    if Path("/tmp/test.txt").exists():
        print(f"\n最终结果: {Path('/tmp/test.txt').read_text()}")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
