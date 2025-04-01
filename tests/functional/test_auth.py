import pytest

@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "newpass",
    })
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_login(client):
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "loginpass",
    })
    response = await client.post("/auth/jwt/login", data={
        "username": "login@example.com",
        "password": "loginpass",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()