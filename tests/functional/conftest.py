import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from src.database import Base, get_async_session
from src.main import app
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


os.environ["TESTING"] = "1"

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Создание тестовой БД."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Создание тестовой сессии."""
    async_session_maker = async_sessionmaker(
        bind=test_engine, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_session: AsyncSession):
    """Фикстура для тестового клиента FastAPI."""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_async_session] = override_get_db
    FastAPICache.init(InMemoryBackend())

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    FastAPICache.reset()


@pytest_asyncio.fixture
async def auth_client(client):
    # Регистрация
    reg_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Testpass123!",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    }
    reg_resp = await client.post("/auth/register", json=reg_data)
    assert reg_resp.status_code == 201

    # Логин
    login_resp = await client.post("/auth/jwt/login", data={
        "username": "test@example.com",
        "password": "Testpass123!"
    })
    assert login_resp.status_code == 200

    # Токен
    token = login_resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest_asyncio.fixture
async def another_auth_client(client):
    """Фикстура второго авторизованного клиента"""
    # Регистрация второго пользователя
    await client.post("/auth/register", json={
        "email": "another@example.com",
        "username": "anotheruser",
        "password": "Testpass123!",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })

    # Логин
    login_resp = await client.post("/auth/jwt/login", data={
        "username": "another@example.com",
        "password": "Testpass123!"
    })
    token = login_resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client



