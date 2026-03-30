"""
Claude Code CLI 集成模块 - 真实实现

核心能力：
1. 启动 Claude Code 会话
2. 发送消息并获取响应
3. 执行完整任务
4. 管理会话状态
"""
import asyncio
import subprocess
import os
import json
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClaudeConfig:
    """Claude 配置"""
    model: str = "haiku"
    max_tokens: int = 4096
    temperature: float = 0.7
    workspace: str = ""


class ClaudeCLI:
    """
    Claude Code CLI 真实集成

    使用 subprocess 调用 claude CLI 进行实际交互
    """

    def __init__(self, config: Optional[ClaudeConfig] = None):
        self.config = config or ClaudeConfig()
        self._claude_path: Optional[str] = None

    def _find_claude_binary(self) -> str:
        """查找 Claude CLI 路径"""
        if self._claude_path:
            return self._claude_path

        # 尝试常见路径
        candidates = [
            'claude',
            '/Users/cyberwiz/.nvm/versions/node/v24.14.0/bin/claude',
        ]

        for cmd in candidates:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if result.returncode == 0:
                    self._claude_path = cmd
                    logger.info(f"Found Claude CLI: {cmd}")
                    return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue

        # 默认回退
        return 'claude'

    def run(self, prompt: str, input_text: str = "") -> str:
        """
        运行 Claude CLI 并获取响应

        Args:
            prompt: 给 Claude 的提示词
            input_text: 可选的输入文本

        Returns:
            Claude 的响应文本
        """
        cmd = [
            self._find_claude_binary(),
            '--print',
            '--model', self.config.model,
            '-p', prompt
        ]

        logger.info(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.config.workspace or os.getcwd()
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr}")
                return f"[错误] {result.stderr}"

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            return "[错误] 执行超时"
        except Exception as e:
            logger.error(f"Claude CLI exception: {e}")
            return f"[错误] {str(e)}"

    async def run_streaming(self, prompt: str, input_text: str = "") -> AsyncIterator[str]:
        """
        流式运行 Claude CLI

        Args:
            prompt: 给 Claude 的提示词
            input_text: 可选的输入文本

        Yields:
            流式响应片段
        """
        cmd = [
            self._find_claude_binary(),
            '--print',
            '--model', self.config.model,
            '-p', prompt
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config.workspace or os.getcwd()
            )

            stdout, stderr = process.communicate(
                input=input_text,
                timeout=120
            )

            if stderr:
                logger.warning(f"Claude stderr: {stderr}")

            # 按行输出
            for line in stdout.split('\n'):
                if line.strip():
                    yield line

        except subprocess.TimeoutExpired:
            yield "[错误] 执行超时"
        except Exception as e:
            yield f"[错误] {str(e)}"
        """
        流式运行 Claude CLI

        Args:
            prompt: 给 Claude 的提示词
            input_text: 可选的输入文本

        Yields:
            流式响应片段
        """
        cmd = [
            self._find_claude_binary(),
            '--print',
            '--model', self.config.model,
            '-p', prompt
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config.workspace or os.getcwd()
            )

            stdout, stderr = process.communicate(
                input=input_text,
                timeout=120
            )

            if stderr:
                logger.warning(f"Claude stderr: {stderr}")

            # 按行输出
            for line in stdout.split('\n'):
                if line.strip():
                    yield line

        except subprocess.TimeoutExpired:
            yield "[错误] 执行超时"
        except Exception as e:
            yield f"[错误] {str(e)}"


class DigitalEmployee:
    """
    数字员工 - 真实连接 Claude CLI
    """

    def __init__(
        self,
        id: str,
        name: str,
        role: str,
        description: str = "",
        skills: list[str] = None,
        system_prompt: str = ""
    ):
        self.id = id
        self.name = name
        self.role = role
        self.description = description
        self.skills = skills or []
        self.system_prompt = system_prompt
        self.cli = ClaudeCLI()

    def _build_prompt(self, task: str) -> str:
        """构建完整的提示词"""
        prompt = self.system_prompt or f"""你是一个专业的 {self.role}。"""

        if self.skills:
            prompt += f"\n\n专业技能: {', '.join(self.skills)}"

        prompt += f"\n\n任务: {task}"

        return prompt

    def execute(self, task: str, input_text: str = "") -> str:
        """执行任务"""
        prompt = self._build_prompt(task)
        return self.cli.run(prompt, input_text)

    def execute_streaming(self, task: str, input_text: str = "") -> AsyncIterator[str]:
        """流式执行任务"""
        prompt = self._build_prompt(task)
        yield from self.cli.run_streaming(prompt, input_text)


# === 测试代码 ===
if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("【真实Claude CLI测试】")
        print("=" * 60)

        # 创建 CEO
        ceo = DigitalEmployee(
            id="test-ceo",
            name="CEO",
            role="首席执行官",
            description="负责战略决策",
            skills=["战略规划", "团队管理"]
        )

        print(f"✅ 创建数字员工: {ceo.name}")

        # 执行真实任务
        print("\n⏳ 正在执行任务...")
        result = ceo.execute("用 Python 写一个快速排序函数")

        print("\n--- 执行结果 ---")
        print(result)
        print("\n" + "=" * 60)
        print("✅ 测试完成")
        print("=" * 60)

    asyncio.run(test())
