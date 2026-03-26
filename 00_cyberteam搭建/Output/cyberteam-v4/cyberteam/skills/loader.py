"""SkillLoader - 增强版Skill加载器.

支持两种格式：
1. Python Skill类 (BaseSkill子类)
2. SKILL.md格式 (v3运营Skill)

SKILL.md格式会被解析并包装成Python Skill类执行。
"""

import os
import re
import yaml
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    name: str
    description: str
    trigger: str
    difficulty: str = "medium"
    estimated_time: str = "15-30分钟"
    version: str = "v1.0"
    author: str = "Cyberwiz"
    tags: List[str] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)


class BaseSkill:
    """Skill 基类"""
    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata

    def initialize(self):
        """初始化 Skill"""
        pass

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行 Skill"""
        raise NotImplementedError


class SKILLSkill(BaseSkill):
    """SKILL.md格式包装器 - 将SKILL.md解析为可执行的Python Skill"""

    def __init__(self, metadata: SkillMetadata, skill_path: str):
        super().__init__(metadata)
        self.skill_path = skill_path
        self._load_content()

    def _load_content(self):
        """加载SKILL.md内容"""
        skill_md_path = Path(self.skill_path) / "SKILL.md"
        if skill_md_path.exists():
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 解析YAML frontmatter
                match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if match:
                    yaml_content = match.group(1)
                    self._yaml_data = yaml.safe_load(yaml_content)
                    self._markdown_content = content[match.end():]
                else:
                    self._yaml_data = {}
                    self._markdown_content = content
        else:
            self._yaml_data = {}
            self._markdown_content = ""

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行SKILL.md定义的Skill"""
        return {
            "skill_name": self.metadata.name,
            "description": self.metadata.description,
            "trigger": self.metadata.trigger,
            "content_preview": self._markdown_content[:500] if self._markdown_content else "",
            "yaml_data": self._yaml_data,
            "skill_path": self.skill_path,
            "message": f"Skill '{self.metadata.name}' 已从 {self.skill_path} 加载"
        }


