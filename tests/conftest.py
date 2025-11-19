import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import MetaData

# Тестовая база данных - используем SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_virtual_economy.db"

# Создаем базовый метаданные для тестов
metadata = MetaData()


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_session(test_engine):
    """Тестовая сессия базы данных"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture(scope="session")
async def test_engine():
    """Тестовый engine для базы данных"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Тестовая сессия базы данных"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def client():
    """Test client для FastAPI - упрощенная версия"""
    # Импортируем ТОЛЬКО когда нужно
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Пример данных пользователя"""
    return {"username": "testuser", "email": "test@example.com", "balance": 1000}


@pytest.fixture
def sample_product_data():
    """Пример данных товара"""
    return {"name": "Test Product", "description": "Test Description", "price": 100, "type": "consumable"}


@pytest.fixture
async def test_session(test_engine):
    """Тестовая сессия базы данных"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


