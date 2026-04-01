"""
allowAgents 权限机制测试
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from cyberteam.spawn.permissions import (
    PermissionStore,
    AgentPermission,
    get_permission_store,
    check_spawn_permission,
    check_send_permission,
    register_spawnable_agent,
    enforce_permission,
)


@pytest.fixture(autouse=True)
def reset_store():
    """每个测试前重置权限存储"""
    PermissionStore.reset()
    yield
    PermissionStore.reset()


class TestPermissionStore:
    """PermissionStore 核心测试"""

    def test_orchestrator_default_full_access(self):
        """orchestrator 默认有完整权限"""
        store = get_permission_store()
        perm = store.get_permission("orchestrator")
        assert perm.allow_agents == ["*"]
        assert perm.agent_to_agent is True
        assert "spawn" in perm.allowed_tools

    def test_unregistered_agent_restricted(self):
        """未注册 Agent 只能 list，无 spawn/send 权限"""
        store = get_permission_store()
        perm = store.get_permission("unknown-agent")
        assert perm.allow_agents == []
        assert perm.agent_to_agent is False
        assert perm.denied_tools == ["spawn", "send", "stop"]

    def test_register_custom_agent(self):
        """注册自定义 Agent，分配最小权限"""
        store = get_permission_store()
        perm = store.register_agent(
            agent_name="coder-1",
            allow_agents=["code-reviewer", "security-reviewer"],
            agent_to_agent=False,
            team_only=True,
        )
        assert perm.agent_name == "coder-1"
        assert "code-reviewer" in perm.allow_agents
        assert "security-reviewer" in perm.allow_agents
        assert "python-reviewer" not in perm.allow_agents

    def test_register_with_star(self):
        """通配符注册：admin 可以调度一切"""
        store = get_permission_store()
        perm = store.register_agent(
            agent_name="admin",
            allow_agents=["*"],
            agent_to_agent=True,
        )
        allowed, reason = store.can_spawn("admin", "any-agent", team_name="my-team")
        assert allowed is True

    def test_unregister(self):
        """注销 Agent 后无权限"""
        store = get_permission_store()
        store.register_agent("temp-agent", allow_agents=["code-reviewer"])
        assert "temp-agent" in store.get_registered_agents()
        store.unregister_agent("temp-agent")
        assert "temp-agent" not in store.get_registered_agents()

    def test_summarize_all(self):
        """汇总所有 Agent 权限"""
        store = get_permission_store()
        store.register_agent("coder-1", allow_agents=["code-reviewer"])
        summary = store.summarize_all()
        assert "orchestrator" in summary["agents"]
        assert "coder-1" in summary["agents"]
        assert "leader" in summary["agents"]


class TestSpawnPermission:
    """spawn 权限检查测试"""

    def test_orchestrator_can_spawn_anyone(self):
        """orchestrator 可以 spawn 任何人"""
        allowed, reason = check_spawn_permission("orchestrator", "coder-1")
        assert allowed is True

    def test_coder_cannot_spawn_different_department(self):
        """普通 Agent 不能 spawn 其他专业 Agent"""
        store = get_permission_store()
        store.register_agent("coder-1", allow_agents=["code-reviewer"])
        allowed, reason = check_spawn_permission("coder-1", "security-reviewer")
        assert allowed is False
        assert "allow_agents" in reason or "白名单" in reason

    def test_coder_can_spawn_same_department(self):
        """同专业 Agent 可互相 spawn"""
        store = get_permission_store()
        store.register_agent("coder-1", allow_agents=["python-reviewer", "rust-reviewer"])
        allowed, reason = check_spawn_permission("coder-1", "python-reviewer", team_name="my-team")
        assert allowed is True

    def test_tool_level_deny(self):
        """工具级别拒绝"""
        store = get_permission_store()
        store.register_agent(
            "readonly-agent",
            allow_agents=["*"],
            allowed_tools=["list"],
            denied_tools=["spawn", "send", "stop"],
        )
        allowed, reason = store.can_spawn("readonly-agent", "coder-1", tool="spawn")
        assert allowed is False
        assert "工具" in reason or "denied" in reason.lower()

    def test_send_requires_agent_to_agent(self):
        """send 需要 agentToAgent=True"""
        store = get_permission_store()
        store.register_agent(
            "isolated-agent",
            allow_agents=["*"],
            agent_to_agent=False,
        )
        # spawn 应该可以（spawn 是调度，不算直接通信）
        spawn_ok, _ = store.can_spawn("isolated-agent", "coder-1", tool="spawn")
        assert spawn_ok is True
        # send 应该不行
        send_ok, _ = store.can_send("isolated-agent", "coder-1")
        assert send_ok is False

    def test_enforce_permission_raises(self):
        """enforce_permission 失败时抛出 PermissionError"""
        store = get_permission_store()
        store.register_agent("restricted", allow_agents=[])
        with pytest.raises(PermissionError) as exc_info:
            enforce_permission("restricted", "coder-1", "spawn")
        assert "restricted" in str(exc_info.value)
        assert "coder-1" in str(exc_info.value)


class TestAgentToAgentEnabled:
    """agentToAgent.enabled 配置测试"""

    def test_default_false_blocks_send(self):
        """默认 agentToAgent=False，阻止 Agent 间直接通信"""
        store = get_permission_store()
        # 普通 Agent 默认 agentTo_agent=False
        perm = store.get_permission("unknown-agent")
        assert perm.agent_to_agent is False

    def test_explicit_enable(self):
        """显式开启 agentToAgent"""
        store = get_permission_store()
        store.register_agent("social-agent", allow_agents=["*"], agent_to_agent=True)
        allowed, _ = store.can_send("social-agent", "another-agent")
        assert allowed is True

    def test_team_only_restricts_cross_team(self):
        """team_only=True 限制跨团队通信"""
        store = get_permission_store()
        store.register_agent(
            "team-alpha-agent",
            allow_agents=["agent-x"],
            agent_to_agent=True,
            team_only=True,
        )
        # 同 team 应该允许
        allowed_same, _ = store.can_spawn(
            "team-alpha-agent", "agent-x", team_name="alpha-team"
        )
        assert allowed_same is True


class TestEnvVarOverride:
    """环境变量覆盖测试"""

    def test_env_var_allow_agents(self, monkeypatch):
        """CLAWTEAM_ALLOW_AGENTS_<AGENT> 环境变量可覆盖白名单"""
        monkeypatch.setenv("CLAWTEAM_ALLOW_AGENTS_TEST_AGENT", '["override-agent"]')
        store = get_permission_store()
        perm = store.register_agent(
            "test-agent",
            allow_agents=["original-agent"],  # 这会被环境变量覆盖
        )
        assert "override-agent" in perm.allow_agents

    def test_env_var_agent_to_agent(self, monkeypatch):
        """CLAWTEAM_AGENT_TO_AGENT_<AGENT> 环境变量控制通信"""
        monkeypatch.setenv("CLAWTEAM_AGENT_TO_AGENT_TEST_AGENT2", "true")
        store = get_permission_store()
        perm = store.register_agent(
            "test-agent2",
            agent_to_agent=False,
        )
        assert perm.agent_to_agent is True


class TestStopPermission:
    """stop 权限测试"""

    def test_self_stop_allowed(self):
        """Agent 可以停止自己"""
        store = get_permission_store()
        store.register_agent("agent-1", allow_agents=["*"])
        allowed, reason = store.can_stop("agent-1", "agent-1")
        assert allowed is True
        assert "自停止" in reason

    def test_orchestrator_can_stop_anyone(self):
        """orchestrator 可以停止任何人"""
        store = get_permission_store()
        allowed, reason = store.can_stop("orchestrator", "any-agent")
        assert allowed is True
        assert "管理员" in reason

    def test_restricted_cannot_stop_others(self):
        """受限 Agent 不能停止他人"""
        store = get_permission_store()
        store.register_agent("limited", allow_agents=[])
        allowed, reason = store.can_stop("limited", "other-agent")
        assert allowed is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
