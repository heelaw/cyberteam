"""CyberTeam Agent 基类模块。

提供所有 Agent 的基类定义，包括思维专家和专业 Agent。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentMetadata:
    """Agent 元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "CyberTeam"
    tags: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Agent 基类

    所有思维专家和专业 Agent 都应继承此类。
    """

    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
        self._initialized = False
        self._context: Dict[str, Any] = {}

    @abstractmethod
    async def think(self, input_data: Any) -> Any:
        """思考过程 - 子类必须实现"""
        pass

    @abstractmethod
    async def execute(self, task: Any) -> Any:
        """执行过程 - 子类必须实现"""
        pass

    def initialize(self) -> None:
        """初始化 Agent"""
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
        """重置 Agent 状态"""
        self._context.clear()
        self._initialized = False


class ThinkingExpert(BaseAgent):
    """思维专家基类

    14个思维专家的基类，提供通用思维框架注入能力。
    """

    def __init__(self, metadata: AgentMetadata, domain: str):
        super().__init__(metadata)
        self.domain = domain
        self.thinking_frameworks: List[str] = []

    async def think(self, input_data: Any) -> Any:
        """注入思维框架的思考过程"""
        self.initialize()
        return await self._think_with_frameworks(input_data)

    @abstractmethod
    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """子类实现具体思维框架"""
        pass

    def add_framework(self, framework: str) -> None:
        """添加思维框架"""
        if framework not in self.thinking_frameworks:
            self.thinking_frameworks.append(framework)


class SpecializedAgent(BaseAgent):
    """专业 Agent 基类

    用于swarm orchestrator、debate moderator等专业角色。
    """

    async def think(self, input_data: Any) -> Any:
        self.initialize()
        return await self._specialized_think(input_data)

    @abstractmethod
    async def _specialized_think(self, input_data: Any) -> Any:
        """子类实现专业思考"""
        pass
