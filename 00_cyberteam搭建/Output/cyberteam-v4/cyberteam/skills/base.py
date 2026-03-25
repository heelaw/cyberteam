"""CyberTeam Skill 基类模块。

提供所有 Skill 的基类定义。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "CyberTeam"
    tags: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)  # 触发条件
    requires: List[str] = field(default_factory=list)  # 依赖的 Skill
    created_at: datetime = field(default_factory=datetime.now)


class BaseSkill(ABC):
    """Skill 基类

    所有 Skill 都应继承此类。
    """

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata
        self._initialized = False
        self._context: Dict[str, Any] = {}
        self._skill_path: Optional[Path] = None

    @abstractmethod
    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行 Skill"""
        pass

    def initialize(self) -> None:
        """初始化 Skill"""
        if not self._initialized:
            self._do_initialize()
            self._initialized = True

    def _do_initialize(self) -> None:
        """子类可覆盖的初始化逻辑"""
        pass

    def set_context(self, key: str, value: Any) -> None:
        """设置上下文"""
        self._context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self._context.get(key, default)

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def reset(self) -> None:
        """重置 Skill 状态"""
        self._context.clear()
        self._initialized = False

    def set_path(self, path: Path) -> None:
        """设置 Skill 路径"""
        self._skill_path = path

    @property
    def skill_path(self) -> Optional[Path]:
        """获取 Skill 路径"""
        return self._skill_path


class WritingSkill(BaseSkill):
    """写作 Skill 基类

    负责转化型文案创作工作流。
    """

    def __init__(self, metadata: SkillMetadata):
        super().__init__(metadata)
        self.current_stage: int = 0

    @abstractmethod
    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        pass

    async def stage_0_init(self, task: Any) -> Any:
        """Stage 0: 工作流初始化"""
        pass

    async def stage_1_user_research(self, task: Any) -> Any:
        """Stage 1: 用户需求挖掘"""
        pass

    async def stage_2_selling_points(self, task: Any) -> Any:
        """Stage 2: 产品卖点挖掘"""
        pass

    async def stage_3_pain_points(self, task: Any) -> Any:
        """Stage 3: 痛点定位"""
        pass

    async def stage_4_strategy(self, task: Any) -> Any:
        """Stage 4: 需求类型判断"""
        pass

    async def stage_5_channel(self, task: Any) -> Any:
        """Stage 5: 场景与渠道分析"""
        pass

    async def stage_6_draft(self, task: Any) -> Any:
        """Stage 6: 文案撰写"""
        pass

    async def stage_7_optimize(self, task: Any) -> Any:
        """Stage 7: 文案优化"""
        pass

    async def stage_8_tracking(self, task: Any) -> Any:
        """Stage 8: 效果追踪"""
        pass


class ContentReviewSkill(BaseSkill):
    """内容审核 Skill 基类

    负责事实核查、品牌审核、合规扫描。
    """

    @abstractmethod
    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        pass

    async def fact_check(self, content: str) -> Any:
        """事实核查"""
        pass

    async def brand_audit(self, content: str) -> Any:
        """品牌调性审核"""
        pass

    async def compliance_scan(self, content: str, platform: str = "general") -> Any:
        """合规风险扫描"""
        pass
