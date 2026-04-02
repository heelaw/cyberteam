#!/usr/bin/env python3
"""
思考天团 Goal-Driven Master Agent
实现真正的循环控制 - 直到Criteria满足才停止
"""

import asyncio
import subprocess
import time
import json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Optional

# Color codes for terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class PressureLevel(Enum):
    L1 = 1  # 换一种根本不同的方法
    L2 = 2  # WebSearch + 读源码
    L3 = 3  # 执行7步检查清单
    L4 = 4  # 绝望模式 - 重启


@dataclass
class TaskResult:
    success: bool
    output: str
    error: Optional[str] = None


class GoalDrivenMaster:
    """Goal-Driven Master Agent - 持续运行直到目标达成"""

    def __init__(
        self,
        goal: str,
        criteria: str,
        team_name: str = "think-tank",
        check_interval: int = 60,  # 1分钟（测试用，生产环境5分钟）
        max_retries: int = 10
    ):
        self.goal = goal
        self.criteria = criteria
        self.team_name = team_name
        self.check_interval = check_interval
        self.max_retries = max_retries
        self.failure_count = 0
        self.iteration = 0

        # Working directory
        self.work_dir = Path(__file__).parent.parent
        self.goal_file = self.work_dir / "goal.md"
        self.criteria_file = self.work_dir / "criteria.md"
        self.state_file = self.work_dir / "master-loop" / "state.json"

    def log(self, level: str, message: str):
        """带颜色的日志输出"""
        color = {
            "INFO": BLUE,
            "SUCCESS": GREEN,
            "WARNING": YELLOW,
            "ERROR": RED,
            "PUA": RED
        }.get(level, NC)
        print(f"{color}[{level}]{NC} {message}")

    def save_state(self):
        """保存当前状态"""
        state = {
            "goal": self.goal,
            "criteria": self.criteria,
            "failure_count": self.failure_count,
            "iteration": self.iteration,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> dict:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def write_goal_and_criteria(self):
        """写入Goal和Criteria文件"""
        with open(self.goal_file, 'w') as f:
            f.write(f"# Goal\n\n{self.goal}\n")

        with open(self.criteria_file, 'w') as f:
            f.write(f"# Criteria\n\n{self.criteria}\n")

        self.log("INFO", f"Goal: {self.goal}")
        self.log("INFO", f"Criteria: {self.criteria}")

    def check_criteria(self) -> bool:
        """
        检查是否满足成功标准
        这是关键：需要实际评估结果是否满足Criteria
        """
        self.log("INFO", f"检查Criteria: {self.criteria}")

        # 读取当前状态
        state = self.load_state()

        # 根据不同类型的goal进行不同的检查
        goal_lower = self.goal.lower()

        # 简单测试任务：创建文件
        if "test.txt" in goal_lower or "hello" in goal_lower:
            test_file = Path("/tmp/test.txt")
            if test_file.exists():
                content = test_file.read_text().strip()
                expected = "hello world"
                if expected in content.lower():
                    self.log("SUCCESS", f"文件存在且内容正确: {content}")
                    return True
                else:
                    self.log("WARNING", f"文件内容不匹配: 期望'{expected}', 实际'{content}'")
                    return False
            else:
                self.log("WARNING", f"文件不存在: {test_file}")
                return False

        # 检查任务完成状态
        if "state" in state:
            if state.get("task_completed"):
                return True

        return False

    def apply_pua_pressure(self):
        """PUA压力升级"""
        level = min(self.failure_count, 4)

        if level <= 0:
            return

        pressure = PressureLevel(level)

        self.log("PUA", "=" * 50)
        self.log("PUA", f"L{level} 压力升级!")

        messages = {
            1: "换一种根本不同的方法",
            2: "WebSearch + 读源码，必须找出根本原因",
            3: "执行7步检查清单，每步都要证据",
            4: "绝望模式！你要被淘汰了！",
        }

        self.log("PUA", f"压力内容: {messages.get(level, '继续尝试')}")
        self.log("PUA", "=" * 50)

    def run_cyberteam(self, args: list, timeout: int = 30) -> tuple:
        """通过bash运行cyberteam命令（因为cyberteam是alias）"""
        # 使用shlex正确转义参数
        import shlex
        cmd_parts = [shlex.quote(arg) for arg in args]
        cmd = " ".join(cmd_parts)
        full_cmd = f"source ~/.cyberteam-venv/bin/activate && cyberteam {cmd}"

        try:
            result = subprocess.run(
                ["bash", "-c", full_cmd],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def restart_executor(self):
        """重启Executor Agent"""
        self.log("INFO", "重启Executor Agent...")

        try:
            # 先终止现有executor
            self.run_cyberteam(["lifecycle", "request-shutdown", self.team_name, "executor"], timeout=10)
            time.sleep(2)

            # 重新启动executor
            returncode, stdout, stderr = self.run_cyberteam([
                "spawn", "--team", self.team_name,
                "--agent-name", "executor",
                "--task", f"创建文件 /tmp/test.txt，内容是 hello world"
            ], timeout=30)

            if returncode == 0:
                self.log("SUCCESS", "Executor重启成功")
            else:
                self.log("ERROR", f"Executor重启失败: {stderr}")
                self.log("ERROR", f"stdout: {stdout}")

        except Exception as e:
            self.log("ERROR", f"重启Executor失败: {e}")

    def check_executor_status(self) -> str:
        """检查Executor状态"""
        try:
            returncode, stdout, stderr = self.run_cyberteam(
                ["--json", "board", "show", self.team_name],
                timeout=15
            )

            if returncode == 0:
                # 解析输出
                output = stdout
                # 检查是否有inactive的agent
                if "inactive" in output.lower() or "error" in output.lower():
                    return "inactive"
                return "running"

        except Exception as e:
            self.log("WARNING", f"检查状态失败: {e}")

        return "unknown"

    def mark_task_complete(self):
        """标记任务完成"""
        state = self.load_state()
        state["task_completed"] = True
        state["completion_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        self.log("SUCCESS", "=" * 50)
        self.log("SUCCESS", "Goal Achieved! 目标达成!")
        self.log("SUCCESS", "=" * 50)

    async def run_loop(self):
        """核心循环 - 持续运行直到Criteria满足"""
        self.log("INFO", "=" * 50)
        self.log("INFO", "Goal-Driven Master Agent 启动")
        self.log("INFO", f"目标: {self.goal}")
        self.log("INFO", f"检查间隔: {self.check_interval}秒")
        self.log("INFO", "=" * 50)

        # 写入Goal和Criteria
        self.write_goal_and_criteria()

        # 初始启动Executor
        self.log("INFO", "初始启动Executor Agent...")
        self.restart_executor()
        self.log("INFO", "Executor已启动，等待执行...")

        # 主循环
        while True:
            self.iteration += 1
            self.save_state()

            self.log("INFO", "-" * 50)
            self.log("INFO", f"迭代 #{self.iteration}")

            # 1. 检查是否满足Criteria
            if self.check_criteria():
                self.mark_task_complete()
                break

            # 2. 检查失败次数
            if self.failure_count >= self.max_retries:
                self.log("ERROR", f"达到最大重试次数 ({self.max_retries})")
                self.log("ERROR", "任务失败，退出")
                break

            # 3. 检查Executor状态
            status = self.check_executor_status()
            self.log("INFO", f"Executor状态: {status}")

            if status == "inactive" or status == "unknown":
                # 4. 应用PUA压力
                self.apply_pua_pressure()

                # 5. 重启Executor
                self.restart_executor()
                self.failure_count += 1

            # 6. 等待
            self.log("INFO", f"等待 {self.check_interval}秒...")
            await asyncio.sleep(self.check_interval)

        self.log("INFO", "Master Agent 结束")
        return self.check_criteria()


async def main():
    """入口函数"""
    # 简单测试任务
    master = GoalDrivenMaster(
        goal="创建一个测试文件 /tmp/test.txt，内容是'hello world'",
        criteria="文件存在且内容正确",
        team_name="think-tank-test2",
        check_interval=15,  # 15秒（给executor时间创建文件）
        max_retries=5
    )

    success = await master.run_loop()
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
