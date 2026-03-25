"""CyberTeam Skill 加载器。

自动扫描并注册所有 Skill。
"""

import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional, Type

from cyberteam.skills.base import BaseSkill, SkillMetadata
from cyberteam.skills.registry import SkillRegistry, get_registry


class SkillLoader:
    """Skill 加载器

    扫描 skills/ 目录，自动注册所有 Skill。
    """

    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # 默认路径
            self.base_path = Path(__file__).parent
        else:
            self.base_path = base_path

    def scan_skills(self) -> List[str]:
        """扫描并注册 Skill"""
        registry = get_registry()
        registered = []

        # 扫描子目录中的 Skill
        skill_categories = [
            "writing",
            "content_review",
            "growth",
            "gstack",
            "baoyu",
            "pua",
            "thinking_frameworks",
            "channel",
            "data"
        ]

        for category in skill_categories:
            category_path = self.base_path / category
            if not category_path.exists():
                continue

            try:
                module = importlib.import_module(f"cyberteam.skills.{category}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseSkill)
                        and attr != BaseSkill
                    ):
                        instance = attr()
                        registry.register(
                            name=instance.metadata.name,
                            skill_class=attr,
                            metadata=instance.metadata,
                            category=category
                        )
                        registered.append(instance.metadata.name)

            except Exception as e:
                print(f"Warning: Failed to load skills in {category}: {e}")

        return registered

    def load_all(self) -> int:
        """加载所有 Skill，返回加载数量"""
        return len(self.scan_skills())

    @staticmethod
    def list_skills(category: Optional[str] = None) -> List[str]:
        """列出已注册的 Skill"""
        return get_registry().list_skills(category)

    @staticmethod
    def get_skill(name: str) -> Optional[BaseSkill]:
        """获取 Skill 实例"""
        registry = get_registry()
        skill_class = registry.get_skill_class(name)
        if skill_class:
            return skill_class()
        return None

    @staticmethod
    def invoke_skill(name: str, input_data: Any = None, context: Optional[dict] = None) -> Optional[Any]:
        """调用 Skill"""
        skill = SkillLoader.get_skill(name)
        if skill:
            skill.initialize()
            return skill.execute(input_data, context)
        return None


# 全局加载器实例
_default_loader: Optional[SkillLoader] = None


def get_loader() -> SkillLoader:
    """获取全局加载器"""
    global _default_loader
    if _default_loader is None:
        _default_loader = SkillLoader()
    return _default_loader


def list_skills(category: Optional[str] = None) -> List[str]:
    """列出所有已注册的 Skill"""
    return SkillLoader.list_skills(category)


def get_skill(name: str) -> Optional[BaseSkill]:
    """获取 Skill 实例"""
    return SkillLoader.get_skill(name)


def invoke_skill(name: str, input_data: Any = None, context: Optional[dict] = None) -> Optional[Any]:
    """调用 Skill"""
    return SkillLoader.invoke_skill(name, input_data, context)
