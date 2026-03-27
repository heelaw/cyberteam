#!/usr/bin/env python3
"""
CyberTeam v2.1 -- 配置生成器

功能:
- 从模板生成配置文件
- 支持多工具配置
- 环境变量处理
- 配置验证

使用方法:
    python3 config-generator.py --template claude-code --output ~/.claude/settings.json
    python3 config-generator.py --all --output ./config/
    python3 config-generator.py --validate ./config/settings.json
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


@dataclass
class ConfigTemplate:
    """配置模板"""
    name: str
    tool: str
    description: str
    fields: dict[str, Any] = field(default_factory=dict)
    required_fields: list[str] = field(default_factory=list)
    validators: dict[str, str] = field(default_factory=dict)  # field -> validator name


class ConfigGenerator:
    """配置生成器"""

    TEMPLATES = {
        'claude-code': ConfigTemplate(
            name='Claude Code',
            tool='claude',
            description='Claude Code 配置文件',
            fields={
                'model': 'claude-opus-4',
                'max_tokens': 4096,
                'temperature': 0.7,
                'tools': ['read', 'edit', 'bash', 'glob', 'grep', 'web-search'],
                'themes': {
                    'light': 'light',
                    'dark': 'dark',
                },
            },
            required_fields=['model'],
        ),
        'cursor': ConfigTemplate(
            name='Cursor',
            tool='cursor',
            description='Cursor AI 配置',
            fields={
                'model': 'gpt-4',
                'max_tokens': 4096,
                'temperature': 0.7,
                'rules': [],
                'preambles': [],
            },
            required_fields=['model'],
        ),
        'windsurf': ConfigTemplate(
            name='Windsurf',
            tool='windsurf',
            description='Windsurf AI 配置',
            fields={
                'model': 'claude-sonnet',
                'max_tokens': 4096,
                'temperature': 0.7,
                'rules_file': '.windsurfrules',
            },
            required_fields=['model'],
        ),
        'copilot': ConfigTemplate(
            name='GitHub Copilot',
            tool='copilot',
            description='GitHub Copilot 配置',
            fields={
                'language': 'auto',
                'suggestion_mode': 'inline',
                'extensions': [],
            },
            required_fields=[],
        ),
        'gemini-cli': ConfigTemplate(
            name='Gemini CLI',
            tool='gemini',
            description='Gemini CLI 配置',
            fields={
                'model': 'gemini-pro',
                'api_key_env': 'GEMINI_API_KEY',
                'temperature': 0.7,
                'max_tokens': 8192,
            },
            required_fields=['model'],
        ),
        'aider': ConfigTemplate(
            name='Aider',
            tool='aider',
            description='Aider 配置',
            fields={
                'model': 'claude-3-5-sonnet',
                'edit_format': 'diff',
                'auto_commit': True,
                'commit_message': 'auto',
            },
            required_fields=['model'],
        ),
        'opencode': ConfigTemplate(
            name='OpenCode',
            tool='opencode',
            description='OpenCode 配置',
            fields={
                'model': 'claude-3-5-sonnet',
                'agents_dir': '.opencode/agents',
                'conventions_file': '.opencode/conventions.md',
            },
            required_fields=['model'],
        ),
        'qwen': ConfigTemplate(
            name='Qwen Code',
            tool='qwen',
            description='Qwen Code 配置',
            fields={
                'model': 'qwen-max',
                'agents_dir': '.qwen/agents',
            },
            required_fields=['model'],
        ),
    }

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = Path(template_dir) if template_dir else Path(__file__).parent.parent / 'templates'
        self.generated_configs: dict[str, dict] = {}

    def load_template(self, name: str) -> Optional[ConfigTemplate]:
        """加载模板"""
        if name in self.TEMPLATES:
            return self.TEMPLATES[name]

        # 尝试从文件加载
        template_file = self.template_dir / f"{name}.json"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ConfigTemplate(**data)

        return None

    def apply_env_vars(self, config: dict) -> dict:
        """替换环境变量占位符"""
        result = {}
        for key, value in config.items():
            if isinstance(value, str):
                # 替换 ${VAR_NAME} 或 $VAR_NAME
                import re
                value = re.sub(r'\$\{(\w+)\}', lambda m: os.getenv(m.group(1), m.group(0)), value)
                value = re.sub(r'\$(\w+)', lambda m: os.getenv(m.group(1), m.group(0)), value)
            elif isinstance(value, dict):
                value = self.apply_env_vars(value)
            elif isinstance(value, list):
                value = [
                    self.apply_env_vars(v) if isinstance(v, dict) else v
                    for v in value
                ]
            result[key] = value
        return result

    def generate(self, template_name: str, overrides: Optional[dict] = None) -> dict:
        """生成配置"""
        template = self.load_template(template_name)
        if not template:
            raise ValueError(f"未知模板: {template_name}")

        config = template.fields.copy()

        # 应用覆盖
        if overrides:
            config.update(overrides)

        # 应用环境变量
        config = self.apply_env_vars(config)

        # 添加元数据
        config['_meta'] = {
            'template': template_name,
            'generated_at': datetime.now().isoformat(),
            'tool': template.tool,
        }

        self.generated_configs[template_name] = config
        return config

    def generate_all(self, overrides: Optional[dict] = None) -> dict[str, dict]:
        """生成所有配置"""
        results = {}
        for name in self.TEMPLATES:
            try:
                results[name] = self.generate(name, overrides)
            except Exception as e:
                print(f"警告: 生成 {name} 配置失败: {e}")
        return results

    def validate(self, config: dict, template_name: str) -> tuple[bool, list[str]]:
        """验证配置"""
        template = self.load_template(template_name)
        if not template:
            return False, [f"未知模板: {template_name}"]

        errors = []

        # 检查必需字段
        for field in template.required_fields:
            if field not in config or config[field] is None:
                errors.append(f"缺少必需字段: {field}")

        # 自定义验证器
        validators = {
            'model': self._validate_model,
            'max_tokens': self._validate_max_tokens,
            'temperature': self._validate_temperature,
        }

        for field_name, validator_name in template.validators.items():
            validator = validators.get(validator_name)
            if validator and field_name in config:
                is_valid, error = validator(config[field_name])
                if not is_valid:
                    errors.append(f"{field_name}: {error}")

        return len(errors) == 0, errors

    def _validate_model(self, value: str) -> tuple[bool, str]:
        """验证模型名称"""
        if not value or len(value) < 3:
            return False, "模型名称太短"
        return True, ""

    def _validate_max_tokens(self, value: int) -> tuple[bool, str]:
        """验证最大 token 数"""
        if not isinstance(value, int):
            return False, "必须是整数"
        if value < 100 or value > 100000:
            return False, "范围应在 100-100000 之间"
        return True, ""

    def _validate_temperature(self, value: float) -> tuple[bool, str]:
        """验证温度参数"""
        if not isinstance(value, (int, float)):
            return False, "必须是数字"
        if value < 0 or value > 2:
            return False, "范围应在 0-2 之间"
        return True, ""

    def save_config(self, config: dict, output_path: str) -> bool:
        """保存配置到文件"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def create_agent_config(self, agent_name: str, agent_def: dict) -> dict:
        """为特定 Agent 创建配置"""
        return {
            'agent_name': agent_name,
            'description': agent_def.get('description', ''),
            'capabilities': agent_def.get('capabilities', []),
            'tools': agent_def.get('tools', []),
            'rules': agent_def.get('rules', []),
            'preambles': agent_def.get('preambles', []),
            'generated_at': datetime.now().isoformat(),
        }

    def create_project_config(self, project_name: str, tools: list[str]) -> dict:
        """创建项目级配置"""
        configs = {}
        for tool in tools:
            if tool in self.TEMPLATES:
                configs[tool] = self.generate(tool)

        return {
            'project_name': project_name,
            'tools': list(tools),
            'configs': configs,
            'generated_at': datetime.now().isoformat(),
        }


