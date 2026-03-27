#!/usr/bin/env python3
"""
CyberTeam v2.1 -- Agent 定义转换工具

功能:
- 将通用 Agent 定义转换为特定工具格式
- 支持: Claude Code / Cursor / Windsurf / CoSTAR / Roo Code / Continue / GitHub Copilot / Aider / Codestral / Lovable / Cline / Gemini CLI / VS Code Agent
- 验证 Agent 定义完整性
- 生成部署配置

使用方法:
    python3 agent-converter.py --tool claude-code --input agents/
    python3 agent-converter.py --all --input agents/ --output integrations/
"""

import argparse
import os
import re
import sys
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class AgentDefinition:
    """Agent 定义数据结构"""
    name: str
    description: str
    color: str = "#6B7280"
    emoji: Optional[str] = None
    vibe: Optional[str] = None
    tools: Optional[str] = None
    body: str = ""
    source_file: str = ""

    # 元数据
    category: str = ""
    slug: str = ""

    def __post_init__(self):
        if not self.slug:
            self.slug = self._slugify(self.name)
        if not self.category:
            self.category = self._infer_category()

    @staticmethod
    def _slugify(text: str) -> str:
        """转换为 kebab-case"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = re.sub(r'^-|-$', '', text)
        return text

    def _infer_category(self) -> str:
        """根据名称推断分类"""
        name_lower = self.name.lower()
        categories = {
            'frontend': ['frontend', 'ui', 'css', 'html', 'react', 'vue'],
            'backend': ['backend', 'api', 'server', 'database'],
            'fullstack': ['fullstack', 'full-stack'],
            'devops': ['devops', 'sre', 'infrastructure', 'deploy'],
            'security': ['security', 'audit', 'vulnerability'],
            'data': ['data', 'analytics', 'ml', 'ai'],
            'mobile': ['mobile', 'ios', 'android', 'flutter'],
            'design': ['design', 'ui/ux', 'figma'],
            'qa': ['qa', 'test', 'quality'],
            'product': ['product', 'pm', 'requirement'],
        }
        for cat, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return cat
        return 'general'


class AgentConverter:
    """Agent 定义转换器"""

    SUPPORTED_TOOLS = [
        'claude-code',
        'copilot',
        'cursor',
        'windsurf',
        'opencode',
        'openclaw',
        'aider',
        'antigravity',
        'gemini-cli',
        'qwen',
        'roo-code',
        'continue',
        'codestral',
        'lovable',
        'cline',
    ]

    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.agents: list[AgentDefinition] = []
        self.today = datetime.now().strftime('%Y-%m-%d')

    def parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """解析 YAML frontmatter"""
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content[3:].split('---', 1)
            if len(parts) >= 2:
                fm_text, body = parts
                body = body.lstrip('\n')

                # 简单的 YAML 解析
                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')

        return frontmatter, body

    def load_agent(self, file_path: Path) -> Optional[AgentDefinition]:
        """加载单个 Agent 定义文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            fm, body = self.parse_frontmatter(content)

            if not fm.get('name'):
                print(f"警告: {file_path} 缺少 name 字段")
                return None

            return AgentDefinition(
                name=fm.get('name', ''),
                description=fm.get('description', ''),
                color=fm.get('color', '#6B7280'),
                emoji=fm.get('emoji'),
                vibe=fm.get('vibe'),
                tools=fm.get('tools'),
                body=body,
                source_file=str(file_path),
            )
        except Exception as e:
            print(f"错误: 加载 {file_path} 失败: {e}")
            return None

    def load_agents(self, pattern: str = "**/*.md") -> list[AgentDefinition]:
        """加载所有 Agent 定义"""
        self.agents = []
        for file_path in self.source_dir.glob(pattern):
            if file_path.name.startswith('.'):
                continue
            agent = self.load_agent(file_path)
            if agent:
                self.agents.append(agent)
        return self.agents

    def validate(self, agent: AgentDefinition) -> list[str]:
        """验证 Agent 定义"""
        errors = []

        if not agent.name:
            errors.append("缺少 name 字段")

        if not agent.description:
            errors.append("缺少 description 字段")

        if len(agent.body) < 100:
            errors.append("body 内容过少 (< 100 字符)")

        # 检查必要章节
        required_sections = ['Identity', 'Core Mission', 'Critical Rules']
        for section in required_sections:
            if section.lower() not in agent.body.lower():
                errors.append(f"建议添加章节: {section}")

        return errors

    def validate_all(self) -> dict:
        """验证所有 Agent"""
        results = {
            'total': len(self.agents),
            'passed': 0,
            'failed': 0,
            'agents': []
        }

        for agent in self.agents:
            errors = self.validate(agent)
            status = 'passed' if not errors else 'failed'
            if not errors:
                results['passed'] += 1
            else:
                results['failed'] += 1
            results['agents'].append({
                'name': agent.name,
                'status': status,
                'errors': errors
            })

        return results

    # =========================================================================
    # 格式转换器
    # =========================================================================

    def convert_claude_code(self, agent: AgentDefinition) -> str:
        """转换为 Claude Code 格式"""
        fm = f"""---
name: {agent.name}
description: {agent.description}
color: {agent.color}
"""
        if agent.emoji:
            fm += f"emoji: {agent.emoji}\n"
        return fm + f"---\n{agent.body}"

    def convert_copilot(self, agent: AgentDefinition) -> str:
        """转换为 GitHub Copilot 格式"""
        return self.convert_claude_code(agent)

    def convert_cursor(self, agent: AgentDefinition) -> str:
        """转换为 Cursor .mdc 格式"""
        fm = f"""---
description: {agent.description}
globs: ""
alwaysApply: false
---
"""
        return fm + agent.body

    def convert_windsurf(self, agent: AgentDefinition) -> str:
        """转换为 Windsurf .windsurfrules 格式"""
        header = f"""================================================================================
## {agent.name}
{agent.description}
================================================================================

"""
        return header + agent.body

    def convert_opencode(self, agent: AgentDefinition) -> str:
        """转换为 OpenCode 格式"""
        color = self._resolve_color(agent.color)
        fm = f"""---
name: {agent.name}
description: {agent.description}
mode: subagent
color: '{color}'
---
"""
        return fm + agent.body

    def convert_openclaw(self, agent: AgentDefinition) -> tuple[dict, str, str]:
        """转换为 OpenClaw 格式，返回 (IDENTITY, SOUL, AGENTS)"""
        # IDENTITY
        identity = f"# {agent.name}\n{agent.description}"
        if agent.emoji and agent.vibe:
            identity = f"# {agent.emoji} {agent.name}\n{agent.vibe}"

        # SOUL vs AGENTS 分离
        soul_keywords = ['identity', 'communication', 'style', 'critical rule', 'rules you must follow']
        soul_lines = []
        agents_lines = []

        current_target = 'agents'
        for line in agent.body.split('\n'):
            if line.startswith('##'):
                header_lower = line.lower()
                if any(kw in header_lower for kw in soul_keywords):
                    current_target = 'soul'
                else:
                    current_target = 'agents'
            if current_target == 'soul':
                soul_lines.append(line)
            else:
                agents_lines.append(line)

        soul = '\n'.join(soul_lines)
        agents = '\n'.join(agents_lines)

        return identity, soul, agents

    def convert_aider(self, agent: AgentDefinition) -> str:
        """转换为 Aider CONVENTIONS.md 格式"""
        return f"""
---

## {agent.name}

> {agent.description}

{agent.body}
"""

    def convert_antigravity(self, agent: AgentDefinition) -> str:
        """转换为 Antigravity SKILL.md 格式"""
        fm = f"""---
name: cyberteam-{agent.slug}
description: {agent.description}
risk: low
source: community
date_added: '{self.today}'
---
"""
        return fm + agent.body

    def convert_gemini_cli(self, agent: AgentDefinition) -> str:
        """转换为 Gemini CLI 格式"""
        fm = f"""---
name: cyberteam-{agent.slug}
description: {agent.description}
---
"""
        return fm + agent.body

    def convert_qwen(self, agent: AgentDefinition) -> str:
        """转换为 Qwen Code 格式"""
        fm = f"""---
name: {agent.slug}
description: {agent.description}
"""
        if agent.tools:
            fm += f"tools: {agent.tools}\n"
        fm += f"---\n{agent.body}"
        return fm

    def convert(self, agent: AgentDefinition, tool: str) -> any:
        """转换单个 Agent"""
        converters = {
            'claude-code': self.convert_claude_code,
            'copilot': self.convert_copilot,
            'cursor': self.convert_cursor,
            'windsurf': self.convert_windsurf,
            'opencode': self.convert_opencode,
            'openclaw': self.convert_openclaw,
            'aider': self.convert_aider,
            'antigravity': self.convert_antigravity,
            'gemini-cli': self.convert_gemini_cli,
            'qwen': self.convert_qwen,
        }

        converter = converters.get(tool)
        if not converter:
            raise ValueError(f"不支持的工具: {tool}")

        return converter(agent)

    def generate_manifest(self, tool: str) -> str:
        """生成工具特定清单"""
        if tool == 'gemini-cli':
            return json.dumps({
                "name": "cyberteam",
                "version": "2.1.0"
            }, indent=2)
        return ""

    # =========================================================================
    # 辅助方法
    # =========================================================================

    def _resolve_color(self, color: str) -> str:
        """解析颜色名为十六进制"""
        named_colors = {
            'cyan': '#00FFFF',
            'blue': '#3498DB',
            'green': '#2ECC71',
            'red': '#E74C3C',
            'purple': '#9B59B6',
            'orange': '#F39C12',
            'teal': '#008080',
            'indigo': '#6366F1',
            'pink': '#E84393',
            'gold': '#EAB308',
            'amber': '#F59E0B',
            'yellow': '#EAB308',
            'violet': '#8B5CF6',
            'rose': '#F43F5E',
            'lime': '#84CC16',
            'gray': '#6B7280',
            'fuchsia': '#D946EF',
        }
        color_lower = color.lower().strip()
        if color_lower in named_colors:
            return named_colors[color_lower]
        if re.match(r'^#[0-9a-fA-F]{6}$', color):
            return color.upper()
        return '#6B7280'

    def save_conversion(self, tool: str):
        """保存转换结果"""
        output_tool_dir = self.output_dir / tool
        output_tool_dir.mkdir(parents=True, exist_ok=True)

        for agent in self.agents:
            try:
                if tool == 'openclaw':
                    identity, soul, agents = self.convert(agent, tool)
                    agent_dir = output_tool_dir / agent.slug
                    agent_dir.mkdir(parents=True, exist_ok=True)
                    (agent_dir / 'IDENTITY.md').write_text(identity, encoding='utf-8')
                    (agent_dir / 'SOUL.md').write_text(soul, encoding='utf-8')
                    (agent_dir / 'AGENTS.md').write_text(agents, encoding='utf-8')
                elif tool == 'aider':
                    # 追加到文件
                    content = self.convert(agent, tool)
                    output_file = output_tool_dir / 'CONVENTIONS.md'
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(content)
                elif tool == 'windsurf':
                    # 追加到文件
                    content = self.convert(agent, tool)
                    output_file = output_tool_dir / '.windsurfrules'
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(content)
                elif tool == 'gemini-cli':
                    # 创建 manifest
                    manifest_file = output_tool_dir / 'gemini-extension.json'
                    manifest_file.write_text(self.generate_manifest(tool), encoding='utf-8')
                    # 保存 skill
                    skill_dir = output_tool_dir / 'skills' / f'cyberteam-{agent.slug}'
                    skill_dir.mkdir(parents=True, exist_ok=True)
                    (skill_dir / 'SKILL.md').write_text(self.convert(agent, tool), encoding='utf-8')
                else:
                    extension = '.mdc' if tool == 'cursor' else '.md'
                    output_file = output_tool_dir / f"{agent.slug}{extension}"
                    output_file.write_text(self.convert(agent, tool), encoding='utf-8')

            except Exception as e:
                print(f"错误: 转换 {agent.name} 失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='CyberTeam v2.1 -- Agent 定义转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换为 Claude Code 格式
  python3 agent-converter.py --tool claude-code --input agents/

  # 转换为 Cursor 格式
  python3 agent-converter.py --tool cursor --input agents/

  # 转换为所有支持的格式
  python3 agent-converter.py --all --input agents/

  # 验证 Agent 定义
  python3 agent-converter.py --validate --input agents/
        """
    )

    parser.add_argument('--input', '-i', required=True, help='Agent 定义目录')
    parser.add_argument('--output', '-o', default='integrations/', help='输出目录')
    parser.add_argument('--tool', '-t', choices=AgentConverter.SUPPORTED_TOOLS, help='目标工具')
    parser.add_argument('--all', '-a', action='store_true', help='转换为所有支持的格式')
    parser.add_argument('--validate', action='store_true', help='仅验证不转换')

    args = parser.parse_args()

    converter = AgentConverter(args.input, args.output)

    print(f"加载 Agent 定义从: {args.input}")
    agents = converter.load_agents()
    print(f"已加载 {len(agents)} 个 Agent\n")

    if args.validate:
        print("验证 Agent 定义...")
        results = converter.validate_all()
        print(f"\n总计: {results['total']} | 通过: {results['passed']} | 失败: {results['failed']}")
        for agent_result in results['agents']:
            if agent_result['errors']:
                print(f"\n{agent_result['name']}:")
                for error in agent_result['errors']:
                    print(f"  - {error}")
        return 0 if results['failed'] == 0 else 1

    if args.all:
        tools = AgentConverter.SUPPORTED_TOOLS
    elif args.tool:
        tools = [args.tool]
    else:
        parser.error("必须指定 --tool 或 --all")

    print(f"转换为: {', '.join(tools)}\n")

    for tool in tools:
        print(f"转换 {tool}...")
        if tool in ['aider', 'windsurf']:
            # 这些格式需要先清空文件
            output_file = Path(args.output) / tool / ('CONVENTIONS.md' if tool == 'aider' else '.windsurfrules')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(f"# CyberTeam v2.1 -- AI Agent 规范\n\n本文件为 {tool} 提供完整的 CyberTeam Agent 列表。\n", encoding='utf-8')

        converter.save_conversion(tool)
        print(f"  完成: {args.output}/{tool}/")

    print("\n转换完成!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
