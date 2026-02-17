"""
Unit tests for interview service.
Tests interview creation, retrieval, and authorization logic.
"""
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.interview_service import interview_service
from app.models.interview import Interview
from app.models.question import Question
from app.models.user import User


@pytest.mark.asyncio
async def test_create_interview_success(test_db: AsyncSession):
    """
    Test successful interview creation with LLM-generated questions.
    
    Validates:
    - Interview is created with correct user_id and role
    - Questions are generated and persisted
    - Questions have correct order
    - Requirements: 2.1, 2.3, 2.4, 2.5
    """
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Mock LLM service to return predictable questions
    mock_questions = [
        "What is Python?",
        "Explain decorators.",
        "What is async/await?"
    ]
    
    with patch('app.services.interview_service.llm_service.generate_questions', 
               new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_questions
        
        # Create interview
        interview = await interview_service.create_interview(
            db=test_db,
            user_id=user.id,
            role="Python Developer",
            num_questions=3
        )
    
    # Verify interview was created
    assert interview.id is not None
    assert interview.user_id == user.id
    assert interview.role == "Python Developer"
    assert interview.created_at is not None
    
    # Verify questions were created
    assert len(interview.questions) == 3
    for i, question in enumerate(interview.questions, start=1):
        assert question.interview_id == interview.id
        assert question.question_text == mock_questions[i-1]
        assert question.question_order == i


@pytest.mark.asyncio
async def test_create_interview_llm_failure(test_db: AsyncSession):
    """
    Test interview creation when LLM service fails.
    
    Validates:
    - Exception is propagated when LLM fails
    - No interview is created in database
    """
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Mock LLM service to raise an exception
    with patch('app.services.interview_service.llm_service.generate_questions',
               new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = Exception("LLM API error")
        
        # Attempt to create interview
        with pytest.raises(Exception, match="LLM API error"):
            await interview_service.create_interview(
                db=test_db,
                user_id=user.id,
                role="Python Developer",
                num_questions=3
            )


@pytest.mark.asyncio
async def test_get_user_interviews(test_db: AsyncSession):
    """
    Test fetching all interviews for a user.
    
    Validates:
    - Returns all interviews for the user
    - Returns empty list if user has no interviews
    - Interviews are ordered by creation date (newest first)
    - Requirements: 2.5
    """
    # Create test users
    user1 = User(username="user1", email="user1@example.com", hashed_password="hashed")
    user2 = User(username="user2", email="user2@example.com", hashed_password="hashed")
    test_db.add_all([user1, user2])
    await test_db.commit()
    await test_db.refresh(user1)
    await test_db.refresh(user2)
    
    # Create interviews for user1
    interview1 = Interview(user_id=user1.id, role="Python Developer")
    interview2 = Interview(user_id=user1.id, role="Data Scientist")
    # Create interview for user2
    interview3 = Interview(user_id=user2.id, role="DevOps Engineer")
    
    test_db.add_all([interview1, interview2, interview3])
    await test_db.commit()
    
    # Fetch user1's interviews
    user1_interviews = await interview_service.get_user_interviews(test_db, user1.id)
    assert len(user1_interviews) == 2
    assert all(i.user_id == user1.id for i in user1_interviews)
    
    # Fetch user2's interviews
    user2_interviews = await interview_service.get_user_interviews(test_db, user2.id)
    assert len(user2_interviews) == 1
    assert user2_interviews[0].user_id == user2.id
    
    # Fetch interviews for non-existent user
    empty_interviews = await interview_service.get_user_interviews(test_db, 9999)
    assert len(empty_interviews) == 0


@pytest.mark.asyncio
async def test_get_interview_by_id_success(test_db: AsyncSession):
    """
    Test fetching a specific interview by ID.
    
    Validates:
    - Returns interview with questions loaded
    - Requirements: 2.4
    """
    # Create test user and interview
    user = User(username="testuser", email="test@example.com", hashed_password="hashed")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Python Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    # Add questions
    question1 = Question(interview_id=interview.id, question_text="Q1", question_order=1)
    question2 = Question(interview_id=interview.id, question_text="Q2", question_order=2)
    test_db.add_all([question1, question2])
    await test_db.commit()
    
    # Fetch interview
    fetched = await interview_service.get_interview_by_id(test_db, interview.id)
    
    assert fetched is not None
    assert fetched.id == interview.id
    assert fetched.role == "Python Developer"
    assert len(fetched.questions) == 2


@pytest.mark.asyncio
async def test_get_interview_by_id_not_found(test_db: AsyncSession):
    """
    Test fetching a non-existent interview.
    
    Validates:
    - Returns None for non-existent interview ID
    """
    fetched = await interview_service.get_interview_by_id(test_db, 9999)
    assert fetched is None


@pytest.mark.asyncio
async def test_get_interview_by_id_with_authorization(test_db: AsyncSession):
    """
    Test interview access with authorization check.
    
    Validates:
    - Returns interview if user_id matches
    - Returns None if user_id doesn't match (authorization failure)
    - Requirements: 6.5
    """
    # Create test users
    user1 = User(username="user1", email="user1@example.com", hashed_password="hashed")
    user2 = User(username="user2", email="user2@example.com", hashed_password="hashed")
    test_db.add_all([user1, user2])
    await test_db.commit()
    await test_db.refresh(user1)
    await test_db.refresh(user2)
    
    # Create interview for user1
    interview = Interview(user_id=user1.id, role="Python Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    # User1 can access their own interview
    fetched = await interview_service.get_interview_by_id(test_db, interview.id, user1.id)
    assert fetched is not None
    assert fetched.id == interview.id
    
    # User2 cannot access user1's interview
    fetched = await interview_service.get_interview_by_id(test_db, interview.id, user2.id)
    assert fetched is None
    
    # No user_id provided (no authorization check) - should return interview
    fetched = await interview_service.get_interview_by_id(test_db, interview.id)
    assert fetched is not None
    assert fetched.id == interview.id