def main():
    parser = argparse.ArgumentParser(
        description='CyberTeam v2.1 -- 配置生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成单个工具配置
  python3 config-generator.py --template claude-code --output ~/.claude/settings.json

  # 生成所有工具配置
  python3 config-generator.py --all --output ./config/

  # 使用覆盖值
  python3 config-generator.py --template claude-code --overrides '{"model": "claude-3-5-sonnet"}'

  # 验证配置
  python3 config-generator.py --validate ./config/settings.json

  # 创建项目配置
  python3 config-generator.py --project "MyProject" --tools claude-code cursor --output ./project.json
        """
    )

    parser.add_argument('--template', '-t', help='模板名称')
    parser.add_argument('--output', '-o', help='输出路径')
    parser.add_argument('--all', '-a', action='store_true', help='生成所有配置')
    parser.add_argument('--overrides', help='JSON 格式的覆盖值')
    parser.add_argument('--validate', help='验证配置文件')
    parser.add_argument('--project', help='创建项目配置')
    parser.add_argument('--tools', nargs='+', help='项目使用的工具列表')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有模板')

    args = parser.parse_args()

    generator = ConfigGenerator()

    if args.list:
        print("CyberTeam v2.1 -- 可用配置模板\n")
        for name, template in generator.TEMPLATES.items():
            print(f"  {name}: {template.description}")
        print()

    elif args.validate:
        with open(args.validate, 'r', encoding='utf-8') as f:
            config = json.load(f)
        template_name = config.get('_meta', {}).get('template', '')
        is_valid, errors = generator.validate(config, template_name)
        if is_valid:
            print(f"配置有效: {args.validate}")
        else:
            print(f"配置无效:")
            for error in errors:
                print(f"  - {error}")
            return 1

    elif args.template:
        overrides = json.loads(args.overrides) if args.overrides else None
        config = generator.generate(args.template, overrides)

        if args.output:
            generator.save_config(config, args.output)
            print(f"配置已保存: {args.output}")
        else:
            print(json.dumps(config, indent=2, ensure_ascii=False))

    elif args.all:
        if not args.output:
            print("错误: --all 需要指定 --output 目录")
            return 1

        configs = generator.generate_all()
        for name, config in configs.items():
            output_path = Path(args.output) / f"{name}.json"
            generator.save_config(config, str(output_path))
            print(f"已生成: {output_path}")

    elif args.project:
        if not args.tools:
            print("错误: --project 需要指定 --tools")
            return 1
        config = generator.create_project_config(args.project, args.tools)
        if args.output:
            generator.save_config(config, args.output)
            print(f"项目配置已保存: {args.output}")
        else:
            print(json.dumps(config, indent=2, ensure_ascii=False))

    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    sys.exit(main())
