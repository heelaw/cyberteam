"""CyberTeam Skills 模块。

整合所有 Skill，包括写作、内容审核、增长等各种专业技能。
"""

from cyberteam.skills.base import (
    BaseSkill,
    WritingSkill,
    ContentReviewSkill,
    SkillMetadata
)
from cyberteam.skills.registry import SkillRegistry, get_registry
from cyberteam.skills.loader import (
    SkillLoader,
    get_loader,
    list_skills,
    get_skill,
    invoke_skill
)

__all__ = [
    # 基类
    "BaseSkill",
    "WritingSkill",
    "ContentReviewSkill",
    "SkillMetadata",
    # 注册表和加载器
    "SkillRegistry",
    "get_registry",
    "SkillLoader",
    "get_loader",
    "list_skills",
    "get_skill",
    "invoke_skill",
]

# 版本信息
__version__ = "4.0.0"
