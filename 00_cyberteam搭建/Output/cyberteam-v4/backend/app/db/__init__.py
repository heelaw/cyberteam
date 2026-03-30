"""DB 模块 - 数据库连接和模型。"""

from .database import (
    get_db,
    init_db,
    close_db,
    AsyncSessionLocal,
    Base,
    # 测试覆盖用：暴露私有变量
    _engine,
    _async_session_factory,
)
from .models import User, Conversation, Message, AgentExecution, BudgetTracking

# 别名：与旧 db.py 兼容
_session_factory = _async_session_factory

__all__ = [
    "get_db",
    "init_db",
    "close_db",
    "AsyncSessionLocal",
    "_engine",           # 测试覆盖用
    "_async_session_factory",  # 测试覆盖用
    "_session_factory",   # 别名兼容
    "Base",
    "User",
    "Conversation",
    "Message",
    "AgentExecution",
    "BudgetTracking",
]
