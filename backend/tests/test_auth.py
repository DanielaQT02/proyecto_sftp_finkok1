import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_register_user(client, setup_db):
    """Prueba registro de usuario."""
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "TestPass123"
    })
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_user(client, setup_db):
    """Prueba login de usuario."""
    # Primero registra
    response_register = await client.post("/auth/register", json={
        "email": "login@example.com",
        "name": "Login User",
        "password": "LoginPass123"
    })
    
    print(f"\nRegister Status: {response_register.status_code}")
    print(f"Register Response: {response_register.json()}")
    
    # Luego intenta login
    response = await client.post("/auth/login", data={
        "username": "login@example.com",
        "password": "LoginPass123"
    })
    
    print(f"\nLogin Status: {response.status_code}")
    print(f"Login Response: {response.json()}")
    
    assert response.status_code == 200
    assert "access_token" in response.json()
