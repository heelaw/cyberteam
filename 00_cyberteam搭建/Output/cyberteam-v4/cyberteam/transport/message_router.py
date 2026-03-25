"""
Message Router - 消息路由模块

负责消息的路径规划和路由选择，支持直接路由和链式路由。
"""
from __future__ import annotations
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import threading


class RouteStrategy(Enum):
    """路由策略"""
    DIRECT = "direct"           # 直接路由
    CHAIN = "chain"             # 链式路由（经过多个Agent）
    BROADCAST = "broadcast"     # 广播
    ROUND_ROBIN = "round_robin" # 轮询


@dataclass
class RouteRule:
    """路由规则"""
    from_agent: str
    to_agent: str
    strategy: RouteStrategy = RouteStrategy.DIRECT
    via_agents: List[str] = field(default_factory=list)  # 链式路由经过的Agent
    conditions: Dict[str, str] = field(default_factory=dict)  # 触发条件


@dataclass
class RouteResult:
    """路由结果"""
    path: List[str]                    # 路由路径
    strategy: RouteStrategy            # 使用的策略
    hops: int                          # 跳数
    estimated_latency: float = 0.0     # 预估延迟（毫秒）


class MessageRouter:
    """
    消息路由器

    负责计算消息的最优路由路径，支持：
    - 直接路由：Agent到Agent直连
    - 链式路由：消息经过多个中间Agent
    - 广播路由：一份消息发送给多个接收者
    """

    def __init__(self):
        self._rules: Dict[str, RouteRule] = {}  # (from, to) -> Rule
        self._agents: Set[str] = set()          # 已知的Agent集合
        self._adjacency: Dict[str, Set[str]] = {}  # 邻接表：Agent -> 可达Agent
        self._lock = threading.RLock()
        self._round_robin_index: Dict[str, int] = {}  # 轮询计数器

    def register_agent(self, agent_id: str, reachable_agents: Optional[List[str]] = None) -> None:
        """
        注册Agent到路由系统

        Args:
            agent_id: Agent唯一标识
            reachable_agents: 该Agent可直接通信的其他Agent列表
        """
        with self._lock:
            self._agents.add(agent_id)
            if agent_id not in self._adjacency:
                self._adjacency[agent_id] = set()
            if reachable_agents:
                self._adjacency[agent_id].update(reachable_agents)

    def add_route_rule(self, rule: RouteRule) -> None:
        """
        添加路由规则

        Args:
            rule: 路由规则
        """
        with self._lock:
            key = (rule.from_agent, rule.to_agent)
            self._rules[key] = rule

    def route(self, message: dict) -> List[str]:
        """
        计算消息的路由路径

        Args:
            message: 消息字典，需包含 'from' 和 'to' 字段

        Returns:
            路由路径列表，如 ['agent_a', 'agent_b', 'agent_c']
        """
        from_agent = message.get("from")
        to_agent = message.get("to")

        if not from_agent or not to_agent:
            raise ValueError("消息必须包含 'from' 和 'to' 字段")

        # 查询是否有自定义规则
        rule_key = (from_agent, to_agent)
        rule = self._rules.get(rule_key)

        if rule:
            if rule.strategy == RouteStrategy.CHAIN and rule.via_agents:
                # 链式路由：from -> via_agents -> to
                return [from_agent] + rule.via_agents + [to_agent]
            elif rule.strategy == RouteStrategy.BROADCAST:
                # 广播：发送给所有可达Agent
                return [from_agent] + list(self._adjacency.get(from_agent, set()))
            elif rule.strategy == RouteStrategy.ROUND_ROBIN:
                # 轮询路由
                return self._round_robin_route(from_agent, to_agent)

        # 默认直接路由
        return [from_agent, to_agent]

    def _round_robin_route(self, from_agent: str, to_agent: str) -> List[str]:
        """轮询路由实现"""
        key = f"{from_agent}:{to_agent}"
        if key not in self._round_robin_index:
            self._round_robin_index[key] = 0

        reachable = list(self._adjacency.get(from_agent, set()))
        if not reachable:
            return [from_agent, to_agent]

        index = self._round_robin_index[key] % len(reachable)
        self._round_robin_index[key] = index + 1
        selected = reachable[index]

        return [from_agent, selected, to_agent]

    def get_path(self, from_agent: str, to_agent: str) -> List[str]:
        """
        获取两个Agent之间的路由路径（不涉及实际消息）

        Args:
            from_agent: 源Agent
            to_agent: 目标Agent

        Returns:
            最短路由路径
        """
        # 优先使用BFS找最短路径
        path = self._bfs_shortest_path(from_agent, to_agent)
        if path:
            return path

        # 回退到直接路由
        return [from_agent, to_agent]

    def _bfs_shortest_path(self, from_agent: str, to_agent: str) -> Optional[List[str]]:
        """BFS查找最短路径"""
        if from_agent == to_agent:
            return [from_agent]

        visited = {from_agent}
        queue = [(from_agent, [from_agent])]

        while queue:
            current, path = queue.pop(0)
            for neighbor in self._adjacency.get(current, set()):
                if neighbor == to_agent:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_all_reachable(self, from_agent: str) -> Set[str]:
        """
        获取从某个Agent可达的所有Agent

        Args:
            from_agent: 源Agent

        Returns:
            可达Agent集合
        """
        visited = set()
        queue = [from_agent]

        while queue:
            current = queue.pop(0)
            for neighbor in self._adjacency.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        visited.discard(from_agent)
        return visited

    def analyze_route(self, from_agent: str, to_agent: str) -> RouteResult:
        """
        分析路由详情

        Args:
            from_agent: 源Agent
            to_agent: 目标Agent

        Returns:
            路由分析结果
        """
        path = self.get_path(from_agent, to_agent)
        hops = len(path) - 1 if path else 0

        # 简单的延迟估算：每跳10ms
        estimated_latency = hops * 10.0

        return RouteResult(
            path=path,
            strategy=RouteStrategy.DIRECT,
            hops=hops,
            estimated_latency=estimated_latency
        )

    def remove_agent(self, agent_id: str) -> None:
        """从路由系统中移除Agent"""
        with self._lock:
            self._agents.discard(agent_id)
            self._adjacency.pop(agent_id, None)
            # 清理涉及该Agent的规则
            keys_to_remove = [k for k in self._rules if agent_id in k]
            for key in keys_to_remove:
                del self._rules[key]