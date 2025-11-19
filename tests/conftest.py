import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Test database - using SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_virtual_economy.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Import and create tables
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session():
    # Вместо async_generator возвращаем мок сессии
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session

    # Create session and return it
    session = async_session()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture
def client():
    """Test client for FastAPI - simplified version"""
    from fastapi.testclient import TestClient
    from app.main import app

    # Disable cache for tests
    from app.core.cache import cache_manager
    cache_manager.redis = None

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Sample user data"""
    return {"username": "testuser", "email": "test@example.com", "balance": 1000}