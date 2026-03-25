"""CyberTeam Agent 注册表。

管理所有 Agent 的注册和发现。
"""

from typing import Dict, List, Optional, Type
from dataclasses import dataclass

from cyberteam.agents.base import BaseAgent, AgentMetadata


@dataclass
class AgentRegistration:
    """Agent 注册信息"""
    name: str
    agent_class: Type[BaseAgent]
    metadata: AgentMetadata
    category: str  # "thinking" or "specialized"


class AgentRegistry:
    """Agent 注册表

    单例模式，全局管理所有 Agent。
    """

    _instance: Optional['AgentRegistry'] = None
    _agents: Dict[str, AgentRegistration] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'AgentRegistry':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(
        self,
        name: str,
        agent_class: Type[BaseAgent],
        metadata: AgentMetadata,
        category: str = "general"
    ) -> None:
        """注册 Agent"""
        registration = AgentRegistration(
            name=name,
            agent_class=agent_class,
            metadata=metadata,
            category=category
        )
        self._agents[name] = registration

    def unregister(self, name: str) -> bool:
        """取消注册 Agent"""
        if name in self._agents:
            del self._agents[name]
            return True
        return False

    def get(self, name: str) -> Optional[AgentRegistration]:
        """获取 Agent 注册信息"""
        return self._agents.get(name)

    def get_agent_class(self, name: str) -> Optional[Type[BaseAgent]]:
        """获取 Agent 类"""
        reg = self._agents.get(name)
        return reg.agent_class if reg else None

    def list_agents(self, category: Optional[str] = None) -> List[str]:
        """列出所有 Agent 或指定类别的 Agent"""
        if category is None:
            return list(self._agents.keys())
        return [
            name for name, reg in self._agents.items()
            if reg.category == category
        ]

    def list_by_tag(self, tag: str) -> List[str]:
        """列出包含指定标签的所有 Agent"""
        return [
            name for name, reg in self._agents.items()
            if tag in reg.metadata.tags
        ]

    def get_by_category(self, category: str) -> List[AgentRegistration]:
        """获取指定类别的所有 Agent"""
        return [
            reg for reg in self._agents.values()
            if reg.category == category
        ]

    def exists(self, name: str) -> bool:
        """检查 Agent 是否已注册"""
        return name in self._agents

    def clear(self) -> None:
        """清空注册表（主要用于测试）"""
        self._agents.clear()

    def get_all_metadata(self) -> List[AgentMetadata]:
        """获取所有 Agent 的元数据"""
        return [reg.metadata for reg in self._agents.values()]


# 全局注册表实例
_global_registry = AgentRegistry.get_instance


def get_registry() -> AgentRegistry:
    """获取全局注册表"""
    return _global_registry()
