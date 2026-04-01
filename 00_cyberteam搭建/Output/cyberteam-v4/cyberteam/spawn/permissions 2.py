"""
allowAgents 权限机制 — IMA 核心安全层

实现 IMA 笔记的最小权限原则：
- 每个 Agent 只能调度白名单中的其他 Agent
- agentToAgent.enabled 控制是否允许 Agent 间直接通信
- spawn/send 操作必须通过权限检查

配置来源（优先级从高到低）：
1. 环境变量 CLAWTEAM_ALLOW_AGENTS_<FROM_AGENT>（JSON 列表）
2. TeamConfig 中的 allow_agents 字段
3. 全局默认值（仅 orchestrator 可用）
"""

from __future__ import annotations

import json
import os
from typing import Optional
from dataclasses import dataclass, field


# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class PermissionGrant:
    """单条权限授权记录"""
    from_agent: str
    to_agent: str
    allowed_tools: list[str] = field(default_factory=lambda: ["spawn", "send", "list"])
    condition: Optional[str] = None  # e.g. "team_only", "same_department"


@dataclass
class AgentPermission:
    """单个 Agent 的权限配置"""
    agent_name: str
    allow_agents: list[str]  # 允许调度哪些 Agent
    agent_to_agent: bool  # 是否允许与其他 Agent 直接通信
    team_only: bool  # 是否只允许与同 team 的 Agent 通信
    allowed_tools: list[str]
    denied_tools: list[str]


# ============================================================================
# 全局权限存储
# ============================================================================

