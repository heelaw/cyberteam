"""CyberTeam Skill 注册表。

管理所有 Skill 的注册和发现。
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass

from cyberteam.skills.base import BaseSkill, SkillMetadata


@dataclass
class SkillRegistration:
    """Skill 注册信息"""
    name: str
    skill_class: Type[BaseSkill]
    metadata: SkillMetadata
    category: str  # "writing", "content_review", "growth", "tools"


class SkillRegistry:
    """Skill 注册表

    单例模式，全局管理所有 Skill。
    """

    _instance: Optional['SkillRegistry'] = None
    _skills: Dict[str, SkillRegistration] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'SkillRegistry':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(
        self,
        name: str,
        skill_class: Type[BaseSkill],
        metadata: SkillMetadata,
        category: str = "general"
    ) -> None:
        """注册 Skill"""
        registration = SkillRegistration(
            name=name,
            skill_class=skill_class,
            metadata=metadata,
            category=category
        )
        self._skills[name] = registration

    def unregister(self, name: str) -> bool:
        """取消注册 Skill"""
        if name in self._skills:
            del self._skills[name]
            return True
        return False

    def get(self, name: str) -> Optional[SkillRegistration]:
        """获取 Skill 注册信息"""
        return self._skills.get(name)

    def get_skill_class(self, name: str) -> Optional[Type[BaseSkill]]:
        """获取 Skill 类"""
        reg = self._skills.get(name)
        return reg.skill_class if reg else None

    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """列出所有 Skill 或指定类别的 Skill"""
        if category is None:
            return list(self._skills.keys())
        return [
            name for name, reg in self._skills.items()
            if reg.category == category
        ]

    def list_by_tag(self, tag: str) -> List[str]:
        """列出包含指定标签的所有 Skill"""
        return [
            name for name, reg in self._skills.items()
            if tag in reg.metadata.tags
        ]

    def list_by_trigger(self, trigger: str) -> List[str]:
        """列出包含指定触发条件的所有 Skill"""
        return [
            name for name, reg in self._skills.items()
            if trigger in reg.metadata.triggers
        ]

    def get_by_category(self, category: str) -> List[SkillRegistration]:
        """获取指定类别的所有 Skill"""
        return [
            reg for reg in self._skills.values()
            if reg.category == category
        ]

    def exists(self, name: str) -> bool:
        """检查 Skill 是否已注册"""
        return name in self._skills

    def clear(self) -> None:
        """清空注册表（主要用于测试）"""
        self._skills.clear()

    def get_all_metadata(self) -> List[SkillMetadata]:
        """获取所有 Skill 的元数据"""
        return [reg.metadata for reg in self._skills.values()]


# 全局注册表实例
_global_registry = SkillRegistry.get_instance


def get_registry() -> SkillRegistry:
    """获取全局注册表"""
    return _global_registry()
