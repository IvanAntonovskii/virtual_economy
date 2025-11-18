import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from app.core.cache import cache_manager
from app.main import app
from fastapi.testclient import TestClient
import os

# Тестовая база данных
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

    # Создаем таблицы
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

    async with async_session() as session:
        yield session


@pytest.fixture
def client(test_session):
    """Test client для FastAPI"""

    # Переопределяем зависимость базы данных
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    # Отключаем кэширование для тестов
    cache_manager.redis = None

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_data(test_session):
    """Создает тестовые данные"""
    from app.models.user import User
    from app.models.product import Product

    # Тестовый пользователь
    test_user = User(
        username="test_user",
        email="test@example.com",
        balance=1000
    )

    # Тестовые товары
    test_products = [
        Product(
            name="Буст на день",
            description="Увеличивает доход на 50%",
            price=100,
            type="consumable"
        ),
        Product(
            name="Премиум-статус",
            description="Постоянный доступ",
            price=500,
            type="permanent"
        )
    ]

    test_session.add(test_user)
    for product in test_products:
        test_session.add(product)

    await test_session.commit()

    return {
        "user": test_user,
        "products": test_products
    }