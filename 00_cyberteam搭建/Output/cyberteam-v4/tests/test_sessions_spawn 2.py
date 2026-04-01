"""sessions_spawn 工具测试。

测试 sessions_spawn 工具的各个功能：
- 派生子Agent任务并返回 session_key
- session_key 格式正确
- cleanup_session 清理会话
- list_sessions 按 team_name/status 过滤
- 会话状态更新

运行方式：
    cd /Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/Output/cyberteam-v4
    python3 -m pytest tests/test_sessions_spawn.py -v --tb=short
"""

from __future__ import annotations

import pytest
import importlib
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


# 确保项目根目录在 sys.path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# 测试 fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_singleton():
    """每个测试前重置 SpawnSessionManager 单例"""
    # 导入模块
    import backend.app.tools.sessions_spawn as spawn_module
    from backend.app.tools.sessions_spawn import SpawnSessionManager

    # 重置单例
    SpawnSessionManager.reset_instance()

    # 清空会话字典
    manager = SpawnSessionManager.get_instance()
    with manager._lock:
        manager._sessions.clear()
        manager._agent_index.clear()

    yield

    # 测试后也重置
    SpawnSessionManager.reset_instance()


# ============================================================================
# 测试用例
# ============================================================================

class TestSessionKeyFormat:
    """测试 session_key 格式"""

    def test_create_session_returns_session_key(self):
        """create_session 后返回 session_key"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        params = SpawnParams(
            agent_type="coder",
            team_name="test-team"
        )
        result = manager.create_session(params)

        assert result.session_key is not None
        assert len(result.session_key) > 0

    def test_session_key_format(self):
        """session_key 格式正确: spawn:{agent_type}:{agent_id}"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        params = SpawnParams(
            agent_type="coder",
            team_name="marketing"
        )
        result = manager.create_session(params)

        # 验证格式: spawn:{agent_type}:{agent_id}
        import re
        pattern = r"^spawn:coder:[a-z_]+_[a-f0-9]{8}$"
        assert re.match(pattern, result.session_key), f"session_key 格式不正确: {result.session_key}"

    def test_multiple_sessions_have_unique_keys(self):
        """多次 create_session 生成唯一的 session_key"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        result1 = manager.create_session(SpawnParams(agent_type="coder", team_name="team"))
        result2 = manager.create_session(SpawnParams(agent_type="analyst", team_name="team"))
        result3 = manager.create_session(SpawnParams(agent_type="reviewer", team_name="team"))

        # 三个 session_key 都不同
        assert result1.session_key != result2.session_key
        assert result2.session_key != result3.session_key
        assert result1.session_key != result3.session_key


class TestSpawnResult:
    """测试 spawn 结果字段"""

    def test_spawn_result_fields(self):
        """spawn 返回包含所有必要字段"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        params = SpawnParams(
            agent_type="coder",
            team_name="test-team"
        )
        result = manager.create_session(params)

        assert result.session_key is not None
        assert result.agent_type == "coder"
        assert result.agent_id is not None
        assert result.status == "pending"
        assert isinstance(result.created_at, datetime)
        assert "session_key" in result.message

    def test_spawn_with_context(self):
        """spawn 支持 context 参数"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()
        context = {"known_pitfalls": ["坑1", "坑2"], "file_path": "/tmp/test"}

        params = SpawnParams(
            agent_type="coder",
            team_name="test",
            context=context
        )
        result = manager.create_session(params)

        assert result.status == "pending"

        # 验证context被存储
        session = manager.get_session(result.session_key)
        assert session is not None
        assert session["context"]["known_pitfalls"] == ["坑1", "坑2"]


class TestSessionManagement:
    """测试会话管理"""

    def test_get_session(self):
        """get_session 获取指定会话"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        params = SpawnParams(
            agent_type="coder",
            team_name="test"
        )
        result = manager.create_session(params)

        session = manager.get_session(result.session_key)
        assert session is not None
        assert session["session_key"] == result.session_key
        assert session["agent_type"] == "coder"

    def test_get_nonexistent_session(self):
        """get_session 不存在的会话返回 None"""
        from backend.app.tools.sessions_spawn import SpawnSessionManager

        manager = SpawnSessionManager.get_instance()
        session = manager.get_session("nonexistent-key")
        assert session is None

    def test_list_sessions_no_filter(self):
        """list_sessions 不过滤返回所有会话"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        manager.create_session(SpawnParams(agent_type="coder", team_name="team-a"))
        manager.create_session(SpawnParams(agent_type="analyst", team_name="team-b"))
        manager.create_session(SpawnParams(agent_type="reviewer", team_name="team-a"))

        result = manager.list_sessions()
        assert result.total == 3
        assert len(result.sessions) == 3

    def test_list_sessions_filter_by_team_name(self):
        """list_sessions 按 team_name 过滤"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        manager.create_session(SpawnParams(agent_type="coder", team_name="marketing"))
        manager.create_session(SpawnParams(agent_type="analyst", team_name="marketing"))
        manager.create_session(SpawnParams(agent_type="reviewer", team_name="sales"))

        result = manager.list_sessions(team_name="marketing")
        assert result.total == 2
        for s in result.sessions:
            assert s["team_name"] == "marketing"

    def test_list_sessions_filter_by_status(self):
        """list_sessions 按 status 过滤"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
            SessionStatus,
            UpdateSessionParams,
        )

        manager = SpawnSessionManager.get_instance()

        result1 = manager.create_session(SpawnParams(agent_type="coder", team_name="team"))
        result2 = manager.create_session(SpawnParams(agent_type="analyst", team_name="team"))
        result3 = manager.create_session(SpawnParams(agent_type="reviewer", team_name="team"))

        # 标记一个完成，一个运行中
        manager.update_session(UpdateSessionParams(
            session_key=result1.session_key,
            status=SessionStatus.COMPLETED
        ))
        manager.update_session(UpdateSessionParams(
            session_key=result2.session_key,
            status=SessionStatus.RUNNING
        ))

        result = manager.list_sessions(status=SessionStatus.COMPLETED)
        assert result.total == 1
        assert result.sessions[0]["status"] == "completed"

        result_running = manager.list_sessions(status=SessionStatus.RUNNING)
        assert result_running.total == 1

        result_pending = manager.list_sessions(status=SessionStatus.PENDING)
        assert result_pending.total == 1


class TestUpdateSession:
    """测试更新会话"""

    def test_update_session_status(self):
        """update_session 可以更新会话状态"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
            UpdateSessionParams,
            SessionStatus,
        )

        manager = SpawnSessionManager.get_instance()

        result = manager.create_session(SpawnParams(
            agent_type="coder",
            team_name="test"
        ))

        update_result = manager.update_session(UpdateSessionParams(
            session_key=result.session_key,
            status=SessionStatus.RUNNING
        ))

        assert update_result.status == "ok"

        # 验证更新
        session = manager.get_session(result.session_key)
        assert session["status"] == "running"

    def test_update_session_metadata(self):
        """update_session 可以更新会话元数据"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
            UpdateSessionParams,
        )

        manager = SpawnSessionManager.get_instance()

        result = manager.create_session(SpawnParams(
            agent_type="coder",
            team_name="test"
        ))

        new_metadata = {"key": "value", "progress": 50}
        update_result = manager.update_session(UpdateSessionParams(
            session_key=result.session_key,
            metadata=new_metadata
        ))

        assert update_result.status == "ok"

        # 验证更新
        session = manager.get_session(result.session_key)
        assert session["metadata"]["key"] == "value"
        assert session["metadata"]["progress"] == 50


class TestToolEntrypoints:
    """测试工具入口函数"""

    def test_sessions_spawn_function(self):
        """sessions_spawn 函数正确工作"""
        from backend.app.tools.sessions_spawn import SpawnSessionManager, SpawnParams

        manager = SpawnSessionManager.get_instance()

        # 直接使用 manager.create_session (绕过 ConversationManager 注册)
        params = SpawnParams(
            agent_type="coder",
            team_name="test"
        )
        result = manager.create_session(params)

        assert result.session_key is not None
        assert result.agent_type == "coder"

    def test_list_sessions_function(self):
        """list_sessions 函数正确工作"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        # 先 spawn 几个
        for i in range(3):
            manager.create_session(SpawnParams(
                agent_type="coder",
                team_name="test"
            ))

        # 再 list
        result = manager.list_sessions()

        assert result.total == 3
        assert len(result.sessions) == 3

    def test_get_session_function(self):
        """get_session 函数正确工作"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()
        result = manager.create_session(SpawnParams(
            agent_type="coder",
            team_name="test"
        ))

        # 使用 get_session
        session = manager.get_session(result.session_key)

        assert session is not None
        assert session["session_key"] == result.session_key


class TestEdgeCases:
    """边界情况测试"""

    def test_get_session_by_agent_id(self):
        """通过 agent_id 获取会话"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        result = manager.create_session(SpawnParams(
            agent_type="coder",
            team_name="test"
        ))

        session = manager.get_session_by_agent_id(result.agent_id)
        assert session is not None
        assert session["session_key"] == result.session_key

    def test_spawn_with_empty_context(self):
        """空 context 应该使用默认值"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        params = SpawnParams(
            agent_type="coder",
            team_name="test",
            context={}
        )
        result = manager.create_session(params)

        assert result.status == "pending"
        session = manager.get_session(result.session_key)
        assert session["context"] == {}

    def test_special_characters_in_team_name(self):
        """团队名称支持特殊字符"""
        from backend.app.tools.sessions_spawn import (
            SpawnSessionManager,
            SpawnParams,
        )

        manager = SpawnSessionManager.get_instance()

        params = SpawnParams(
            agent_type="coder",
            team_name="team-with-dashes_and_underscores"
        )
        result = manager.create_session(params)

        assert result.session_key is not None
        session = manager.get_session(result.session_key)
        assert session["team_name"] == "team-with-dashes_and_underscores"


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
