"""
CyberTeam V4 Test Configuration

Provides shared pytest fixtures:
- test_engine: SQLite test database engine
- app: FastAPI application instance
"""
# pytest-asyncio: match backend/tests/pytest.ini
pytest_plugins = ["pytest_asyncio"]

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import event
from httpx import AsyncClient, ASGITransport

import sys
from pathlib import Path

# Project root directory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create session-level event loop (for async fixtures)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator:
    """Create isolated test database engine (SQLite in-memory)."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    # Create tables
    from backend.app.db import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
def app():
    """Get FastAPI application instance."""
    from backend.app.main import app as _app
    return _app


@pytest_asyncio.fixture(scope="function")
async def client(test_engine, app) -> AsyncGenerator:
    """Create test HTTP client, inject test database."""
    from backend.app.db import database as db_file_module
    from backend.app import db as db_module

    original_async_factory = db_file_module._async_session_factory
    original_factory = db_module._session_factory

    # Create test session factory
    test_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Override both db package and database.py module
    db_file_module._async_session_factory = test_session_factory
    db_module._async_session_factory = test_session_factory
    db_module._session_factory = test_session_factory

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=10.0) as ac:
        yield ac

    # Restore original config
    db_file_module._async_session_factory = original_async_factory
    db_module._async_session_factory = original_async_factory
    db_module._session_factory = original_factory


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide test database session."""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()
