import pytest
from datetime import datetime, timedelta
from fastapi import status, HTTPException
from requests import Request

from src.database import Link, User, ExpiredLink
from src.shorturl.router import redirect_to_original, create_short_url, get_link_stats, update_link, delete_link, \
    search_links, get_project_links, get_expired_links, create_public_short_url
from src.shorturl.schemas import LinkResponse, LinkCreate, LinkCodeUpdate, PublicLinkCreate


@pytest.mark.asyncio
async def test_create_link(auth_client):
    test_data = {
        "original_url": "https://example.com",
        "username": "testuser"
    }
    response = await auth_client.post(
        "/links/shorten",
        json=test_data
    )
    assert response.status_code == 201
    LinkResponse(**response.json())


@pytest.mark.asyncio
async def test_redirect(client, auth_client):
    create_data = {
        "original_url": "https://example.com",
        "username": "testuser"
    }
    create_resp = await auth_client.post("/links/shorten", json=create_data)
    assert create_resp.status_code == 201

    short_code = create_resp.json()["short_code"]
    redirect_resp = await client.get(f"/links/{short_code}", follow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers["location"] == "https://example.com"

    redirect_resp = await client.get(
        f"/links/{short_code}",
        follow_redirects=False
    )
    assert redirect_resp.status_code == 307


@pytest.mark.asyncio
async def test_update_link(auth_client):
    # Создание ссылки
    create_resp = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com", "username": "testuser"}
    )
    short_code = create_resp.json()["short_code"]

    # Обновление
    update_resp = await auth_client.patch(
        f"/links/{short_code}",
        json={"original_url": "https://updated.com"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["original_url"] == "https://updated.com"


@pytest.mark.asyncio
async def test_link_stats(auth_client):
    create_resp = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://stats.com", "username": "testuser"}
    )
    stats_resp = await auth_client.get(f"/links/{create_resp.json()['short_code']}/stats")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["clicks"] == 0


@pytest.mark.asyncio
async def test_expired_links(auth_client):
    # Создание ссылки с истекшим сроком
    expired_date = datetime.now() - timedelta(days=1)
    create_resp = await auth_client.post(
        "/links/shorten",
        json={
            "original_url": "https://expired.com",
            "username": "testuser",
            "expires_at": expired_date.isoformat()
        }
    )

    expired_resp = await auth_client.get("/links/expired/")
    assert expired_resp.status_code == 200
    assert len(expired_resp.json()) > 0


@pytest.mark.asyncio
async def test_get_nonexistent_link_stats(auth_client):
    """Тест статистики для несуществующей ссылки"""
    response = await auth_client.get("/links/nonexistentcode/stats")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_link_unauthorized(auth_client, another_auth_client):
    """Тест попытки обновления чужой ссылки"""
    # Создаем ссылку первым пользователем
    create_resp = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://example.com", "username": "user1"}
    )

    # Пытаемся обновить вторым пользователем
    response = await another_auth_client.patch(
        f"/links/{create_resp.json()['short_code']}",
        json={"original_url": "https://hacked.com"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_link(client, auth_client):
    """Тест удаления ссылки"""
    create_resp = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://todelete.com", "username": "testuser"}
    )
    short_code = create_resp.json()["short_code"]

    # Удаляем
    delete_resp = await auth_client.delete(f"/links/{short_code}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Link deleted successfully"

    get_resp = await client.get(f"/links/{short_code}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_search_links(auth_client):
    """Тест поиска ссылок"""
    # Создание тестовых ссылок
    await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://searchtest.com/page1", "username": "testuser"}
    )
    await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://searchtest.com/page2", "username": "testuser"}
    )

    search_resp = await auth_client.get("/links/search?original_url=searchtest")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) == 2


@pytest.mark.asyncio
async def test_project_links(auth_client):
    """Тест получения ссылок проекта"""
    project_name = "testproject"
    # Создание ссылки проекта
    await auth_client.post(
        "/links/shorten",
        json={
            "original_url": "https://project.com/page1",
            "username": "testuser",
            "project": project_name
        }
    )

    project_resp = await auth_client.get(f"/links/projects/{project_name}")
    assert project_resp.status_code == 200
    assert len(project_resp.json()) == 1
    assert project_resp.json()[0]["project"] == project_name


