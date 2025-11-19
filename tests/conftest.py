import pytest
import asyncio
from unittest.mock import AsyncMock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_session():
    """Mock session for unit tests"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


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