"""
Integration tests for answer router endpoints.

Tests:
    - Answer submission with valid data
    - Answer submission with invalid question
    - Answer submission without authorization
    - Evaluation status checking
    - Background evaluation triggering
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.models.user import User
from app.models.interview import Interview
from app.models.question import Question
from app.models.answer import Answer
from app.models.evaluation import Evaluation


@pytest.mark.asyncio
async def test_submit_answer_success(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test successful answer submission."""
    # Create interview and question
    interview = Interview(
        user_id=test_user.id,
        role="Backend Developer"
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is REST?",
        order=1
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    
    # Submit answer
    answer_data = {
        "question_id": question.id,
        "answer_text": "REST is an architectural style for web services."
    }
    
    response = await client.post(
        "/api/answers",
        json=answer_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["question_id"] == question.id
    assert data["answer_text"] == answer_data["answer_text"]
    assert "id" in data
    assert "submitted_at" in data


@pytest.mark.asyncio
async def test_submit_answer_question_not_found(
    client: AsyncClient,
    auth_headers: dict
):
    """Test answer submission with non-existent question."""
    answer_data = {
        "question_id": 99999,
        "answer_text": "Some answer"
    }
    
    response = await client.post(
        "/api/answers",
        json=answer_data,
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_submit_answer_unauthorized(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test answer submission for interview user doesn't own."""
    # Create another user and their interview
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="hashed"
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    
    interview = Interview(
        user_id=other_user.id,
        role="Frontend Developer"
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is React?",
        order=1
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    
    # Try to submit answer as test_user
    answer_data = {
        "question_id": question.id,
        "answer_text": "React is a library"
    }
    
    response = await client.post(
        "/api/answers",
        json=answer_data,
        headers=auth_headers
    )
    
    assert response.status_code == 403
    assert "access" in response.json()["detail"].lower() or "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_submit_answer_without_auth(client: AsyncClient):
    """Test answer submission without authentication."""
    answer_data = {
        "question_id": 1,
        "answer_text": "Some answer"
    }
    
    response = await client.post(
        "/api/answers",
        json=answer_data
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_answer_status_pending(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test checking status of answer with pending evaluation."""
    # Create interview, question, and answer
    interview = Interview(
        user_id=test_user.id,
        role="Backend Developer"
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is REST?",
        order=1
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=test_user.id,
        answer_text="REST is an architectural style."
    )
    db_session.add(answer)
    await db_session.commit()
    await db_session.refresh(answer)
    
    # Check status
    response = await client.get(
        f"/api/answers/{answer.id}/status",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_status"] == "pending"
    assert data["evaluation"] is None
    assert data["answer"]["id"] == answer.id


@pytest.mark.asyncio
async def test_get_answer_status_completed(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test checking status of answer with completed evaluation."""
    # Create interview, question, answer, and evaluation
    interview = Interview(
        user_id=test_user.id,
        role="Backend Developer"
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is REST?",
        order=1
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=test_user.id,
        answer_text="REST is an architectural style."
    )
    db_session.add(answer)
    await db_session.commit()
    await db_session.refresh(answer)
    
    evaluation = Evaluation(
        answer_id=answer.id,
        status="completed",
        technical_accuracy=8,
        completeness=7,
        clarity=9,
        feedback="Good explanation",
        suggestions=["Add more examples"]
    )
    db_session.add(evaluation)
    await db_session.commit()
    
    # Check status
    response = await client.get(
        f"/api/answers/{answer.id}/status",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_status"] == "completed"
    assert data["evaluation"] is not None
    assert data["evaluation"]["technical_accuracy"] == 8
    assert data["evaluation"]["completeness"] == 7
    assert data["evaluation"]["clarity"] == 9


@pytest.mark.asyncio
async def test_get_answer_status_not_found(
    client: AsyncClient,
    auth_headers: dict
):
    """Test checking status of non-existent answer."""
    response = await client.get(
        "/api/answers/99999/status",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_answer_status_unauthorized(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test checking status of answer user doesn't own."""
    # Create another user and their answer
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="hashed"
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    
    interview = Interview(
        user_id=other_user.id,
        role="Frontend Developer"
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is React?",
        order=1
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=other_user.id,
        answer_text="React is a library"
    )
    db_session.add(answer)
    await db_session.commit()
    await db_session.refresh(answer)
    
    # Try to check status as test_user
    response = await client.get(
        f"/api/answers/{answer.id}/status",
        headers=auth_headers
    )
    
    assert response.status_code == 403
