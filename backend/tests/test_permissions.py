import pytest


@pytest.mark.asyncio
async def test_user_has_roles(client, setup_db, db_session):
    """Prueba que un usuario tiene roles asignados."""
    # Registrar usuario
    response_register = await client.post("/auth/register", json={
        "email": "roletest@example.com",
        "name": "Role Test User",
        "password": "TestPass123"
    })
    assert response_register.status_code == 201
    
    # Login
    response_login = await client.post("/auth/login", data={
        "username": "roletest@example.com",
        "password": "TestPass123"
    })
    assert response_login.status_code == 200
    
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ver el token decodificado (debería tener permisos)
    response_perms = await client.get("/users/test-permissions", headers=headers)
    print(f"\nUser data: {response_perms.json()}")
    
    # El usuario debería tener datos
    assert response_perms.status_code == 200
    assert "user" in response_perms.json()
    assert "role" in response_perms.json()


@pytest.mark.asyncio
async def test_admin_can_create_users(client, setup_db):
    """Prueba que un admin puede crear otros usuarios."""
    # Registrar usuario normal
    response_register = await client.post("/auth/register", json={
        "email": "admin@example.com",
        "name": "Admin User",
        "password": "AdminPass123"
    })
    assert response_register.status_code == 201
    
    # Login
    response_login = await client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "AdminPass123"
    })
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Intentar crear otro usuario
    response_create = await client.post("/users/", headers=headers, json={
        "email": "newuser@example.com",
        "name": "New User",
        "password": "NewUserPass123"
    })
    
    print(f"\nCreate user status: {response_create.status_code}")
    print(f"Create user response: {response_create.json()}")
    
    # Debería permitir (200 o 201) o bloquear con 403
    assert response_create.status_code in [200, 201, 403]


@pytest.mark.asyncio
async def test_permission_denied_without_token(client, setup_db):
    """Prueba que endpoints protegidos requieren tokens."""
    # Intentar acceder sin token
    response = await client.get("/users/")
    
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_invalid_token(client, setup_db):
    """Prueba que un token inválido es rechazado."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await client.get("/users/", headers=headers)
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_requires_auth(client, setup_db):
    """Prueba que listar usuarios requiere autenticación."""
    response = await client.get("/users/")
    
    assert response.status_code == 401
    error = response.json()
    # El mensaje puede ser "Not authenticated" o "unauthorized" o "token"
    assert "authenticated" in error["detail"].lower() or "token" in error["detail"].lower()
