"""sessions_send 双向通信工具测试

测试场景：
1. 发送消息到不存在的会话 -> not_found
2. 轮次超过5次 -> max_rounds
3. 超时场景
4. 多轮对话
5. 回复接收
"""

import pytest
import time
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# 导入被测试的模块 - 使用正确的路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.sessions_send import (
    SessionsSendParams,
    SessionsSendResult,
    ConversationManager,
    sessions_send,
    MAX_ROUNDS,
)
from app.tools.sessions_spawn import (
    SpawnSessionManager,
    SpawnParams,
    SessionStatus,
)
from app.tools.sessions_receive import (
    sessions_receive,
    sessions_reply,
    SubAgentMessageQueue,
    SessionsReceiveParams,
    SessionsReplyParams,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_managers():
    """每个测试前重置单例"""
    ConversationManager.reset_instance()
    SpawnSessionManager.reset_instance()
    SubAgentMessageQueue.reset_instance()
    yield
    ConversationManager.reset_instance()
    SpawnSessionManager.reset_instance()
    SubAgentMessageQueue.reset_instance()


@pytest.fixture
def spawn_session():
    """创建一个测试用的子Agent会话"""
    manager = SpawnSessionManager.get_instance()
    params = SpawnParams(
        agent_type="test_agent",
        team_name="test_team"
    )
    return manager.create_session(params)


# ============================================================================
# Test 1: 发送消息到不存在的会话 -> not_found
# ============================================================================

def test_send_to_nonexistent_session():
    """Test: 发送消息到不存在的会话返回 not_found"""
    params = SessionsSendParams(
        session_key="spawn:nonexistent:agent_999",
        message="Hello",
        timeout_seconds=1
    )

    result = sessions_send(params)

    assert result.status == "not_found"
    assert result.reply is None
    assert result.error is not None
    assert "不存在" in result.error


# ============================================================================
# Test 2: 轮次超过5次 -> max_rounds
# ============================================================================

def test_max_rounds_exceeded(spawn_session):
    """Test: 轮次超过5次返回 max_rounds"""
    session_key = spawn_session.session_key
    manager = ConversationManager.get_instance()

    # 注册会话
    manager.register_session(session_key)

    # 模拟已达到最大轮次
    for _ in range(MAX_ROUNDS):
        manager._rounds[session_key] = MAX_ROUNDS

    params = SessionsSendParams(
        session_key=session_key,
        message="Hello",
        timeout_seconds=1
    )

    result = sessions_send(params)

    assert result.status == "max_rounds"
    assert result.reply is None
    assert f"最大对话轮次 {MAX_ROUNDS}" in result.error


# ============================================================================
# Test 3: 超时场景
# ============================================================================

def test_send_timeout(spawn_session):
    """Test: 等待回复超时"""
    session_key = spawn_session.session_key
    manager = ConversationManager.get_instance()

    # 注册会话但不提交回复
    manager.register_session(session_key)

    params = SessionsSendParams(
        session_key=session_key,
        message="Hello",
        timeout_seconds=1  # 1秒超时
    )

    result = sessions_send(params)

    # 超时状态应该是 timeout 或 error（取决于实现）
    assert result.status in ("timeout", "error")
    assert result.reply is None


# ============================================================================
# Test 4: 多轮对话
# ============================================================================

def test_multi_round_conversation(spawn_session):
    """Test: 多轮对话正常进行（测试轮次计数器）"""
    session_key = spawn_session.session_key
    manager = ConversationManager.get_instance()

    # 注册会话
    manager.register_session(session_key)

    # 前5轮应该能正常递增
    for round_num in range(1, MAX_ROUNDS + 1):
        # 模拟在发送之前的状态
        initial_round = manager.get_round(session_key)
        assert initial_round == round_num - 1

        # 手动触发轮次增加（模拟发送消息后的行为）
        manager._rounds[session_key] = round_num

        # 验证轮次已增加
        assert manager.get_round(session_key) == round_num

    # 第6轮应该被拒绝
    params = SessionsSendParams(
        session_key=session_key,
        message="Round 6",
        timeout_seconds=1
    )

    # 由于已经达到 MAX_ROUNDS，应该返回 max_rounds
    result = sessions_send(params)
    assert result.status == "max_rounds"


def test_conversation_rounds_counter(spawn_session):
    """Test: 对话轮次计数器正确递增"""
    session_key = spawn_session.session_key
    manager = ConversationManager.get_instance()

    manager.register_session(session_key)

    # 初始轮次为0
    assert manager.get_round(session_key) == 0

    # 发送消息后轮次应该增加
    # 注意：由于我们不实际等待回复，这里只测试计数器
    manager._rounds[session_key] = 1
    assert manager.get_round(session_key) == 1

    # 测试重置
    manager.reset_rounds(session_key)
    assert manager.get_round(session_key) == 0


# ============================================================================
# Test 5: 回复接收
# ============================================================================

def test_receive_reply(spawn_session):
    """Test: 子Agent可以提交回复给主Agent"""
    session_key = spawn_session.session_key
    queue = SubAgentMessageQueue.get_instance()

    # 子Agent提交回复
    params = SessionsReplyParams(
        session_key=session_key,
        reply="Task completed successfully",
        success=True
    )

    result = sessions_reply(params)

    assert result.status == "ok"
    assert result.session_key == session_key


def test_receive_reply_with_error(spawn_session):
    """Test: 子Agent可以提交错误信息"""
    session_key = spawn_session.session_key

    params = SessionsReplyParams(
        session_key=session_key,
        reply="Error: step 2 failed - missing dependency",
        success=False
    )

    result = sessions_reply(params)

    assert result.status == "ok"  # 提交本身应该成功


# ============================================================================
# Test 6: 子Agent接收消息
# ============================================================================

def test_sub_agent_receive_message(spawn_session):
    """Test: 子Agent可以接收主Agent发送的消息"""
    session_key = spawn_session.session_key
    agent_id = spawn_session.agent_id

    # 模拟主Agent发送消息到子Agent的收件箱
    queue = SubAgentMessageQueue.get_instance()
    queue.push_message(
        session_key=session_key,
        agent_id=agent_id,
        message="Please execute task XYZ",
        reply_required=True
    )

    # 子Agent接收消息
    params = SessionsReceiveParams(
        session_key=session_key,
        timeout_seconds=1
    )

    result = sessions_receive(params)

    assert result.has_message is True
    assert result.message == "Please execute task XYZ"
    assert result.reply_required is True


def test_sub_agent_empty_inbox(spawn_session):
    """Test: 子Agent收件箱为空时返回 has_message=False"""
    session_key = spawn_session.session_key
    agent_id = spawn_session.agent_id

    # 不发送任何消息

    params = SessionsReceiveParams(
        session_key=session_key,
        timeout_seconds=1
    )

    result = sessions_receive(params)

    assert result.has_message is False
    assert result.message is None


# ============================================================================
# Test 7: Session 管理
# ============================================================================

def test_create_session():
    """Test: 创建子Agent会话"""
    manager = SpawnSessionManager.get_instance()
    params = SpawnParams(
        agent_type="code_review",
        team_name="engineering"
    )

    result = manager.create_session(params)

    assert result.session_key.startswith("spawn:code_review:")
    assert result.agent_type == "code_review"
    assert result.agent_id is not None
    assert result.status == SessionStatus.PENDING.value


def test_get_session(spawn_session):
    """Test: 获取会话信息"""
    session_key = spawn_session.session_key
    manager = SpawnSessionManager.get_instance()

    session = manager.get_session(session_key)

    assert session is not None
    assert session["session_key"] == session_key
    assert session["agent_type"] == "test_agent"


def test_list_sessions(spawn_session):
    """Test: 列出所有会话"""
    manager = SpawnSessionManager.get_instance()

    result = manager.list_sessions()

    assert result.total >= 1
    assert len(result.sessions) >= 1


def test_delete_session(spawn_session):
    """Test: 删除会话"""
    session_key = spawn_session.session_key
    manager = SpawnSessionManager.get_instance()

    # 删除前应该存在
    assert manager.get_session(session_key) is not None

    # 删除
    success = manager.delete_session(session_key)
    assert success is True

    # 删除后不应该存在
    assert manager.get_session(session_key) is None


def test_update_session_status(spawn_session):
    """Test: 更新会话状态"""
    session_key = spawn_session.session_key
    manager = SpawnSessionManager.get_instance()

    from app.tools.sessions_spawn import UpdateSessionParams

    params = UpdateSessionParams(
        session_key=session_key,
        status=SessionStatus.RUNNING
    )

    result = manager.update_session(params)

    assert result.status == "ok"

    # 验证状态已更新
    session = manager.get_session(session_key)
    assert session["status"] == SessionStatus.RUNNING.value


# ============================================================================
# Test 8: 会话与 ConversationManager 集成
# ============================================================================

def test_session_registered_in_conversation_manager(spawn_session):
    """Test: 创建会话时自动注册到 ConversationManager"""
    session_key = spawn_session.session_key

    manager = ConversationManager.get_instance()

    assert manager.is_session_registered(session_key) is True


# ============================================================================
# Test 9: 参数验证
# ============================================================================

def test_params_validation():
    """Test: 参数模型验证"""
    # 有效的 params
    params = SessionsSendParams(
        session_key="spawn:test:agent_1",
        message="Hello",
        timeout_seconds=30
    )
    assert params.session_key == "spawn:test:agent_1"
    assert params.message == "Hello"
    assert params.timeout_seconds == 30

    # 测试默认值
    params2 = SessionsSendParams(
        session_key="spawn:test:agent_1",
        message="Hello"
    )
    assert params2.timeout_seconds == 30  # 默认值
    assert params2.round_limit == MAX_ROUNDS  # 默认值


# ============================================================================
# Test 10: 结果模型转换
# ============================================================================

def test_result_to_dict():
    """Test: 结果模型可以转换为字典"""
    result = SessionsSendResult(
        session_key="spawn:test:agent_1",
        status="ok",
        reply="Done",
        round=1,
        sent_at=datetime.utcnow(),
        reply_at=datetime.utcnow()
    )

    result_dict = result.to_dict()

    assert result_dict["session_key"] == "spawn:test:agent_1"
    assert result_dict["status"] == "ok"
    assert result_dict["reply"] == "Done"
    assert result_dict["round"] == 1
    assert "sent_at" in result_dict


# ============================================================================
# Test 11-15: 额外的边界场景
# ============================================================================

def test_extract_agent_id():
    """Test: 从 session_key 提取 agent_id"""
    from app.tools.sessions_receive import _extract_agent_id

    assert _extract_agent_id("spawn:code_review:agent_001") == "agent_001"
    assert _extract_agent_id("spawn:test:x") == "x"
    assert _extract_agent_id("invalid_key") is None
    assert _extract_agent_id("spawn:a:b:c") == "c"


def test_invalid_session_key_format():
    """Test: 无效的 session_key 格式"""
    params = SessionsSendParams(
        session_key="invalid_format",
        message="Hello",
        timeout_seconds=1
    )

    result = sessions_send(params)

    # 无效格式会导致 not_found
    assert result.status == "not_found"


def test_message_queue_clear():
    """Test: 清空子Agent收件箱"""
    queue = SubAgentMessageQueue.get_instance()

    # 添加消息
    queue.push_message("session_1", "agent_1", "msg1", True)
    queue.push_message("session_1", "agent_1", "msg2", True)

    assert queue.is_empty("agent_1") is False

    # 清空
    queue.clear("agent_1")

    assert queue.is_empty("agent_1") is True


def test_max_rounds_constant():
    """Test: MAX_ROUNDS 常量值正确"""
    assert MAX_ROUNDS == 5


def test_multiple_sessions_independent():
    """Test: 多个会话之间相互独立"""
    manager = SpawnSessionManager.get_instance()

    # 创建多个会话
    params1 = SpawnParams(agent_type="agent_1", team_name="team")
    params2 = SpawnParams(agent_type="agent_2", team_name="team")

    result1 = manager.create_session(params1)
    result2 = manager.create_session(params2)

    session_key1 = result1.session_key
    session_key2 = result2.session_key

    # 两个会话应该独立
    assert session_key1 != session_key2

    # ConversationManager 应该分别注册
    conv_manager = ConversationManager.get_instance()
    assert conv_manager.is_session_registered(session_key1) is True
    assert conv_manager.is_session_registered(session_key2) is True

    # 两个会话的轮次应该独立
    conv_manager.register_session(session_key1)
    conv_manager._rounds[session_key1] = 3
    conv_manager._rounds[session_key2] = 0

    assert conv_manager.get_round(session_key1) == 3
    assert conv_manager.get_round(session_key2) == 0


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
