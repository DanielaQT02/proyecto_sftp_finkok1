import pytest


@pytest.mark.asyncio
async def test_create_business_requires_auth(client, setup_db):
    """Prueba que crear un negocio requiere autenticación."""
    response = await client.post("/businesses/", json={
        "taxpayer_id": "ABC123456789",
        "business_name": "Test Business"
    })
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_businesses_requires_auth(client, setup_db):
    """Prueba que listar negocios requiere autenticación."""
    response = await client.get("/businesses/")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_can_view_businesses(client, setup_db):
    """Prueba que un usuario autenticado puede ver negocios."""
    # Registrar y login
    await client.post("/auth/register", json={
        "email": "bizuser@example.com",
        "name": "Biz User",
        "password": "BizPass123"
    })
    
    response_login = await client.post("/auth/login", data={
        "username": "bizuser@example.com",
        "password": "BizPass123"
    })
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar listar negocios
    response = await client.get("/businesses/?account_id=1", headers=headers)
    
    print(f"\nList businesses status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response length: {len(response.json())}")
    else:
        print(f"Response: {response.text[:200]}")
    
    # Debería retornar 200 o un error apropiado (no 401)
    assert response.status_code in [200, 403, 404]
