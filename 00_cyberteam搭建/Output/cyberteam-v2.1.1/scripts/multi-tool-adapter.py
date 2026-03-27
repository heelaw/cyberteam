#!/usr/bin/env python3
"""
CyberTeam v2.1 -- 多工具适配层

功能:
- 统一接口适配多种 AI 编程工具
- 自动检测可用工具
- 动态路由到最优工具
- 跨工具状态同步

支持的工具:
- claude     : Claude Code
- cursor     : Cursor
- windsurf   : Windsurf
- copilot    : GitHub Copilot
- aider     : Aider
- codestral  : Codestral
- lovable    : Lovable
- cline      : Cline
- gemini     : Gemini CLI
- continue   : Continue
- opencode   : OpenCode
- qwen       : Qwen Code
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class TaskType(Enum):
    """任务类型枚举"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    RESEARCH = "research"
    ARCHITECTURE = "architecture"


@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    display_name: str
    command: str
    config_path: str
    agent_dir: str
    detected: bool = False
    version: str = ""


@dataclass
class Task:
    """任务定义"""
    type: TaskType
    description: str
    context: dict = field(default_factory=dict)
    priority: int = 1  # 1-5, 5 最高
    preferred_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)


class MultiToolAdapter:
    """多工具适配器"""

    SUPPORTED_TOOLS = {
        'claude': ToolInfo(
            name='claude',
            display_name='Claude Code',
            command='claude',
            config_path='~/.claude/',
            agent_dir='~/.claude/agents/',
        ),
        'cursor': ToolInfo(
            name='cursor',
            display_name='Cursor',
            command='cursor',
            config_path='.cursor/',
            agent_dir='.cursor/rules/',
        ),
        'windsurf': ToolInfo(
            name='windsurf',
            display_name='Windsurf',
            command='windsurf',
            config_path='.windsurfrules',
            agent_dir='.windsurfrules',
        ),
        'copilot': ToolInfo(
            name='copilot',
            display_name='GitHub Copilot',
            command='code',
            config_path='~/.github/agents/',
            agent_dir='~/.github/agents/',
        ),
        'aider': ToolInfo(
            name='aider',
            display_name='Aider',
            command='aider',
            config_path='CONVENTIONS.md',
            agent_dir='CONVENTIONS.md',
        ),
        'codestral': ToolInfo(
            name='codestral',
            display_name='Codestral',
            command='codestral',
            config_path='~/.codestral/',
            agent_dir='~/.codestral/agents/',
        ),
        'lovable': ToolInfo(
            name='lovable',
            display_name='Lovable',
            command='lovable',
            config_path='~/.lovable/',
            agent_dir='~/.lovable/agents/',
        ),
        'cline': ToolInfo(
            name='cline',
            display_name='Cline',
            command='cline',
            config_path='~/.cline/',
            agent_dir='~/.cline/rules/',
        ),
        'gemini': ToolInfo(
            name='gemini',
            display_name='Gemini CLI',
            command='gemini',
            config_path='~/.gemini/extensions/',
            agent_dir='~/.gemini/antigravity/skills/',
        ),
        'continue': ToolInfo(
            name='continue',
            display_name='Continue',
            command='continue',
            config_path='~/.continue/',
            agent_dir='~/.continue/config.json',
        ),
        'opencode': ToolInfo(
            name='opencode',
            display_name='OpenCode',
            command='opencode',
            config_path='.opencode/',
            agent_dir='.opencode/agents/',
        ),
        'qwen': ToolInfo(
            name='qwen',
            display_name='Qwen Code',
            command='qwen',
            config_path='.qwen/',
            agent_dir='.qwen/agents/',
        ),
    }

    # 任务类型到工具的映射
    TASK_TOOL_PREFERENCES = {
        TaskType.CODE_GENERATION: ['claude', 'copilot', 'cursor', 'windsurf'],
        TaskType.CODE_REVIEW: ['claude', 'copilot', 'aider'],
        TaskType.BUG_FIX: ['claude', 'aider', 'cline'],
        TaskType.REFACTORING: ['claude', 'aider', 'copilot'],
        TaskType.DOCUMENTATION: ['claude', 'continue', 'gemini'],
        TaskType.TESTING: ['claude', 'copilot', 'aider'],
        TaskType.DEPLOYMENT: ['claude', 'copilot', 'qwen'],
        TaskType.RESEARCH: ['gemini', 'claude', 'continue'],
        TaskType.ARCHITECTURE: ['claude', 'gemini', 'copilot'],
    }

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.detected_tools: list[str] = []
        self.tool_states: dict = {}

    def detect_tool(self, tool_name: str) -> bool:
        """检测单个工具是否可用"""
        tool = self.SUPPORTED_TOOLS.get(tool_name)
        if not tool:
            return False

        # 检查命令是否存在
        if shutil.which(tool.command):
            tool.detected = True
            # 尝试获取版本
            try:
                result = subprocess.run(
                    [tool.command, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                tool.version = result.stdout.strip() or result.stderr.strip() or "unknown"
            except:
                tool.version = "unknown"
            return True

        # 检查配置目录是否存在
        config_path = Path(tool.config_path).expanduser()
        if config_path.exists():
            tool.detected = True
            return True

        # 项目级工具检查
        if tool.name in ['cursor', 'windsurf', 'aider', 'opencode', 'qwen']:
            project_config = self.project_root / tool.config_path
            if project_config.exists():
                tool.detected = True
                return True

        return False

    def detect_tools(self) -> list[str]:
        """检测所有可用工具"""
        self.detected_tools = []
        for tool_name in self.SUPPORTED_TOOLS:
            if self.detect_tool(tool_name):
                self.detected_tools.append(tool_name)
        return self.detected_tools

    def route(self, task: Task) -> list[str]:
        """路由任务到最优工具"""
        candidates = []

        # 优先级: 首选工具 > 任务类型偏好 > 检测到的工具
        if task.preferred_tools:
            for tool in task.preferred_tools:
                if tool in self.detected_tools and tool not in task.blocked_tools:
                    candidates.append(tool)

        if not candidates:
            preferred = self.TASK_TOOL_PREFERENCES.get(task.type, [])
            for tool in preferred:
                if tool in self.detected_tools and tool not in task.blocked_tools:
                    candidates.append(tool)

        # 如果没有匹配的回退到任何检测到的工具
        if not candidates:
            for tool in self.detected_tools:
                if tool not in task.blocked_tools:
                    candidates.append(tool)

        return candidates

    def execute_on_tool(self, tool_name: str, task: Task) -> dict:
        """在指定工具上执行任务"""
        result = {
            'success': False,
            'tool': tool_name,
            'task': task.description,
            'output': '',
            'error': ''
        }

        if tool_name not in self.detected_tools:
            result['error'] = f"工具 {tool_name} 未检测到"
            return result

        tool = self.SUPPORTED_TOOLS[tool_name]

        try:
            if tool_name == 'claude':
                result['output'] = self._execute_claude(task)
            elif tool_name == 'aider':
                result['output'] = self._execute_aider(task)
            elif tool_name == 'gemini':
                result['output'] = self._execute_gemini(task)
            else:
                result['output'] = f"工具 {tool_name} 执行接口尚未实现"

            result['success'] = True
        except Exception as e:
            result['error'] = str(e)

        return result

    def _execute_claude(self, task: Task) -> str:
        """通过 Claude Code 执行"""
        cmd = ['claude', '-p', task.description]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout or result.stderr

    def _execute_aider(self, task: Task) -> str:
        """通过 Aider 执行"""
        cmd = ['aider', '--message', task.description]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout or result.stderr

    def _execute_gemini(self, task: Task) -> str:
        """通过 Gemini CLI 执行"""
        cmd = ['gemini', 'ask', task.description]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout or result.stderr

    def sync_state(self, source_tool: str, target_tool: str) -> bool:
        """同步两个工具之间的状态"""
        if source_tool not in self.SUPPORTED_TOOLS or target_tool not in self.SUPPORTED_TOOLS:
            return False

        source = self.SUPPORTED_TOOLS[source_tool]
        target = self.SUPPORTED_TOOLS[target_tool]

        # 读取源状态
        source_path = Path(source.agent_dir).expanduser()
        if not source_path.exists():
            return False

        # 这里应该实现具体的同步逻辑
        # 例如：复制 agent 定义、同步配置等
        return True

    def generate_report(self) -> dict:
        """生成工具状态报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'detected_tools': [
                {
                    'name': tool,
                    'display_name': self.SUPPORTED_TOOLS[tool].display_name,
                    'version': self.SUPPORTED_TOOLS[tool].version,
                }
                for tool in self.detected_tools
            ],
            'supported_tools': len(self.SUPPORTED_TOOLS),
            'available_tools': len(self.detected_tools),
        }


def main():
    parser = argparse.ArgumentParser(
        description='CyberTeam v2.1 -- 多工具适配器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检测所有可用工具
  python3 multi-tool-adapter.py --detect

  # 列出工具状态
  python3 multi-tool-adapter.py --list

  # 获取工具推荐
  python3 multi-tool-adapter.py --recommend --task "代码审查"
        """
    )

    parser.add_argument('--detect', action='store_true', help='检测可用工具')
    parser.add_argument('--list', action='store_true', help='列出所有工具状态')
    parser.add_argument('--recommend', action='store_true', help='获取工具推荐')
    parser.add_argument('--task', type=str, help='任务描述')
    parser.add_argument('--project', '-p', type=str, help='项目根目录')
    parser.add_argument('--output', '-o', type=str, help='输出文件 (JSON)')

    args = parser.parse_args()

    adapter = MultiToolAdapter(args.project)

    if args.detect or args.list or args.recommend:
        print("CyberTeam v2.1 -- 工具检测\n")
        detected = adapter.detect_tools()
        print(f"检测到 {len(detected)} 个可用工具:\n")
        for tool in detected:
            t = adapter.SUPPORTED_TOOLS[tool]
            print(f"  {t.display_name:20} ({tool}) - v{t.version}")

    if args.recommend and args.task:
        print(f"\n任务: {args.task}")
        # 简单匹配
        task_type = TaskType.CODE_GENERATION
        for tt in TaskType:
            if tt.value.replace('_', '') in args.task.lower().replace(' ', ''):
                task_type = tt
                break

        task = Task(type=task_type, description=args.task)
        recommended = adapter.route(task)
        print(f"推荐工具: {', '.join(recommended) if recommended else '无'}")

    report = adapter.generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n报告已保存到: {args.output}")
    else:
        print(json.dumps(report, indent=2))

    return 0


if __name__ == '__main__':
    sys.exit(main())
