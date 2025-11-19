import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Тестовая база данных - используем SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_virtual_economy.db"


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Тестовый engine для базы данных"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Импортируем и создаем таблицы
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Тестовая сессия базы данных"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Создаем сессию и возвращаем ее
    session = async_session()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture
def client():
    """Test client для FastAPI - упрощенная версия"""
    from fastapi.testclient import TestClient
    from app.main import app

    # Отключаем кэш для тестов
    from app.core.cache import cache_manager
    cache_manager.redis = None

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Пример данных пользователя"""
    return {"username": "testuser", "email": "test@example.com", "balance": 1000}