"""CyberTeam V4 数据库连接管理。"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .config import get_settings
from .models import Base

log = logging.getLogger("cyberteam.db")

# 全局引擎和会话工厂
_engine = None
_session_factory = None


async def init_db():
    """初始化数据库连接。"""
    global _engine, _session_factory

    settings = get_settings()
    _engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
    )

    # 创建表
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话工厂
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    log.info(f"Database initialized: {settings.database_url}")


async def close_db():
    """关闭数据库连接。"""
    global _engine

    if _engine:
        await _engine.dispose()
        log.info("Database connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（用于 FastAPI 依赖注入）。"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _session_factory() as session:
        yield session


async def get_session() -> AsyncSession:
    """获取数据库会话（同步方式，用于非依赖注入场景）。"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    return _session_factory()