import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import MagicMock, patch


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


def test_app_structure():
    """Тест структуры приложения"""
    assert isinstance(app, FastAPI)

    # Проверка наличия всех роутеров
    routes = {route.path for route in app.routes}
    assert "/auth/jwt/login" in routes
    assert "/auth/register" in routes
    assert "/protected-route" in routes
    assert "/unprotected-route" in routes
    assert "/links/" in routes
    assert "/report/" in routes


def test_unprotected_route(test_client):
    """Тест незащищенного маршрута"""
    response = test_client.get("/unprotected-route")
    assert response.status_code == 200
    assert response.json() == "Hello, anonym"


@pytest.mark.asyncio
async def test_protected_route_unauthorized(test_client):
    """Тест защищенного маршрута без аутентификации"""
    response = test_client.get("/protected-route")
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_protected_route_authorized(test_client):
    """Тест защищенного маршрута с аутентификацией"""
    mock_user = MagicMock()
    mock_user.email = "test@example.com"

    with patch('src.main.current_active_user', return_value=mock_user):
        response = test_client.get("/protected-route")
        assert response.status_code == 200
        assert response.json() == f"Hello, {mock_user.email}"


def test_auth_routers_registered():
    """Тест регистрации auth роутеров"""
    auth_routes = [
        route.path
        for route in app.routes
        if hasattr(route, "tags") and "auth" in route.tags
    ]
    assert "/auth/jwt/login" in auth_routes
    assert "/auth/register" in auth_routes


def test_uvicorn_run():
    """Тест запуска uvicorn (мокированный)"""
    with patch('uvicorn.run') as mock_run:
        with patch('__main__.__name__', '__main__'):
            mock_run.assert_called_once_with(
                "src.main:app",
                reload=True,
                host="0.0.0.0",
                log_level="info"
            )


@pytest.mark.parametrize("route,expected_status", [
    ("/auth/jwt/login", 200),
    ("/auth/register", 200),
    ("/nonexistent", 404)
])
def test_route_availability(test_client, route, expected_status):
    """Параметризованный тест доступности маршрутов"""
    response = test_client.get(route)
    assert response.status_code == expected_status


def test_shortlink_router_included():
    """Тест подключения роутера коротких ссылок"""
    shortlink_routes = [
        route.path
        for route in app.routes
        if route.path.startswith("/links")
    ]
    assert len(shortlink_routes) > 0
    assert "/links/shorten" in shortlink_routes


def test_tasks_router_included():
    """Тест подключения роутера задач"""
    tasks_routes = [
        route.path
        for route in app.routes
        if route.path.startswith("/report")
    ]
    assert len(tasks_routes) > 0
    assert "/report/send" in tasks_routes