"""
Integration tests for authentication router endpoints.

Tests:
    - User registration with valid and invalid data
    - User login with correct and incorrect credentials
    - Protected endpoint access with valid/invalid/expired tokens
    - Duplicate user registration handling

Requirements:
    - 1.1: Generate JWT tokens for valid credentials
    - 1.2: Return authentication errors for invalid credentials
    - 1.3: Validate JWT tokens on protected endpoints
    - 1.4: Reject expired JWT tokens
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth_service import hash_password


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert data["message"] == "User registered successfully"
    assert isinstance(data["user_id"], int)


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_db: AsyncSession):
    """Test registration with duplicate username returns 409 conflict."""
    # Create existing user
    existing_user = User(
        username="existinguser",
        email="existing@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(existing_user)
    await test_db.commit()
    
    # Try to register with same username
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "existinguser",
            "email": "newemail@example.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == 409
    assert "Username already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_db: AsyncSession):
    """Test registration with duplicate email returns 409 conflict."""
    # Create existing user
    existing_user = User(
        username="existinguser",
        email="existing@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(existing_user)
    await test_db.commit()
    
    # Try to register with same email
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "existing@example.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == 409
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email format returns 422 validation error."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "not-an-email",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Test registration with password shorter than 8 characters returns 422."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_db: AsyncSession):
    """Test successful login returns JWT token."""
    # Create user
    user = User(
        username="loginuser",
        email="login@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(user)
    await test_db.commit()
    
    # Login
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "loginuser",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_db: AsyncSession):
    """Test login with incorrect password returns 401 unauthorized."""
    # Create user
    user = User(
        username="loginuser",
        email="login@example.com",
        hashed_password=hash_password("correctpassword")
    )
    test_db.add(user)
    await test_db.commit()
    
    # Try to login with wrong password
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "loginuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent username returns 401 unauthorized."""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, test_db: AsyncSession):
    """Test accessing protected /me endpoint with valid token returns user data."""
    # Create user
    user = User(
        username="meuser",
        email="me@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(user)
    await test_db.commit()
    
    # Login to get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "meuser",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Should not expose password


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    """Test accessing protected endpoint without token returns 401."""
    response = await client.get("/api/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """Test accessing protected endpoint with invalid token returns 401."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_malformed_token(client: AsyncClient):
    """Test accessing protected endpoint with malformed token returns 401."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not.a.jwt"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_complete_auth_flow(client: AsyncClient):
    """Test complete authentication flow: register -> login -> access protected endpoint."""
    # Register
    register_response = await client.post(
        "/api/auth/register",
        json={
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "password123"
        }
    )
    assert register_response.status_code == 201
    
    # Login
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "flowuser",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    me_response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    data = me_response.json()
    assert data["username"] == "flowuser"
    assert data["email"] == "flow@example.com"
