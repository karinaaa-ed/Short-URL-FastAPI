import pytest
from src.shorturl.schemas import LinkResponse


@pytest.mark.asyncio
async def test_invalid_url(auth_client):
    test_data = {
        "original_url": "invalid-url",
        "username": "testuser"
    }
    response = await auth_client.post(
        "/links/shorten",
        json=test_data
    )
    print("Invalid URL response:", response.status_code, response.json())
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_nonexistent_redirect(client):
    response = await client.get("/links/nonexistent", follow_redirects=False)
    assert response.status_code == 404


async def test_duplicate_url_creation(auth_client):
    test_data = {
        "original_url": "https://example.com",
        "username": "testuser"
    }

    # Первое создание
    first = await auth_client.post("/links/shorten", json=test_data)
    assert first.status_code == 201
    LinkResponse(**first.json())

    # Второе создание
    second = await auth_client.post("/links/shorten", json=test_data)
    assert second.status_code == 201
    LinkResponse(**second.json())
    assert first.json()["short_code"] != second.json()["short_code"]
