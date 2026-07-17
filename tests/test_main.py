import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    """Test that the health endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway-boilerplate"


@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    """Test user registration flow."""
    payload = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "secret123",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert data["is_active"] is True
    assert "id" in data
    assert "password" not in data


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    """Test that registering with an existing email returns 409."""
    payload = {
        "email": "bob@example.com",
        "username": "bob",
        "password": "secret123",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.anyio
async def test_login(client: AsyncClient):
    """Test login flow and token response."""
    # Register first
    await client.post("/api/v1/auth/register", json={
        "email": "carol@example.com",
        "username": "carol",
        "password": "mypassword",
    })

    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "carol@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test that invalid credentials return 401."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401


@pytest.mark.anyio
async def test_jwt_protected_endpoint(client: AsyncClient):
    """Test that a protected endpoint requires a valid JWT."""
    # Without token
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No Authorization header

    # With invalid token
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.anyio
async def test_me_endpoint(client: AsyncClient):
    """Test the /auth/me endpoint with a valid token."""
    # Register and login
    await client.post("/api/v1/auth/register", json={
        "email": "dave@example.com",
        "username": "dave",
        "password": "pass123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "dave@example.com",
        "password": "pass123",
    })
    token = login_resp.json()["access_token"]

    # Access /me
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "dave@example.com"
    assert data["username"] == "dave"


@pytest.mark.anyio
async def test_crud_items(client: AsyncClient):
    """Test full item CRUD lifecycle."""
    # Register and login
    await client.post("/api/v1/auth/register", json={
        "email": "eve@example.com",
        "username": "eve",
        "password": "pass456",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "eve@example.com",
        "password": "pass456",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create item
    create_resp = await client.post("/api/v1/items", json={
        "title": "Test Item",
        "description": "A test item",
    }, headers=headers)
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    # Get item
    get_resp = await client.get(f"/api/v1/items/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Test Item"

    # List items
    list_resp = await client.get("/api/v1/items")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # Update item
    update_resp = await client.put(f"/api/v1/items/{item_id}", json={
        "title": "Updated Item",
    }, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Item"

    # Delete item
    delete_resp = await client.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert delete_resp.status_code == 204
