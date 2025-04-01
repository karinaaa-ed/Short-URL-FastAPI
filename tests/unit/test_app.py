import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from src.app import app, lifespan
import logging


@pytest.fixture
def mock_redis():
    with patch('aioredis.from_url') as mock:
        mock_redis = MagicMock()
        mock.return_value = mock_redis
        yield mock_redis


@pytest.fixture
def test_client(mock_redis):
    with TestClient(app) as client:
        yield client


def test_app_initialization():
    """Тест инициализации FastAPI приложения"""
    assert isinstance(app, FastAPI)
    assert app.title == "FastAPI"
    assert app.version == "0.1.0"


def test_cors_settings(test_client):
    """Тест настроек CORS"""
    response = test_client.options(
        "/",
        headers={
            "Origin": "http://test.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Test"
        }
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


@pytest.mark.asyncio
async def test_lifespan(mock_redis):
    """Тест lifespan менеджера"""
    mock_app = MagicMock(spec=FastAPI)
    mock_app.state = {}

    async with lifespan(mock_app) as manager:
        assert isinstance(manager, type(None))
        assert hasattr(mock_app.state, "redis")
        assert mock_app.state.redis == mock_redis
        assert FastAPICache.get_backend() is not None

    mock_redis.close.assert_called_once()


def test_logging_configuration():
    """Тест конфигурации логирования"""
    assert logging.getLogger().level == logging.INFO


@patch('logging.basicConfig')
def test_lifespan_logging(mock_logging, mock_redis):
    """Тест настройки логирования в lifespan"""
    mock_app = MagicMock()
    mock_app.state = {}

    async def test():
        async with lifespan(mock_app):
            pass

    import asyncio
    asyncio.run(test())
    mock_logging.assert_called_once_with(level=logging.INFO)


def test_cache_initialization(mock_redis, test_client):
    """Тест инициализации кэша"""
    test_client.get("/")
    assert FastAPICache.get_backend() is not None
    assert hasattr(app.state, "redis")