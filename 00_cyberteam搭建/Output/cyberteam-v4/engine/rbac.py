#!/usr/bin/env python3
"""
CyberTeam V4 - RBAC 权限矩阵模块 (L3)

基于 Edict allowAgents 白名单机制，实现 CyberTeam 三层架构的权限控制：
- 决策层: CEO/COO/PM (Intake, Draft, Review, Dispatch)
- 协调层: 部门总监 (各BG总监)
- 执行层: 部门执行层 (HR, Finance, Admin, Operations, Legal, Engineering)

权限矩阵定义了 Agent 之间的通信白名单，只有在白名单中的 Agent 之间才能进行通信。

参考: Edict agent_config.json allowAgents 机制
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentLayer(Enum):
    """Agent 层级枚举"""
    # 决策层 - 三省
    CEO_ROUTE = "ceo_route"           # CEO路由 · 旨意分拣官
    COO_PLANNING = "coo_planning"     # COO规划 · 规划起草官
    CEO_REVIEW = "ceo_review"         # CEO审核 · 审议质量官
    PM_DISPATCH = "pm_dispatch"       # PM调度 · 执行调度官

    # 协调层 - 部门总监
    GROWTH_BG = "growth_bg"       # 增长部总监
    PRODUCT_BG = "product_bg"     # 产品部总监
    TECHNOLOGY_BG = "tech_bg"     # 技术部总监
    CONTENT_BG = "content_bg"     # 内容部总监
    OPERATIONS_BG = "ops_bg"      # 运营部总监
    FINANCE_BG = "finance_bg"     # 财务部总监
    HR_BG = "hr_bg"              # 人力部总监
    SECURITY_BG = "security_bg"  # 安全部总监
    DATA_BG = "data_bg"          # 数据部总监
    DESIGN_BG = "design_bg"      # 设计部总监
    MARKETING_BG = "mkt_bg"      # 市场部总监

    # 执行层 - 部门
    MARKETING = "marketing"           # 市场部 · 代码实现官
    LEGAL = "legal"                   # 法务部 · 测试审查官
    DESIGN = "design"                 # 设计部 · 文档编制官
    FINANCE = "finance"               # 财务部 · 数据分析官
    ENGINEERING = "engineering"      # 工程部 · 基础设施官
    HR = "hr"                         # 人力部 · 人力资源官

    # 特殊Agent
    USER = "user"               # 用户/皇上


class PermissionResult:
    """权限检查结果"""

    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason

    def __bool__(self) -> bool:
        return self.allowed

    def __repr__(self) -> str:
        status = "✓" if self.allowed else "✗"
        return f"<PermissionResult {status}: {self.reason}>"


@dataclass
class AgentInfo:
    """Agent 信息"""
    id: str
    label: str
    layer: AgentLayer
    role: str
    duty: str
    allow_agents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class RBACMatrix:
    """
    RBAC 权限矩阵

    基于 Edict allowAgents 白名单机制，实现 CyberTeam 三层架构的权限控制。

    层级结构:
    - 决策层 (CEO/COO/PM): taizi → zhongshu → menxia ↔ shangshu
    - 协调层 (部门总监): 受 shangshu 调度
    - 执行层 (部门): bingbu, xingbu, libu, hubu, gongbu, libu_hr

    权限规则:
    1. taizi(Intake)可以将任务分发给 zhongshu(Draft)
    2. zhongshu(Draft)可以与 menxia(Review)、shangshu(Dispatch)通信
    3. menxia(Review)可以与 zhongshu(Draft)、shangshu(Dispatch)通信
    4. shangshu(Dispatch)可以调度部门执行
    5. 部门只能与 shangshu 通信，不能直接与其他部门通信
    """

    # 默认权限矩阵 (Edict allowAgents 机制的 CyberTeam 映射)
    DEFAULT_MATRIX: dict[str, list[str]] = {
        # 决策层 - 三省
        "ceo_route": ["coo_planning"],                    # CEO路由 → COO规划
        "coo_planning": ["ceo_review", "pm_dispatch"],   # COO规划 → CEO审核、PM调度
        "ceo_review": ["coo_planning", "pm_dispatch"],    # CEO审核 → COO规划、PM调度
        "pm_dispatch": [                                  # PM调度 → 部门
            "marketing", "legal", "design", "finance",
            "engineering", "hr",
            # 协调层部门总监
            "growth_bg", "product_bg", "tech_bg",
            "content_bg", "ops_bg", "finance_bg",
            "hr_bg", "security_bg", "data_bg",
            "design_bg", "mkt_bg"
        ],

        # 协调层 - 部门总监 (只接受PM调度)
        "growth_bg": ["pm_dispatch"],
        "product_bg": ["pm_dispatch"],
        "tech_bg": ["pm_dispatch"],
        "content_bg": ["pm_dispatch"],
        "ops_bg": ["pm_dispatch"],
        "finance_bg": ["pm_dispatch"],
        "hr_bg": ["pm_dispatch"],
        "security_bg": ["pm_dispatch"],
        "data_bg": ["pm_dispatch"],
        "design_bg": ["pm_dispatch"],
        "mkt_bg": ["pm_dispatch"],

        # 执行层 - 部门 (只接受PM调度)
        "marketing": ["pm_dispatch"],
        "legal": ["pm_dispatch"],
        "design": ["pm_dispatch"],
        "finance": ["pm_dispatch"],
        "engineering": ["pm_dispatch"],
        "hr": ["pm_dispatch"],

        # 用户
        "user": ["ceo_route"],                        # 用户 → CEO路由
    }

    # Agent 元数据
    AGENT_METADATA: dict[str, dict[str, str]] = {
        "ceo_route": {"label": "CEO路由", "role": "旨意分拣官", "duty": "旨意分拣、紧急判断"},
        "coo_planning": {"label": "COO规划", "role": "规划起草官", "duty": "深度分析、任务拆解"},
        "ceo_review": {"label": "CEO审核", "role": "审议质量官", "duty": "方案审议、质量把控"},
        "pm_dispatch": {"label": "PM调度", "role": "执行调度官", "duty": "任务派发、结果汇总"},
        "marketing": {"label": "市场部", "role": "代码实现官", "duty": "代码开发、工程实现"},
        "legal": {"label": "法务部", "role": "测试审查官", "duty": "测试验证、质量审查"},
        "design": {"label": "设计部", "role": "文档编制官", "duty": "文档编写、规范制定"},
        "finance": {"label": "财务部", "role": "数据分析官", "duty": "数据分析、财务核算"},
        "engineering": {"label": "工程部", "role": "基础设施官", "duty": "基础设施、DevOps"},
        "hr": {"label": "人力部", "role": "人力资源官", "duty": "人才招聘、团队管理"},
        "growth_bg": {"label": "增长部", "role": "部门总监", "duty": "用户增长业务"},
        "product_bg": {"label": "产品部", "role": "部门总监", "duty": "产品规划管理"},
        "tech_bg": {"label": "技术部", "role": "部门总监", "duty": "技术架构决策"},
        "content_bg": {"label": "内容部", "role": "部门总监", "duty": "内容运营管理"},
        "ops_bg": {"label": "运营部", "role": "部门总监", "duty": "运营统筹协调"},
        "finance_bg": {"label": "财务部", "role": "部门总监", "duty": "财务预算管理"},
        "hr_bg": {"label": "人力部", "role": "部门总监", "duty": "人力资源管理"},
        "security_bg": {"label": "安全部", "role": "部门总监", "duty": "安全合规管理"},
        "data_bg": {"label": "数据部", "role": "部门总监", "duty": "数据治理分析"},
        "design_bg": {"label": "设计部", "role": "部门总监", "duty": "设计方向把控"},
        "mkt_bg": {"label": "市场部", "role": "部门总监", "duty": "市场营销推广"},
    }

    def __init__(self, custom_matrix: dict[str, list[str]] = None):
        """
        初始化 RBAC 权限矩阵

        Args:
            custom_matrix: 自定义权限矩阵，会与默认矩阵合并
        """
        self.matrix = {**self.DEFAULT_MATRIX}
        if custom_matrix:
            self.matrix.update(custom_matrix)

        # 构建反向索引 (谁可以调度我)
        self._reverse_index: dict[str, set[str]] = {}
        self._build_reverse_index()

        logger.info(f"RBACMatrix initialized with {len(self.matrix)} agents")

    def _build_reverse_index(self):
        """构建反向索引"""
        for agent, allowed_list in self.matrix.items():
            for target in allowed_list:
                if target not in self._reverse_index:
                    self._reverse_index[target] = set()
                self._reverse_index[target].add(agent)

    def can_communicate(self, from_agent: str, to_agent: str) -> PermissionResult:
        """
        检查两个 Agent 之间是否可以通信

        Args:
            from_agent: 源 Agent ID
            to_agent: 目标 Agent ID

        Returns:
            PermissionResult: 权限检查结果
        """
        # 相同的 Agent 可以与自己通信
        if from_agent == to_agent:
            return PermissionResult(True, "同一 Agent 内部通信")

        # 检查 from_agent 是否在 to_agent 的 allowAgents 白名单中
        allowed_list = self.matrix.get(from_agent, [])

        if to_agent in allowed_list:
            return PermissionResult(True, f"{from_agent} → {to_agent} 在白名单中")
        else:
            return PermissionResult(
                False,
                f"{from_agent} 无权直接联系 {to_agent}，"
                f"允许的目标: {allowed_list or '无'}"
            )

    def get_allowed_agents(self, agent_id: str) -> list[str]:
        """
        获取指定 Agent 可以通信的目标 Agent 列表

        Args:
            agent_id: Agent ID

        Returns:
            List[str]: 允许通信的 Agent ID 列表
        """
        return self.matrix.get(agent_id, [])

    def get_can_reach_me(self, agent_id: str) -> set[str]:
        """
        获取可以联系指定 Agent 的所有 Agent

        Args:
            agent_id: Agent ID

        Returns:
            Set[str]: 可以联系该 Agent 的所有 Agent
        """
        return self._reverse_index.get(agent_id, set())

    def can调度(self, from_agent: str, to_agent: str) -> PermissionResult:
        """
        检查 from_agent 是否有权调度 to_agent

        调度权限规则:
        - shangshu 可以调度所有部门和部门总监
        - 部门总监可以调度其下属执行层 Agent
        - 其他 Agent 之间的通信由 can_communicate 控制

        Args:
            from_agent: 调度方 Agent ID
            to_agent: 被调度方 Agent ID

        Returns:
            PermissionResult: 权限检查结果
        """
        # 检查基本通信权限
        basic_perm = self.can_communicate(from_agent, to_agent)
        if not basic_perm:
            return basic_perm

        # Dispatch可以调度部门和部门总监
        if from_agent == "shangshu":
            if to_agent in self.matrix.get("shangshu", []):
                return PermissionResult(True, "Dispatch有权调度")

        # 部门总监可以调度其管辖范围内的 Agent
        if from_agent.endswith("_bg"):
            # 部门总监只能调度执行层的部门
            six_bu_agents = {"bingbu", "xingbu", "libu", "hubu", "gongbu", "libu_hr"}
            if to_agent in six_bu_agents:
                return PermissionResult(True, f"{from_agent} 有权调度执行层")

        return PermissionResult(False, f"{from_agent} 无权调度 {to_agent}")

    def get_layer(self, agent_id: str) -> Optional[AgentLayer]:
        """
        获取 Agent 所属层级

        Args:
            agent_id: Agent ID

        Returns:
            Optional[AgentLayer]: Agent 层级
        """
        try:
            return AgentLayer(agent_id)
        except ValueError:
            return None

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """
        获取 Agent 详细信息

        Args:
            agent_id: Agent ID

        Returns:
            Optional[AgentInfo]: Agent 信息
        """
        layer = self.get_layer(agent_id)
        if not layer:
            return None

        metadata = self.AGENT_METADATA.get(agent_id, {})
        return AgentInfo(
            id=agent_id,
            label=metadata.get("label", agent_id),
            layer=layer,
            role=metadata.get("role", ""),
            duty=metadata.get("duty", ""),
            allow_agents=self.get_allowed_agents(agent_id),
            metadata={}
        )

    def get_agents_by_layer(self, layer: AgentLayer) -> list[str]:
        """
        获取指定层级的所有 Agent

        Args:
            layer: Agent 层级

        Returns:
            List[str]: 该层级的所有 Agent ID
        """
        return [agent_id for agent_id, _ in self.matrix.items()
                if self.get_layer(agent_id) == layer]

    def get_routing_path(self, from_agent: str, to_agent: str) -> list[str]:
        """
        计算两个 Agent 之间的路由路径

        如果两个 Agent 不能直接通信，尝试找到通过中间人的路由路径。

        Args:
            from_agent: 源 Agent ID
            to_agent: 目标 Agent ID

        Returns:
            List[str]: 路由路径，如果无法到达返回空列表
        """
        # 如果可以直接通信
        if self.can_communicate(from_agent, to_agent):
            return [from_agent, to_agent]

        # BFS 查找最短路径
        from collections import deque

        visited = {from_agent}
        queue = deque([(from_agent, [from_agent])])

        while queue:
            current, path = queue.popleft()

            for next_agent in self.get_allowed_agents(current):
                if next_agent == to_agent:
                    return path + [to_agent]

                if next_agent not in visited:
                    visited.add(next_agent)
                    queue.append((next_agent, path + [next_agent]))

        return []

    def validate_agent_config(self, agent_config: dict[str, Any]) -> list[str]:
        """
        验证 Agent 配置的权限矩阵是否有效

        Args:
            agent_config: Agent 配置字典 (来自 agent_config.json)

        Returns:
            List[str]: 错误列表，空列表表示验证通过
        """
        errors = []

        if "agents" not in agent_config:
            errors.append("配置缺少 'agents' 字段")
            return errors

        for agent in agent_config["agents"]:
            agent_id = agent.get("id", "unknown")
            allow_agents = agent.get("allowAgents", [])

            # 检查 allowAgents 中的目标是否都存在
            existing_agents = {a["id"] for a in agent_config["agents"]}
            existing_agents.add("user")  # user 是内置的

            for target in allow_agents:
                if target not in existing_agents:
                    errors.append(
                        f"Agent '{agent_id}' 的 allowAgents 包含不存在的 agent: {target}"
                    )

            # 检查权限是否符合 RBAC 规则
            if agent_id == "taizi" and "zhongshu" not in allow_agents:
                errors.append(f"Agent 'taizi' 必须能够联系 'zhongshu'")

            if agent_id == "shangshu":
                for bu in ["bingbu", "xingbu", "libu", "hubu", "gongbu", "libu_hr"]:
                    if bu not in allow_agents:
                        errors.append(
                            f"Agent 'shangshu' 必须能够调度部门，当前缺少 '{bu}'"
                        )

        return errors

    def to_dict(self) -> dict[str, list[str]]:
        """
        将权限矩阵转换为字典格式

        Returns:
            Dict[str, List[str]]: 权限矩阵字典
        """
        return self.matrix.copy()

    def to_agent_config(self) -> dict[str, Any]:
        """
        将权限矩阵转换为 Edict 格式的 agent_config

        Returns:
            Dict[str, Any]: Edict 格式的 Agent 配置
        """
        agents = []
        for agent_id in self.matrix:
            info = self.get_agent_info(agent_id)
            if info:
                agents.append({
                    "id": agent_id,
                    "label": info.label,
                    "role": info.role,
                    "duty": info.duty,
                    "allowAgents": info.allow_agents
                })

        return {"agents": agents}


# 全局单例实例
_default_rbac: Optional[RBACMatrix] = None


def get_rbac() -> RBACMatrix:
    """
    获取全局 RBAC 实例

    Returns:
        RBACMatrix: RBAC 权限矩阵实例
    """
    global _default_rbac
    if _default_rbac is None:
        _default_rbac = RBACMatrix()
    return _default_rbac


def check_permission(from_agent: str, to_agent: str) -> PermissionResult:
    """
    快捷函数：检查两个 Agent 之间的通信权限

    Args:
        from_agent: 源 Agent ID
        to_agent: 目标 Agent ID

    Returns:
        PermissionResult: 权限检查结果
    """
    return get_rbac().can_communicate(from_agent, to_agent)


def check_dispatch(from_agent: str, to_agent: str) -> PermissionResult:
    """
    快捷函数：检查调度权限

    Args:
        from_agent: 调度方 Agent ID
        to_agent: 被调度方 Agent ID

    Returns:
        PermissionResult: 权限检查结果
    """
    return get_rbac().can调度(from_agent, to_agent)
