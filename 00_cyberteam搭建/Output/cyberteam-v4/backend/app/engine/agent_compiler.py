"""Agent 编译器 - 抄 Magic AgentLang 核心。

核心功能：
把 SOUL.md + agent.yaml 编译成运行时 AgentProfile

编译器输入：
1. agent.yaml - 声明式配置（名称、LLM、工具、所属部门）
2. SOUL.md - 角色定义（Markdown 格式的角色描述）
3. prompts/ - 模块化 Prompt（.prompt 文件）
4. SKILL.md - 技能定义

编译器输出：
- AgentProfile - 可直接用于运行的 Agent 配置

设计理念：
- 声明式配置 + 编译时组合 = 灵活的 Agent 定义
- 支持 Prompt 模块化和复用
- 支持技能继承和组合
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import yaml
import logging

log = logging.getLogger("cyberteam.agent_compiler")


@dataclass
class AgentProfile:
    """编译后的 Agent 配置文件。"""

    name: str
    code: str  # Agent 代码（唯一标识）
    llm: str = "main_llm"
    tools: List[str] = field(default_factory=list)
    skills: List[Dict[str, Any]] = field(default_factory=list)
    system_prompt: str = ""
    departments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "code": self.code,
            "llm": self.llm,
            "tools": self.tools,
            "skills": self.skills,
            "system_prompt": self.system_prompt,
            "departments": self.departments,
            "metadata": self.metadata,
            "version": self.version,
        }


@dataclass
class SkillDefinition:
    """技能定义。"""

    name: str
    code: str
    trigger: str  # 触发条件
    workflow: str  # 工作流程
    prompts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCompiler:
    """Agent 编译器。

    用法:
        compiler = AgentCompiler()
        profile = await compiler.compile(agent_dir=Path("/path/to/agent"))
    """

    # 支持的 Prompt 文件扩展名
    PROMPT_EXTENSIONS = [".prompt", ".md", ".txt"]

    def __init__(self):
        self._cache: Dict[str, AgentProfile] = {}

    async def compile(self, agent_dir: Path, use_cache: bool = True) -> AgentProfile:
        """编译 Agent 目录到 AgentProfile。

        Args:
            agent_dir: Agent 目录路径
            use_cache: 是否使用缓存

        Returns:
            AgentProfile 对象
        """
        agent_dir = Path(agent_dir)

        if not agent_dir.exists():
            raise FileNotFoundError(f"Agent directory not found: {agent_dir}")

        # 检查缓存
        cache_key = str(agent_dir.absolute())
        if use_cache and cache_key in self._cache:
            log.debug(f"Using cached profile for {agent_dir.name}")
            return self._cache[cache_key]

        # 1. 读取 agent.yaml（声明式配置）
        config = self._load_config(agent_dir)

        # 2. 读取 SOUL.md（角色定义）
        soul = self._load_soul(agent_dir)

        # 3. 读取 prompts/（模块化 Prompt）
        prompts = self._load_prompts(agent_dir)

        # 4. 读取 skills/（技能定义）
        skills = self._load_skills(agent_dir)

        # 5. 读取 SKILL.md（主技能文件）
        main_skill = self._load_main_skill(agent_dir)

        # 6. 编译成 AgentProfile
        system_prompt = self._compose_system_prompt(soul, prompts, config)

        profile = AgentProfile(
            name=config.get("name", agent_dir.name),
            code=config.get("code", agent_dir.name.lower().replace("-", "_")),
            llm=config.get("llm", "main_llm"),
            tools=config.get("tools", []),
            skills=skills + ([main_skill] if main_skill else []),
            system_prompt=system_prompt,
            departments=config.get("departments", []),
            metadata={
                "config": config,
                "soul_path": str(agent_dir / "SOUL.md"),
                "prompts_count": len(prompts),
                "skills_count": len(skills),
            },
            version=config.get("version", "1.0.0"),
        )

        # 缓存
        self._cache[cache_key] = profile

        log.info(f"Compiled agent: {profile.name} (code={profile.code}, tools={len(profile.tools)}, skills={len(profile.skills)})")

        return profile

    def _load_config(self, agent_dir: Path) -> dict:
        """读取 agent.yaml 配置文件。"""
        config_file = agent_dir / "agent.yaml"

        if config_file.exists():
            try:
                return yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as e:
                log.warning(f"Failed to parse {config_file}: {e}")

        return {}

    def _load_soul(self, agent_dir: Path) -> str:
        """读取 SOUL.md 角色定义。"""
        soul_file = agent_dir / "SOUL.md"

        if soul_file.exists():
            return soul_file.read_text(encoding="utf-8")

        log.debug(f"SOUL.md not found in {agent_dir}")
        return ""

    def _load_prompts(self, agent_dir: Path) -> Dict[str, str]:
        """读取 prompts/ 目录下的所有 Prompt 文件。"""
        prompts = {}
        prompts_dir = agent_dir / "prompts"

        if not prompts_dir.exists():
            return prompts

        for ext in self.PROMPT_EXTENSIONS:
            for prompt_file in prompts_dir.glob(f"*{ext}"):
                key = prompt_file.stem  # 文件名（不含扩展名）
                prompts[key] = prompt_file.read_text(encoding="utf-8")

        log.debug(f"Loaded {len(prompts)} prompts from {prompts_dir}")
        return prompts

    def _load_skills(self, agent_dir: Path) -> List[Dict[str, Any]]:
        """读取 skills/ 目录下的技能定义。"""
        skills = []
        skills_dir = agent_dir / "skills"

        if not skills_dir.exists():
            return skills

        for skill_file in skills_dir.glob("*.md"):
            skill = self._parse_skill_file(skill_file)
            if skill:
                skills.append(skill)

        log.debug(f"Loaded {len(skills)} skills from {skills_dir}")
        return skills

    def _load_main_skill(self, agent_dir: Path) -> Optional[Dict[str, Any]]:
        """读取根目录的 SKILL.md 主技能文件。"""
        skill_file = agent_dir / "SKILL.md"

        if skill_file.exists():
            return self._parse_skill_file(skill_file)

        return None

    def _parse_skill_file(self, skill_file: Path) -> Optional[Dict[str, Any]]:
        """解析技能文件。"""
        try:
            content = skill_file.read_text(encoding="utf-8")
            return {
                "name": skill_file.stem,
                "code": skill_file.stem.lower().replace(" ", "_"),
                "content": content,
                "file": str(skill_file),
            }
        except Exception as e:
            log.warning(f"Failed to parse skill file {skill_file}: {e}")
            return None

    def _compose_system_prompt(
        self, soul: str, prompts: Dict[str, str], config: dict
    ) -> str:
        """组合 system prompt。

        顺序：
        1. SOUL.md 的角色定义
        2. prompts/ 中的模块化 Prompt
        3. agent.yaml 中的额外配置
        """
        parts = []

        # 1. SOUL.md
        if soul:
            parts.append(soul)

        # 2. prompts/ 模块
        if prompts:
            prompt_parts = ["\n\n## Module Prompts\n"]
            for key, content in prompts.items():
                prompt_parts.append(f"\n### {key}\n\n{content}")
            parts.append("".join(prompt_parts))

        # 3. 额外配置
        extra_config = config.get("extra_prompt", "")
        if extra_config:
            parts.append(f"\n\n## Additional Configuration\n\n{extra_config}")

        return "\n\n".join(parts)

    def compile_from_dict(self, config: dict) -> AgentProfile:
        """从字典配置直接编译（不读取文件）。

        用于运行时动态创建 Agent。
        """
        return AgentProfile(
            name=config.get("name", "unnamed"),
            code=config.get("code", "unnamed"),
            llm=config.get("llm", "main_llm"),
            tools=config.get("tools", []),
            skills=config.get("skills", []),
            system_prompt=config.get("system_prompt", ""),
            departments=config.get("departments", []),
            metadata=config.get("metadata", {}),
            version=config.get("version", "1.0.0"),
        )

    def clear_cache(self) -> None:
        """清空编译缓存。"""
        self._cache.clear()
        log.info("Agent compiler cache cleared")


# 全局编译器实例
_agent_compiler: Optional[AgentCompiler] = None


def get_agent_compiler() -> AgentCompiler:
    """获取 Agent 编译器单例。"""
    global _agent_compiler
    if _agent_compiler is None:
        _agent_compiler = AgentCompiler()
    return _agent_compiler