class SkillLoader:
    """Skill加载器 - 支持Python Skill类和SKILL.md格式"""

    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            # 默认路径：项目根目录
            self.base_path = Path(__file__).parent.parent.parent
        else:
            self.base_path = Path(base_path)

        self._skills: Dict[str, BaseSkill] = {}
        self._skill_paths: Dict[str, str] = {}

    def scan_skills(self, skills_dir: str = "skills") -> Dict[str, BaseSkill]:
        """扫描并加载Skills"""
        skills_path = self.base_path / skills_dir

        if not skills_path.exists():
            print(f"⚠️ Skills目录不存在: {skills_path}")
            return {}

        # 1. 扫描Python Skill类
        self._scan_python_skills(skills_path / "growth")

        # 2. 扫描SKILL.md格式
        self._scan_skill_md_formats(skills_path)

        return self._skills

    def _scan_python_skills(self, skill_dir: Path):
        """扫描Python Skill类"""
        if not skill_dir.exists():
            return

        # 导入growth模块的Skills
        try:
            # 尝试导入growth模块
            module_name = "CYBERTEAM.skills.growth"
            if str(skill_dir).endswith("growth"):
                # 动态导入
                import sys
                skill_path_str = str(skill_dir.parent.parent)
                if skill_path_str not in sys.path:
                    sys.path.insert(0, skill_path_str)

                from skills.growth import (
                    ReportingFrameworkSkill,
                    TimeManagementSkill,
                    ProgressTrackingSkill,
                    RetrospectiveSkill,
                    UserGrowthSkill,
                    ContentOperationsSkill,
                    ActivityOperationsSkill,
                    GrowthMarketingSkill,
                    BrandMarketingSkill,
                    PerformanceMarketingSkill,
                    TeamManagementSkill,
                    StrategyPlanningSkill,
                )

                skill_classes = [
                    ReportingFrameworkSkill,
                    TimeManagementSkill,
                    ProgressTrackingSkill,
                    RetrospectiveSkill,
                    UserGrowthSkill,
                    ContentOperationsSkill,
                    ActivityOperationsSkill,
                    GrowthMarketingSkill,
                    BrandMarketingSkill,
                    PerformanceMarketingSkill,
                    TeamManagementSkill,
                    StrategyPlanningSkill,
                ]

                for skill_class in skill_classes:
                    instance = skill_class()
                    self._skills[instance.metadata.name] = instance
                    print(f"✅ Python Skill加载: {instance.metadata.name}")

        except Exception as e:
            print(f"⚠️ 导入Python Skill失败: {e}")

    def _scan_skill_md_formats(self, skills_base: Path):
        """扫描SKILL.md格式的Skills - 从v3运营Agent融合"""
        # 扫描"需要融合的对象/运营AGENT"下的SKILL.md
        fusion_source = self.base_path.parent / "需要融合的对象" / "运营AGENT"

        if not fusion_source.exists():
            print(f"⚠️ 融合源目录不存在: {fusion_source}")
            return

        # 遍历所有运营Agent
        for agent_dir in fusion_source.iterdir():
            if not agent_dir.is_dir():
                continue

            skill配套_dir = agent_dir / "配套skill"
            if not skill配套_dir.exists():
                continue

            # 遍历配套skill
            for skill_dir in skill配套_dir.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                try:
                    # 解析SKILL.md
                    metadata = self._parse_skill_md(skill_md)
                    if metadata:
                        # 创建SKILL包装器
                        skill_instance = SKILLSkill(metadata, str(skill_dir))
                        self._skills[metadata.name] = skill_instance
                        self._skill_paths[metadata.name] = str(skill_dir)
                        print(f"✅ SKILL.md加载: {metadata.name} (from {agent_dir.name})")

                except Exception as e:
                    print(f"⚠️ 加载SKILL失败 {skill_dir.name}: {e}")

    def _parse_skill_md(self, skill_md_path: Path) -> Optional[SkillMetadata]:
        """解析SKILL.md的frontmatter"""
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取YAML frontmatter
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return None

            yaml_content = match.group(1)
            data = yaml.safe_load(yaml_content)

            if not data:
                return None

            return SkillMetadata(
                name=data.get('name', skill_md_path.parent.name),
                description=data.get('description', ''),
                trigger=data.get('trigger', ''),
                difficulty=data.get('difficulty', 'medium'),
                estimated_time=data.get('estimated_time', '15-30分钟'),
                version=data.get('version', 'v1.0'),
                author=data.get('author', 'Cyberwiz'),
                tags=data.get('tags', []),
                success_metrics=data.get('success_metrics', {})
            )

        except Exception as e:
            print(f"⚠️ 解析SKILL.md失败 {skill_md_path}: {e}")
            return None

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """获取指定Skill"""
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """列出所有已加载的Skills"""
        return list(self._skills.keys())

    def get_skill_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取Skill信息"""
        skill = self._skills.get(name)
        if not skill:
            return None

        return {
            "name": skill.metadata.name,
            "description": skill.metadata.description,
            "trigger": skill.metadata.trigger,
            "difficulty": skill.metadata.difficulty,
            "tags": skill.metadata.tags,
            "path": self._skill_paths.get(name, "Python类")
        }


# 全局SkillLoader实例
_global_loader: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """获取全局SkillLoader实例"""
    global _global_loader
    if _global_loader is None:
        _global_loader = SkillLoader()
    return _global_loader


def load_all_skills() -> Dict[str, BaseSkill]:
    """加载所有Skills"""
    loader = get_skill_loader()
    return loader.scan_skills()


if __name__ == "__main__":
    # 测试SkillLoader
    loader = SkillLoader()
    skills = loader.scan_skills()

    print(f"\n📊 Skill加载统计:")
    print(f"  总数: {len(skills)}")

    python_skills = [k for k, v in loader._skill_paths.items() if v == "Python类"]
    skill_md_skills = [k for k, v in loader._skill_paths.items() if v != "Python类"]

    print(f"  Python类: {len([s for s in skills.keys() if 'growth' in str(type(skills[s]))])}")
    print(f"  SKILL.md: {len(skill_md_skills)}")

    print(f"\n📋 Skills列表:")
    for name in sorted(skills.keys()):
        path = loader._skill_paths.get(name, "内置")
        print(f"  - {name} ({path})")
