"""
Integration tests for interview router endpoints.

Tests:
    - Interview creation with valid and invalid data
    - Interview listing returns only user's interviews
    - Interview access authorization
    - Error handling for LLM failures and invalid inputs

Requirements:
    - 2.1: Generate relevant technical questions for specified roles
    - 2.3: Persist interview with generated questions to database
    - 2.4: Return interview ID and questions to client
    - 2.5: Associate interview with authenticated user
    - 6.5: Authorization check for interview access
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.models.user import User
from app.services.auth_service import hash_password


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user for authentication."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def auth_token(client: AsyncClient, test_user: User) -> str:
    """Get authentication token for test user."""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_interview_success(client: AsyncClient, auth_token: str):
    """Test successful interview creation with LLM-generated questions."""
    # Mock LLM service to avoid actual API calls
    mock_questions = [
        "What is Python?",
        "Explain decorators in Python.",
        "What is the difference between list and tuple?"
    ]
    
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_questions
        
        response = await client.post(
            "/api/interviews",
            json={
                "role": "Python Developer",
                "num_questions": 3
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "id" in data
    assert data["role"] == "Python Developer"
    assert "created_at" in data
    assert "questions" in data
    assert len(data["questions"]) == 3
    
    # Verify questions structure
    for i, question in enumerate(data["questions"], start=1):
        assert "id" in question
        assert "question_text" in question
        assert "question_order" in question
        assert question["question_order"] == i
        assert question["question_text"] == mock_questions[i-1]


@pytest.mark.asyncio
async def test_create_interview_no_auth(client: AsyncClient):
    """Test interview creation without authentication returns 401."""
    response = await client.post(
        "/api/interviews",
        json={
            "role": "Python Developer",
            "num_questions": 3
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_interview_invalid_token(client: AsyncClient):
    """Test interview creation with invalid token returns 401."""
    response = await client.post(
        "/api/interviews",
        json={
            "role": "Python Developer",
            "num_questions": 3
        },
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_interview_invalid_num_questions(client: AsyncClient, auth_token: str):
    """Test interview creation with invalid number of questions returns 422."""
    # Test with 0 questions
    response = await client.post(
        "/api/interviews",
        json={
            "role": "Python Developer",
            "num_questions": 0
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422
    
    # Test with more than 10 questions
    response = await client.post(
        "/api/interviews",
        json={
            "role": "Python Developer",
            "num_questions": 11
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_interview_empty_role(client: AsyncClient, auth_token: str):
    """Test interview creation with empty role returns 422."""
    response = await client.post(
        "/api/interviews",
        json={
            "role": "",
            "num_questions": 3
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_interview_llm_failure(client: AsyncClient, auth_token: str):
    """Test interview creation handles LLM service failures gracefully."""
    # Mock LLM service to raise an exception
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM API error")
        
        response = await client.post(
            "/api/interviews",
            json={
                "role": "Python Developer",
                "num_questions": 3
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 500
    assert "Failed to create interview" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_interviews_empty(client: AsyncClient, auth_token: str):
    """Test listing interviews when user has no interviews returns empty list."""
    response = await client.get(
        "/api/interviews",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_interviews_with_data(client: AsyncClient, auth_token: str):
    """Test listing interviews returns user's interviews."""
    mock_questions = ["Question 1", "Question 2"]
    
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_questions
        
        # Create two interviews
        await client.post(
            "/api/interviews",
            json={"role": "Python Developer", "num_questions": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        await client.post(
            "/api/interviews",
            json={"role": "JavaScript Developer", "num_questions": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    # List interviews
    response = await client.get(
        "/api/interviews",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify interviews are ordered by created_at descending (newest first)
    assert data[0]["role"] == "JavaScript Developer"
    assert data[1]["role"] == "Python Developer"
    
    # Verify each interview has questions
    for interview in data:
        assert "id" in interview
        assert "role" in interview
        assert "created_at" in interview
        assert "questions" in interview
        assert len(interview["questions"]) == 2


@pytest.mark.asyncio
async def test_list_interviews_no_auth(client: AsyncClient):
    """Test listing interviews without authentication returns 401."""
    response = await client.get("/api/interviews")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_interviews_only_user_interviews(client: AsyncClient, test_db: AsyncSession):
    """Test listing interviews returns only the authenticated user's interviews."""
    # Create two users
    user1 = User(
        username="user1",
        email="user1@example.com",
        hashed_password=hash_password("password123")
    )
    user2 = User(
        username="user2",
        email="user2@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(user1)
    test_db.add(user2)
    await test_db.commit()
    
    # Get tokens for both users
    response1 = await client.post(
        "/api/auth/login",
        json={"username": "user1", "password": "password123"}
    )
    token1 = response1.json()["access_token"]
    
    response2 = await client.post(
        "/api/auth/login",
        json={"username": "user2", "password": "password123"}
    )
    token2 = response2.json()["access_token"]
    
    mock_questions = ["Question 1"]
    
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_questions
        
        # User 1 creates 2 interviews
        await client.post(
            "/api/interviews",
            json={"role": "Python Developer", "num_questions": 1},
            headers={"Authorization": f"Bearer {token1}"}
        )
        await client.post(
            "/api/interviews",
            json={"role": "Java Developer", "num_questions": 1},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # User 2 creates 1 interview
        await client.post(
            "/api/interviews",
            json={"role": "Go Developer", "num_questions": 1},
            headers={"Authorization": f"Bearer {token2}"}
        )
    
    # User 1 lists interviews - should see only their 2 interviews
    response1 = await client.get(
        "/api/interviews",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1) == 2
    assert all(interview["role"] in ["Python Developer", "Java Developer"] for interview in data1)
    
    # User 2 lists interviews - should see only their 1 interview
    response2 = await client.get(
        "/api/interviews",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 1
    assert data2[0]["role"] == "Go Developer"


@pytest.mark.asyncio
async def test_get_interview_success(client: AsyncClient, auth_token: str):
    """Test getting a specific interview by ID."""
    mock_questions = ["Question 1", "Question 2", "Question 3"]
    
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_questions
        
        # Create interview
        create_response = await client.post(
            "/api/interviews",
            json={"role": "Python Developer", "num_questions": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        interview_id = create_response.json()["id"]
    
    # Get interview
    response = await client.get(
        f"/api/interviews/{interview_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == interview_id
    assert data["role"] == "Python Developer"
    assert len(data["questions"]) == 3


@pytest.mark.asyncio
async def test_get_interview_not_found(client: AsyncClient, auth_token: str):
    """Test getting a non-existent interview returns 404."""
    response = await client.get(
        "/api/interviews/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "Interview not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_interview_no_auth(client: AsyncClient):
    """Test getting an interview without authentication returns 401."""
    response = await client.get("/api/interviews/1")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_interview_unauthorized_access(client: AsyncClient, test_db: AsyncSession):
    """Test getting another user's interview returns 403 forbidden."""
    # Create two users
    user1 = User(
        username="owner",
        email="owner@example.com",
        hashed_password=hash_password("password123")
    )
    user2 = User(
        username="other",
        email="other@example.com",
        hashed_password=hash_password("password123")
    )
    test_db.add(user1)
    test_db.add(user2)
    await test_db.commit()
    
    # Get tokens
    response1 = await client.post(
        "/api/auth/login",
        json={"username": "owner", "password": "password123"}
    )
    token1 = response1.json()["access_token"]
    
    response2 = await client.post(
        "/api/auth/login",
        json={"username": "other", "password": "password123"}
    )
    token2 = response2.json()["access_token"]
    
    mock_questions = ["Question 1"]
    
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_questions
        
        # User 1 creates interview
        create_response = await client.post(
            "/api/interviews",
            json={"role": "Python Developer", "num_questions": 1},
            headers={"Authorization": f"Bearer {token1}"}
        )
        interview_id = create_response.json()["id"]
    
    # User 2 tries to access user 1's interview
    response = await client.get(
        f"/api/interviews/{interview_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    assert response.status_code == 403
    assert "don't have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_complete_interview_flow(client: AsyncClient, auth_token: str):
    """Test complete interview flow: create -> list -> get specific."""
    mock_questions = ["Question 1", "Question 2"]
    
    with patch("app.services.interview_service.llm_service.generate_questions", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_questions
        
        # Create interview
        create_response = await client.post(
            "/api/interviews",
            json={"role": "Python Developer", "num_questions": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 201
        interview_id = create_response.json()["id"]
        
        # List interviews
        list_response = await client.get(
            "/api/interviews",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # Get specific interview
        get_response = await client.get(
            f"/api/interviews/{interview_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["id"] == interview_id
