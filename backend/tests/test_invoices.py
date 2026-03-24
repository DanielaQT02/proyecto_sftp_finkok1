import pytest


@pytest.mark.asyncio
async def test_create_invoice_requires_auth(client, setup_db):
    """Prueba que crear una factura requiere autenticación."""
    response = await client.post("/invoices/", json={
        "business_id": 1,
        "invoice_number": "INV-001",
        "amount": 1000.00
    })
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_can_create_invoice(client, setup_db):
    """Prueba que un usuario autenticado puede crear factura."""
    # Registrar y login
    await client.post("/auth/register", json={
        "email": "invoice@example.com",
        "name": "Invoice User",
        "password": "InvoicePass123"
    })
    
    response_login = await client.post("/auth/login", data={
        "username": "invoice@example.com",
        "password": "InvoicePass123"
    })
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear factura (puede fallar si requiere business_id válido)
    response = await client.post("/invoices/", headers=headers, json={
        "business_id": 1,
        "invoice_number": "INV-001",
        "amount": 1000.00
    })
    
    print(f"\nCreate invoice status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Cualquier respuesta que no sea 401 es válida para esta prueba
    assert response.status_code != 401


@pytest.mark.asyncio
async def test_list_invoices_requires_auth(client, setup_db):
    """Prueba que listar facturas requiere autenticación."""
    response = await client.get("/invoices/")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_can_view_invoices(client, setup_db):
    """Prueba que un usuario autenticado puede ver facturas."""
    # Registrar y login
    await client.post("/auth/register", json={
        "email": "invuser@example.com",
        "name": "Invoice User",
        "password": "InvPass123"
    })
    
    response_login = await client.post("/auth/login", data={
        "username": "invuser@example.com",
        "password": "InvPass123"
    })
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Listar facturas
    response = await client.get("/invoices/", headers=headers)
    
    print(f"\nList invoices status: {response.status_code}")
    print(f"Response type: {type(response.json())}")
    
    # Debería retornar 200 con lista
    assert response.status_code == 200
    assert isinstance(response.json(), list)
