"""Agent compiler for CyberTeam - compiles agent definitions from YAML + DB + Markdown."""
from __future__ import annotations

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any, Union
from jinja2 import Template


@dataclass
class AgentProfile:
    """Compiled agent profile."""
    name: str
    llm: str = "claude"
    tools: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    system_prompt: str = ""
    departments: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    description: str = ""
    raw_config: Optional[dict] = None
    is_custom: bool = False  # True = from DB, False = from YAML


class AgentCompiler:
    """Compiles agent definitions from directory structure + database.

    Expected YAML structure:
        agent_dir/
        ├── agent.yaml        # Agent metadata
        ├── SOUL.md          # System prompt
        ├── prompts/
        │   ├── think.prompt
        │   ├── act.prompt
        │   └── reflect.prompt
        └── skills/
            ├── skill1.yaml
            └── skill2.yaml
    """

    def __init__(self, agents_dir: str = ""):
        if not agents_dir:
            base = Path(__file__).resolve().parents[3]
            candidates = [base / "AGENTS", base / "Output" / "cyberteam-v4" / "agents"]
            for c in candidates:
                if c.exists():
                    agents_dir = str(c)
                    break
            else:
                agents_dir = str(candidates[0])
        self.agents_dir = Path(agents_dir)
        self._compiled_agents: dict[str, AgentProfile] = {}
        self._templates: dict[str, Template] = {}

    def compile(self, agent_dir: Union[str, Path]) -> AgentProfile:
        """Compile an agent from its YAML directory."""
        agent_dir = Path(agent_dir)
        agent_name = agent_dir.name

        config_file = agent_dir / "agent.yaml"
        if not config_file.exists():
            config_file = agent_dir / "AGENT.md"
            if config_file.exists():
                return self._compile_from_md(config_file, agent_name)

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        soul_file = agent_dir / "SOUL.md"
        soul_content = ""
        if soul_file.exists():
            with open(soul_file, "r", encoding="utf-8") as f:
                soul_content = f.read()

        prompts_dir = agent_dir / "prompts"
        prompt_templates = {}
        if prompts_dir.exists():
            for prompt_file in prompts_dir.glob("*.prompt"):
                with open(prompt_file, "r", encoding="utf-8") as f:
                    prompt_templates[prompt_file.stem] = f.read()

        system_prompt = self._compose(soul_content, config, prompt_templates)

        raw_skills = config.get("skills", [])
        flat_skills: list[str] = []
        if isinstance(raw_skills, list):
            flat_skills = raw_skills
        elif isinstance(raw_skills, dict):
            for _cat, vals in raw_skills.items():
                if isinstance(vals, list):
                    flat_skills.extend(vals)
                elif isinstance(vals, str):
                    flat_skills.append(vals)

        profile = AgentProfile(
            name=agent_name,
            llm=config.get("llm", "claude"),
            tools=config.get("tools", []),
            skills=flat_skills,
            system_prompt=system_prompt,
            departments=config.get("departments", []),
            version=config.get("version", "1.0.0"),
            description=config.get("description", ""),
            raw_config=config,
            is_custom=False,
        )

        self._compiled_agents[agent_name] = profile
        return profile

    def _compile_from_md(self, md_file: Path, agent_name: str) -> AgentProfile:
        """Compile agent from markdown file."""
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        return AgentProfile(
            name=agent_name,
            system_prompt=content,
            description=content[:200],
            is_custom=False,
        )

    def _compose(
        self,
        soul: str,
        config: dict,
        prompts: dict[str, str],
    ) -> str:
        """Compose system prompt using Jinja2 templates."""
        template_str = soul or "You are {{ agent_name }}."

        try:
            template = Template(template_str)
            composed = template.render(
                agent_name=config.get("name", "Agent"),
                version=config.get("version", "1.0.0"),
                departments=config.get("departments", []),
            )
        except Exception:
            composed = template_str

        if prompts:
            prompt_section = "\n\n## Prompt Templates\n"
            for name, content in prompts.items():
                prompt_section += f"\n### {name}\n{content}\n"
            composed += prompt_section

        return composed

    def get_available_agents(self) -> list[AgentProfile]:
        """Scan agents directory and compile all agents.

        Returns:
            List of compiled AgentProfiles (YAML only, DB agents via separate method)
        """
        if not self.agents_dir.exists():
            return []

        agents = []
        for item in self.agents_dir.iterdir():
            if item.is_dir():
                try:
                    profile = self.compile(item)
                    agents.append(profile)
                except Exception as e:
                    print(f"Error compiling agent {item.name}: {e}")

        return agents

    def get_agent(self, name: str) -> Optional[AgentProfile]:
        """Get a compiled agent by name from cache or YAML directory."""
        if name in self._compiled_agents:
            return self._compiled_agents[name]

        agent_dir = self.agents_dir / name
        if agent_dir.exists():
            return self.compile(agent_dir)

        return None

    def list_agents(self) -> list[str]:
        """List all available agent names (YAML only)."""
        agents = self.get_available_agents()
        return [a.name for a in agents]

    # ============ Custom Agent (DB) Integration ============

    def add_custom_agent(self, db_agent: Any) -> AgentProfile:
        """Add a custom agent from DB to the compiler cache.

        Args:
            db_agent: SQLAlchemy CustomAgent model instance

        Returns:
            AgentProfile wrapping the custom agent
        """
        profile = AgentProfile(
            name=db_agent.name,
            llm=db_agent.llm or "claude",
            tools=db_agent.tools or [],
            skills=db_agent.skills or [],
            system_prompt=db_agent.system_prompt or "",
            departments=db_agent.departments or [],
            version=db_agent.version or "1.0.0",
            description=db_agent.description or "",
            is_custom=True,
        )
        self._compiled_agents[db_agent.name] = profile
        return profile

    def get_all_agents(self) -> list[AgentProfile]:
        """Get all agents (YAML built-in + cached custom).

        Note: Custom agents must be added via add_custom_agent() first.
        For HTTP requests, use get_agents_with_db() instead.
        """
        return list(self._compiled_agents.values())


# Global instance
agent_compiler = AgentCompiler()


async def sync_custom_agents_to_compiler(db_session: Any) -> int:
    """Load all active custom agents from DB into compiler cache.

    Called at startup to ensure chat endpoint can find custom agents.

    Returns:
        Number of custom agents synced
    """
    """Load all active custom agents from DB into compiler cache.

    Called at startup to ensure chat endpoint can find custom agents.

    Returns:
        Number of custom agents synced
    """
    from sqlalchemy import select
    from app.db.models import CustomAgent

    stmt = select(CustomAgent).where(CustomAgent.is_active == True)
    result = await db_session.execute(stmt)
    db_agents = result.scalars().all()

    count = 0
    for db_agent in db_agents:
        agent_compiler.add_custom_agent(db_agent)
        count += 1

    return count