@pytest.mark.asyncio
async def test_create_public_link(client):
    """Тест создания публичной ссылки без аутентификации"""
    response = await client.post(
        "/links/public/",
        json={"original_url": "https://public.com"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] is None


@pytest.mark.asyncio
async def test_public_link_custom_alias_rejection(client):
    """Тест запрета кастомных алиасов для публичных ссылок"""
    response = await client.post(
        "/links/public/",
        json={
            "original_url": "https://public.com",
            "custom_alias": "mypublic"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Custom aliases are not allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_inactive_link_redirect(client, auth_client):
    """Тест редиректа для неактивной ссылки"""
    create_resp = await auth_client.post(
        "/links/shorten",
        json={"original_url": "https://inactive.com", "username": "testuser"}
    )
    short_code = create_resp.json()["short_code"]

    await auth_client.patch(
        f"/links/{short_code}",
        json={"is_active": False}
    )

    redirect_resp = await client.get(f"/links/{short_code}")
    assert redirect_resp.status_code == status.HTTP_404_NOT_FOUND


async def test_create_short_url_with_custom_alias(db, user):
    link_data = LinkCreate(
        original_url="https://example.com",
        custom_alias="custom",
        expires_at=None,
        project="test"
    )
    response = await create_short_url(link_data, db, user)
    assert response.short_code == "custom"
    assert response.is_custom is True

    # Проверка на дубликат
    with pytest.raises(HTTPException) as exc_info:
        await create_short_url(link_data, db, user)
    assert exc_info.value.status_code == 400


async def test_create_short_url_without_custom_alias(db, user):
    link_data = LinkCreate(
        original_url="https://example.com",
        expires_at=None,
        project="test"
    )
    response = await create_short_url(link_data, db, user)
    assert len(response.short_code) == 6
    assert response.is_custom is False


async def test_redirect_to_original(db, link):
    response = await redirect_to_original(link.short_code, db)
    assert response.status_code == 302
    assert response.headers["location"] == link.original_url

    # Проверка счетчика кликов
    updated_link = await db.get(Link, link.id)
    assert updated_link.clicks == 1
    assert updated_link.last_clicked_at is not None


async def test_get_link_stats(db, user, link):
    response = await get_link_stats(link.short_code, db, user)
    assert response.original_url == link.original_url

    # Проверка запрета доступа для другого пользователя
    other_user = User(id=2, email="other@example.com")
    with pytest.raises(HTTPException) as exc_info:
        await get_link_stats(link.short_code, db, other_user)
    assert exc_info.value.status_code == 403


async def test_update_link(db, user, link):
    new_code = LinkCodeUpdate(short_code="newcode")
    response = await update_link(link.short_code, new_code, db, user)
    assert response.short_code == "newcode"

    # Проверка на дубликат
    other_link = Link(short_code="existing", original_url="https://example.org", user_id=user.id)
    db.add(other_link)
    await db.commit()
    with pytest.raises(HTTPException) as exc_info:
        await update_link(link.short_code, LinkCodeUpdate(short_code="existing"), db, user)
    assert exc_info.value.status_code == 400


async def test_delete_link(db, user, link, mock_redis):
    response = await delete_link(link.short_code, Request({"type": "http"}), db, user)
    assert response["message"] == "Link deleted successfully"

    # Проверка, что ссылка удалена из БД
    deleted_link = await db.get(Link, link.id)
    assert deleted_link is None

    # Проверка очистки кэша (мок Redis)
    mock_redis.delete.assert_awaited()


async def test_search_links(db, user):
    link = Link(original_url="https://example.com/search", user_id=user.id)
    db.add(link)
    await db.commit()

    response = await search_links("search", db, user)
    assert len(response) == 1
    assert response[0].original_url == "https://example.com/search"


async def test_get_project_links(db, user):
    link = Link(original_url="https://example.com", project="test", user_id=user.id)
    db.add(link)
    await db.commit()

    response = await get_project_links("test", db, user)
    assert len(response) == 1
    assert response[0].project == "test"


async def test_get_expired_links(db, user):
    expired_link = ExpiredLink(original_url="https://expired.com", short_code="expired", user_id=user.id)
    db.add(expired_link)
    await db.commit()

    response = await get_expired_links(db, user)
    assert len(response) == 1
    assert response[0].short_code == "expired"


async def test_create_public_short_url(db):
    link_data = PublicLinkCreate(original_url="https://public.com", expires_at=None, project="public")
    response = await create_public_short_url(link_data, db)
    assert response.user_id is None

    # Проверка ограничения на количество ссылок
    for _ in range(99):
        await create_public_short_url(link_data, db)
    with pytest.raises(HTTPException) as exc_info:
        await create_public_short_url(link_data, db)
    assert exc_info.value.status_code == 403

