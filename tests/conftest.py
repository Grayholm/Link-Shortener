from httpx import ASGITransport, AsyncClient
import pytest

from src.dependencies import get_db
from src.database.db import async_session_null_pool
from src.database.config import settings
from src.main import app

@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "test", "Tests must be run in test mode. Please set MODE=test in your .env file."

@pytest.fixture
async def db():
    async def override_get_db():
        async with async_session_null_pool() as session:
            try:
                yield session
            finally:
                await session.rollback()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()

@pytest.fixture
async def ac(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac