"""MCP sessions 工具集成测试。

测试 cyberteam/mcp/tools/sessions.py 模块：
- sessions_spawn: 派发子 Agent 并返回 session_id
- sessions_send: 双向 ping-pong 通信
- sessions_list: 列出活跃会话
- sessions_stop: 停止会话

运行方式：
    cd /Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/Output/cyberteam-v4
    python3 -m pytest tests/test_mcp_sessions.py -v --tb=short
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clean_session_store():
    """每个测试前清理 SessionStore 数据"""
    from cyberteam.team.models import get_data_dir

    for team in ["test-mcp-team", "test-import-chain"]:
        test_data_dir = get_data_dir() / "sessions" / team
        if test_data_dir.exists():
            import shutil
            shutil.rmtree(test_data_dir, ignore_errors=True)

    yield

    for team in ["test-mcp-team", "test-import-chain"]:
        test_data_dir = get_data_dir() / "sessions" / team
        if test_data_dir.exists():
            import shutil
            shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture
def mock_spawn():
    """Mock TmuxBackend + TeamManager.add_member（sessions_spawn 内部导入）"""
    with patch("cyberteam.spawn.tmux_backend.TmuxBackend") as mock_tmux, \
         patch("cyberteam.team.manager.TeamManager.add_member") as mock_add:
        mock_tmux_instance = MagicMock()
        mock_tmux_instance.spawn.return_value = "Agent 'test' spawned in tmux"
        mock_tmux.return_value = mock_tmux_instance
        mock_add.return_value = None
        yield {"tmux": mock_tmux_instance, "add_member": mock_add}


@pytest.fixture
def mock_spawn_and_mailbox():
    """Mock spawn + MailboxManager（sessions_send 使用）"""
    with patch("cyberteam.spawn.tmux_backend.TmuxBackend") as mock_tmux, \
         patch("cyberteam.team.manager.TeamManager.add_member") as mock_add, \
         patch("cyberteam.mcp.tools.sessions.MailboxManager") as mock_mail_cls:
        mock_tmux_instance = MagicMock()
        mock_tmux_instance.spawn.return_value = "Agent spawned in tmux"
        mock_tmux.return_value = mock_tmux_instance
        mock_add.return_value = None

        mock_mail = MagicMock()
        mock_mail.send.return_value = MagicMock()
        mock_mail.receive.return_value = []
        mock_mail_cls.return_value = mock_mail

        yield {"tmux": mock_tmux_instance, "mailbox": mock_mail}


# ============================================================================
# Test: sessions_spawn
# ============================================================================

class TestSessionsSpawn:
    """测试 sessions_spawn 工具"""

    def test_spawn_returns_session_id(self, mock_spawn):
        """spawn 后返回 session_id"""
        from cyberteam.mcp.tools.sessions import sessions_spawn

        result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="test-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="审查 login.py 代码",
        )

        assert "sessionId" in result
        assert result["sessionId"] is not None
        assert len(result["sessionId"]) == 12
        assert result["agentName"] == "test-agent"
        assert result["teamName"] == "test-mcp-team"

    def test_spawn_status_spawned_on_success(self, mock_spawn):
        """成功 spawn 时 status 为 spawned"""
        from cyberteam.mcp.tools.sessions import sessions_spawn

        result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="test-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="审查代码",
        )

        assert result["status"] == "spawned"

    def test_spawn_status_error_on_backend_failure(self):
        """backend 失败时 status 为 error"""
        from cyberteam.mcp.tools.sessions import sessions_spawn

        with patch("cyberteam.spawn.tmux_backend.TmuxBackend") as mock_tmux, \
             patch("cyberteam.team.manager.TeamManager.add_member"):
            mock_tmux_instance = MagicMock()
            mock_tmux_instance.spawn.side_effect = Exception("tmux not found")
            mock_tmux.return_value = mock_tmux_instance

            result = sessions_spawn(
                team_name="test-mcp-team",
                agent_name="test-agent",
                agent_id="code-reviewer",
                agent_type="python",
                task="审查代码",
            )

        assert result["status"] == "error"
        assert "error" in result  # error 字符串在 spawnResult 中

    def test_spawn_persists_session_state(self, mock_spawn):
        """spawn 后 SessionStore 保存了状态"""
        from cyberteam.mcp.tools.sessions import sessions_spawn
        from cyberteam.spawn.sessions import SessionStore

        result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="persist-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="审查代码",
            timeout_seconds=300,
        )

        store = SessionStore("test-mcp-team")
        session = store.load("persist-agent")
        assert session is not None
        assert session.agent_name == "persist-agent"
        assert session.state.get("timeout") == 300

    def test_spawn_with_model_hint(self, mock_spawn):
        """spawn 支持 model 参数"""
        from cyberteam.mcp.tools.sessions import sessions_spawn

        result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="model-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="审查代码",
            model="sonnet",
        )

        assert result["status"] == "spawned"
        assert result["modelHint"] == "sonnet"

    def test_spawn_multiple_unique_session_ids(self, mock_spawn):
        """多次 spawn 生成唯一 session_id"""
        from cyberteam.mcp.tools.sessions import sessions_spawn

        ids = []
        for i in range(5):
            result = sessions_spawn(
                team_name="test-mcp-team",
                agent_name=f"agent-{i}",
                agent_id="code-reviewer",
                agent_type="python",
                task=f"任务{i}",
            )
            ids.append(result["sessionId"])

        assert len(ids) == len(set(ids))

    def test_spawn_prompt_length_recorded(self, mock_spawn):
        """spawn 记录 prompt 长度"""
        from cyberteam.mcp.tools.sessions import sessions_spawn

        task = "审查 login.py 中的 SQL 注入漏洞，这是一个长任务描述"

        result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="prompt-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task=task,
        )

        assert "promptLength" in result
        assert result["promptLength"] > 0


# ============================================================================
# Test: sessions_list
# ============================================================================

class TestSessionsList:
    """测试 sessions_list 工具"""

    def test_list_empty_team(self):
        """空 team 返回空列表"""
        from cyberteam.mcp.tools.sessions import sessions_list

        result = sessions_list(team_name="test-mcp-team")

        assert result["teamName"] == "test-mcp-team"
        assert result["sessions"] == []
        assert result["total"] == 0

    def test_list_returns_all_sessions(self, mock_spawn):
        """spawn 后 list 能看到所有会话"""
        from cyberteam.mcp.tools.sessions import sessions_spawn, sessions_list

        for i in range(3):
            sessions_spawn(
                team_name="test-mcp-team",
                agent_name=f"list-agent-{i}",
                agent_id="code-reviewer",
                agent_type="python",
                task=f"任务{i}",
            )

        result = sessions_list(team_name="test-mcp-team")

        assert result["total"] == 3
        assert len(result["sessions"]) == 3
        names = [s["agentName"] for s in result["sessions"]]
        for i in range(3):
            assert f"list-agent-{i}" in names

    def test_list_filter_by_agent_name(self, mock_spawn):
        """sessions_list 支持 agent_name_filter 前缀匹配"""
        from cyberteam.mcp.tools.sessions import sessions_spawn, sessions_list

        sessions_spawn(
            team_name="test-mcp-team",
            agent_name="filter-python-1",
            agent_id="code-reviewer",
            agent_type="python",
            task="任务1",
        )
        sessions_spawn(
            team_name="test-mcp-team",
            agent_name="filter-rust-1",
            agent_id="rust-reviewer",
            agent_type="rust",
            task="任务2",
        )

        result = sessions_list(
            team_name="test-mcp-team",
            agent_name_filter="filter-python",
        )

        assert result["total"] == 1
        assert result["sessions"][0]["agentName"] == "filter-python-1"

    def test_list_enriches_with_status_fields(self, mock_spawn):
        """sessions_list 包含 alive 和 status 字段"""
        from cyberteam.mcp.tools.sessions import sessions_spawn, sessions_list

        sessions_spawn(
            team_name="test-mcp-team",
            agent_name="alive-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="任务",
        )

        result = sessions_list(team_name="test-mcp-team")

        assert len(result["sessions"]) > 0
        session = result["sessions"][0]
        assert "alive" in session
        assert "status" in session
        assert "sessionId" in session


# ============================================================================
# Test: sessions_send
# ============================================================================

class TestSessionsSend:
    """测试 sessions_send 双向通信"""

    def test_send_to_nonexistent_session(self):
        """向不存在的 session 发送返回错误"""
        from cyberteam.mcp.tools.sessions import sessions_send

        result = sessions_send(
            team_name="test-mcp-team",
            session_id="nonexistent-session",
            from_agent="orchestrator",
            to_agent="ghost-agent",
            content="你好",
        )

        assert result["status"] == "error"
        assert "error" in result
        assert "No session" in result["error"]

    def test_send_with_round_limit_timeout(self, mock_spawn_and_mailbox):
        """sessions_send 达到 round_limit 后超时"""
        from cyberteam.mcp.tools.sessions import sessions_spawn, sessions_send

        spawn_result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="round-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="任务",
        )

        result = sessions_send(
            team_name="test-mcp-team",
            session_id=spawn_result["sessionId"],
            from_agent="orchestrator",
            to_agent="round-agent",
            content="请完成代码审查",
            round_limit=2,
        )

        assert "roundCount" in result
        assert "response" in result
        assert result["roundCount"] >= 1

    def test_send_ping_pong_receives_response(self, mock_spawn_and_mailbox):
        """sessions_send 收到子 Agent 响应"""
        from cyberteam.mcp.tools.sessions import sessions_spawn, sessions_send

        spawn_result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="pong-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="任务",
        )

        mock_response = MagicMock()
        mock_response.content = "代码审查完成，发现 2 处问题"
        mock_response.request_id = "any-id"
        mock_response.from_agent = "pong-agent"

        mock_spawn_and_mailbox["mailbox"].receive.side_effect = [[], [mock_response]]

        result = sessions_send(
            team_name="test-mcp-team",
            session_id=spawn_result["sessionId"],
            from_agent="orchestrator",
            to_agent="pong-agent",
            content="审查结果是什么？",
            round_limit=3,
        )

        assert result["response"] == "代码审查完成，发现 2 处问题"
        assert result["status"] == "ok"


# ============================================================================
# Test: sessions_stop
# ============================================================================

class TestSessionsStop:
    """测试 sessions_stop 工具"""

    def test_stop_spawned_session(self, mock_spawn):
        """sessions_stop 停止已 spawn 的 session"""
        from cyberteam.mcp.tools.sessions import sessions_spawn, sessions_stop

        spawn_result = sessions_spawn(
            team_name="test-mcp-team",
            agent_name="stop-agent",
            agent_id="code-reviewer",
            agent_type="python",
            task="任务",
        )

        # stop_agent 在 sessions.py 内部从 cyberteam.spawn.registry 导入
        with patch("cyberteam.spawn.registry.stop_agent") as mock_stop:
            mock_stop.return_value = True

            result = sessions_stop(
                team_name="test-mcp-team",
                agent_name="stop-agent",
                session_id=spawn_result["sessionId"],
            )

        assert result["agentName"] == "stop-agent"
        assert result["status"] == "stopped"

    def test_stop_nonexistent_returns_status(self, mock_spawn):
        """sessions_stop 不存在的 session 返回 status 字段"""
        from cyberteam.mcp.tools.sessions import sessions_stop

        with patch("cyberteam.spawn.registry.stop_agent", side_effect=Exception("not found")):
            result = sessions_stop(
                team_name="test-mcp-team",
                agent_name="ghost-agent",
                session_id="ghost-session",
            )

        assert "status" in result


# ============================================================================
# Test: _build_spawn_context
# ============================================================================

class TestBuildSpawnContext:
    """测试 _build_spawn_context 上下文构建"""

    def test_context_contains_task(self):
        """上下文包含任务描述"""
        from cyberteam.mcp.tools.sessions import _build_spawn_context

        result = _build_spawn_context(
            team_name="test-team",
            agent_name="test-agent",
            task="审查 login.py 的 SQL 注入",
        )

        assert "审查 login.py 的 SQL 注入" in result
        assert "## Task" in result

    def test_context_contains_coordination_protocol(self):
        """上下文包含协调协议"""
        from cyberteam.mcp.tools.sessions import _build_spawn_context

        result = _build_spawn_context(
            team_name="test-team",
            agent_name="test-agent",
            task="任务",
        )

        assert "## Coordination Protocol" in result
        assert "clawteam task" in result
        assert "clawteam inbox send" in result

    def test_context_contains_skill_summary(self):
        """上下文包含技能摘要"""
        from cyberteam.mcp.tools.sessions import _build_spawn_context

        result = _build_spawn_context(
            team_name="test-team",
            agent_name="test-agent",
            task="任务",
            context={"skill_summary": "使用 Python 审查代码，重点关注 SQL 注入"},
        )

        assert "## Skill Context" in result
        assert "SQL 注入" in result


# ============================================================================
# Test: TOOL_FUNCTIONS 注册
# ============================================================================

class TestToolRegistration:
    """测试新工具是否正确注册到 MCP"""

    def test_sessions_tools_in_toolf_functions(self):
        """sessions_spawn/send/list/stop 在 TOOL_FUNCTIONS 中"""
        from cyberteam.mcp import TOOL_FUNCTIONS

        tool_names = [f.__name__ for f in TOOL_FUNCTIONS]

        assert "sessions_spawn" in tool_names
        assert "sessions_send" in tool_names
        assert "sessions_list" in tool_names
        assert "sessions_stop" in tool_names

    def test_sessions_tools_count(self):
        """TOOL_FUNCTIONS 总数 >= 28"""
        from cyberteam.mcp import TOOL_FUNCTIONS

        assert len(TOOL_FUNCTIONS) >= 28


# ============================================================================
# Test: Orchestrator IMA 知识分层
# ============================================================================

class TestOrchestratorKnowledgeLayering:
    """测试 Orchestrator 的 IMA 知识分层结构"""

    def test_orchestrator_soul_exists(self):
        soul_path = project_root / "AGENTS/orchestrator/Orchestrator/SOUL.md"
        assert soul_path.exists()
        content = soul_path.read_text(encoding="utf-8")
        assert "Never Execute Directly" in content
        assert "Orchestrator" in content

    def test_orchestrator_soul_no_direct_execution(self):
        soul_path = project_root / "AGENTS/orchestrator/Orchestrator/SOUL.md"
        content = soul_path.read_text(encoding="utf-8")
        assert "❌ 禁止直接执行" in content

    def test_orchestrator_skill_exists(self):
        skill_path = project_root / "AGENTS/orchestrator/Orchestrator/SKILL.md"
        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "sessions_spawn" in content
        assert ("TRAP" in content or "陷阱" in content)

    def test_orchestrator_agent_exists(self):
        agent_path = project_root / "AGENTS/orchestrator/Orchestrator/AGENT.md"
        assert agent_path.exists()

    def test_orchestrator_memory_dir_exists(self):
        memory_path = project_root / "AGENTS/orchestrator/Orchestrator/memory"
        assert memory_path.exists()
        assert memory_path.is_dir()


# ============================================================================
# Test: Import Chain 完整性
# ============================================================================

class TestImportChain:
    """测试导入链完整性"""

    def test_mcp_init_imports_sessions(self):
        from cyberteam.mcp import TOOL_FUNCTIONS
        names = [f.__name__ for f in TOOL_FUNCTIONS]
        assert "sessions_spawn" in names

    def test_session_store_load_save(self):
        from cyberteam.spawn.sessions import SessionStore

        store = SessionStore("test-import-chain")

        saved = store.save(
            agent_name="import-test-agent",
            session_id="test-123",
            last_task_id="task-456",
            state={"status": "running", "model": "sonnet"},
        )
        assert saved.agent_name == "import-test-agent"

        loaded = store.load("import-test-agent")
        assert loaded is not None
        assert loaded.session_id == "test-123"
        assert loaded.state["model"] == "sonnet"

        store.clear("import-test-agent")
        assert store.load("import-test-agent") is None


# ============================================================================
# Run
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