class PermissionStore:
    """
    全局 Agent 权限存储（内存 + 配置覆盖）。

    架构：
    - 内存字典：动态注册的 Agent 权限
    - 配置覆盖：TeamConfig / 环境变量优先
    - 默认策略：只有 orchestrator 可用，无其他权限
    """

    _instance: Optional['PermissionStore'] = None

    def __init__(self):
        # agent_name -> AgentPermission
        self._permissions: dict[str, AgentPermission] = {}

        # 全局默认值：所有 Agent 的默认权限（保守策略）
        self._default_allowed_agents: list[str] = []
        self._default_agent_to_agent: bool = False
        self._default_team_only: bool = True

        # 已注册的 Agent 白名单（只读，不可越权 spawn）
        self._registered_agents: dict[str, dict] = {}

        self._init_defaults()

    @classmethod
    def get_instance(cls) -> 'PermissionStore':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """重置单例（测试用）"""
        cls._instance = None

    def _init_defaults(self) -> None:
        """初始化默认权限：orchestrator 有完整权限"""
        # orchestrator 可以调度所有注册过的 Agent
        self._permissions["orchestrator"] = AgentPermission(
            agent_name="orchestrator",
            allow_agents=["*"],  # orchestrator 可以调度一切
            agent_to_agent=True,
            team_only=False,
            allowed_tools=["spawn", "send", "list", "stop"],
            denied_tools=[],
        )
        # 其他 Agent 默认无调度权限
        self._permissions["leader"] = AgentPermission(
            agent_name="leader",
            allow_agents=["*"],
            agent_to_agent=True,
            team_only=True,
            allowed_tools=["spawn", "send", "list", "stop"],
            denied_tools=[],
        )

    # ── 注册 ──

    def register_agent(
        self,
        agent_name: str,
        allow_agents: Optional[list[str]] = None,
        agent_to_agent: bool = False,
        team_only: bool = True,
        allowed_tools: Optional[list[str]] = None,
        denied_tools: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> AgentPermission:
        """注册 Agent 到权限系统，分配其权限"""
        # 环境变量覆盖：CLAWTEAM_ALLOW_AGENTS_<AGENT_NAME>
        env_key = f"CLAWTEAM_ALLOW_AGENTS_{agent_name.upper().replace('-', '_')}"
        env_value = os.environ.get(env_key)
        if env_value:
            try:
                allow_agents = json.loads(env_value)
            except json.JSONDecodeError:
                allow_agents = [a.strip() for a in env_value.split(",")]

        # 环境变量控制 agentToAgent
        env_a2a = os.environ.get(f"CLAWTEAM_AGENT_TO_AGENT_{agent_name.upper().replace('-', '_')}")
        if env_a2a is not None:
            agent_to_agent = env_a2a.lower() in ("1", "true", "yes")

        permission = AgentPermission(
            agent_name=agent_name,
            allow_agents=allow_agents or [],
            agent_to_agent=agent_to_agent,
            team_only=team_only,
            allowed_tools=allowed_tools or ["spawn", "send", "list", "stop"],
            denied_tools=denied_tools or [],
        )
        self._permissions[agent_name] = permission
        self._registered_agents[agent_name] = metadata or {}

        return permission

    def unregister_agent(self, agent_name: str) -> bool:
        """注销 Agent"""
        self._permissions.pop(agent_name, None)
        self._registered_agents.pop(agent_name, None)
        return agent_name not in self._permissions

    # ── 查询 ──

    def get_permission(self, agent_name: str) -> AgentPermission:
        """获取 Agent 权限，找不到返回受限默认"""
        return self._permissions.get(agent_name, AgentPermission(
            agent_name=agent_name,
            allow_agents=[],
            agent_to_agent=False,
            team_only=True,
            allowed_tools=["list"],
            denied_tools=["spawn", "send", "stop"],
        ))

    def get_registered_agents(self) -> list[str]:
        """获取所有已注册的 Agent"""
        return list(self._registered_agents.keys())

    # ── 权限检查（核心方法） ──

    def can_spawn(
        self,
        from_agent: str,
        to_agent: str,
        tool: str = "spawn",
        team_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        检查 from_agent 是否有权 spawn to_agent。

        Args:
            from_agent: 调用方 Agent
            to_agent: 目标 Agent
            tool: 调用的工具名
            team_name: 当前 team（用于 team_only 检查）

        Returns:
            (是否允许, 原因)
        """
        perm = self.get_permission(from_agent)

        # 工具级别检查
        if tool in perm.denied_tools:
            return False, f"工具 '{tool}' 被禁止用于 {from_agent}"
        if (
            "*" not in perm.allowed_tools
            and tool not in perm.allowed_tools
        ):
            return False, f"工具 '{tool}' 未在 {from_agent} 的允许列表中"

        # agent_to_agent 全局开关
        if tool in ("send", "stop") and not perm.agent_to_agent:
            return False, f"{from_agent} 的 agentToAgent.enabled = False"

        # allow_agents 白名单检查（orchestrator/leader 永远可以）
        if from_agent not in ("orchestrator", "leader"):
            if "*" not in perm.allow_agents and to_agent not in perm.allow_agents:
                # team_only 特例：同 team 内 Agent 可互相调度
                if perm.team_only and team_name:
                    return True, f"team_only: {from_agent} 与 {to_agent} 同 team"
                return False, (
                    f"'{to_agent}' 不在 '{from_agent}' 的 allow_agents 白名单中。"
                    f" 当前白名单: {perm.allow_agents}"
                )

        return True, "允许"

    def can_send(
        self,
        from_agent: str,
        to_agent: str,
        team_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """检查 from_agent 是否可以向 to_agent 发送消息"""
        return self.can_spawn(from_agent, to_agent, tool="send", team_name=team_name)

    def can_list(
        self,
        from_agent: str,
        team_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """检查 from_agent 是否有权列出会话（通常所有 Agent 都可以）"""
        perm = self.get_permission(from_agent)
        if "list" in perm.denied_tools:
            return False, f"工具 'list' 被禁止用于 {from_agent}"
        return True, "允许"

    def can_stop(
        self,
        from_agent: str,
        target_agent: str,
        team_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """检查 from_agent 是否可以停止 target_agent"""
        perm = self.get_permission(from_agent)
        # orchestrator / leader 可以停止任何人
        if from_agent in ("orchestrator", "leader"):
            return True, "管理员权限"
        # 其他 Agent 只能停止自己
        if from_agent == target_agent:
            return True, "自停止"
        return self.can_spawn(from_agent, target_agent, tool="stop", team_name=team_name)

    # ── 便捷方法 ──

    def check_and_raise(
        self,
        from_agent: str,
        to_agent: str,
        tool: str,
        team_name: Optional[str] = None,
    ) -> None:
        """权限检查，失败则抛出 PermissionError"""
        allowed, reason = self.can_spawn(from_agent, to_agent, tool=tool, team_name=team_name)
        if not allowed:
            raise PermissionError(
                f"[allowAgents] {from_agent} 无法 {tool} {to_agent}: {reason}"
            )

    def summarize(self, agent_name: str) -> dict:
        """获取 Agent 权限摘要"""
        perm = self.get_permission(agent_name)
        return {
            "agent_name": agent_name,
            "allow_agents": perm.allow_agents,
            "agent_to_agent": perm.agent_to_agent,
            "team_only": perm.team_only,
            "allowed_tools": perm.allowed_tools,
            "denied_tools": perm.denied_tools,
        }

    def summarize_all(self) -> dict:
        """获取所有 Agent 权限摘要"""
        return {
            "agents": {name: self.summarize(name) for name in self._permissions},
            "total_registered": len(self._registered_agents),
            "default_policy": {
                "allow_agents": self._default_allowed_agents,
                "agent_to_agent": self._default_agent_to_agent,
                "team_only": self._default_team_only,
            },
        }


# ============================================================================
# 全局快捷函数
# ============================================================================

def get_permission_store() -> PermissionStore:
    return PermissionStore.get_instance()


def check_spawn_permission(
    from_agent: str,
    to_agent: str,
    team_name: Optional[str] = None,
) -> tuple[bool, str]:
    """检查 spawn 权限"""
    return get_permission_store().can_spawn(from_agent, to_agent, tool="spawn", team_name=team_name)


def check_send_permission(
    from_agent: str,
    to_agent: str,
    team_name: Optional[str] = None,
) -> tuple[bool, str]:
    """检查 send 权限"""
    return get_permission_store().can_send(from_agent, to_agent, team_name=team_name)


def register_spawnable_agent(
    agent_name: str,
    allow_agents: Optional[list[str]] = None,
    agent_to_agent: bool = False,
    team_only: bool = True,
    metadata: Optional[dict] = None,
) -> AgentPermission:
    """注册一个可被 spawn 的 Agent"""
    return get_permission_store().register_agent(
        agent_name=agent_name,
        allow_agents=allow_agents,
        agent_to_agent=agent_to_agent,
        team_only=team_only,
        metadata=metadata,
    )


def enforce_permission(
    from_agent: str,
    to_agent: str,
    tool: str,
    team_name: Optional[str] = None,
) -> None:
    """权限检查，失败则抛出异常"""
    get_permission_store().check_and_raise(from_agent, to_agent, tool, team_name)
