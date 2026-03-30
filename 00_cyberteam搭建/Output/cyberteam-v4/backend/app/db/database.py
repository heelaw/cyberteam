"""数据库连接管理 - 抄 Magic。

核心功能：
- 异步 SQLAlchemy 引擎创建
- Session 工厂管理
- 生命周期管理（init/close）
- 支持 SQLite（开发）和 PostgreSQL（生产）

连接字符串格式：
- SQLite: sqlite+aiosqlite:///./cyberteam.db
- PostgreSQL: postgresql+asyncpg://user:pass@localhost/dbname
"""

from typing import AsyncGenerator, Optional, Union
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
import logging

from ..config import get_settings

log = logging.getLogger("cyberteam.db")

# 基础类
Base = declarative_base()

# 全局引擎和 session 工厂
_engine = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def _create_engine():
    """创建数据库引擎。"""
    settings = get_settings()

    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

    log.info(f"Database engine created: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}")
    return engine


async def init_db() -> None:
    """初始化数据库：创建引擎和表。"""
    global _engine, _async_session_factory

    _engine = _create_engine()
    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # 创建表
    from .models import Base
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    log.info("Database tables created/verified")


async def close_db() -> None:
    """关闭数据库连接。"""
    global _engine

    if _engine:
        await _engine.dispose()
        _engine = None
        log.info("Database connections closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库 Session 的依赖注入。

    用法:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


AsyncSessionLocal = _async_session_factory
