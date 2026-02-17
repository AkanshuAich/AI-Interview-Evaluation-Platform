"""
Unit tests for answer service.
Tests answer submission, validation, and authorization logic.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.answer_service import answer_service
from app.models.user import User
from app.models.interview import Interview
from app.models.question import Question
from app.models.answer import Answer


@pytest.mark.asyncio
async def test_submit_answer_success(test_db: AsyncSession):
    """Test successful answer submission."""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    await test_db.flush()
    
    # Create test interview
    interview = Interview(
        user_id=user.id,
        role="Software Engineer"
    )
    test_db.add(interview)
    await test_db.flush()
    
    # Create test question
    question = Question(
        interview_id=interview.id,
        question_text="What is Python?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    
    # Submit answer
    answer = await answer_service.submit_answer(
        db=test_db,
        interview_id=interview.id,
        question_id=question.id,
        answer_text="Python is a high-level programming language.",
        user_id=user.id
    )
    
    # Verify answer was created
    assert answer.id is not None
    assert answer.question_id == question.id
    assert answer.user_id == user.id
    assert answer.answer_text == "Python is a high-level programming language."
    assert answer.submitted_at is not None


@pytest.mark.asyncio
async def test_submit_answer_interview_not_found(test_db: AsyncSession):
    """Test answer submission with non-existent interview."""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    
    # Try to submit answer to non-existent interview
    with pytest.raises(ValueError, match="Interview 999 does not exist"):
        await answer_service.submit_answer(
            db=test_db,
            interview_id=999,
            question_id=1,
            answer_text="Some answer",
            user_id=user.id
        )


@pytest.mark.asyncio
async def test_submit_answer_question_not_found(test_db: AsyncSession):
    """Test answer submission with non-existent question."""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    await test_db.flush()
    
    # Create test interview
    interview = Interview(
        user_id=user.id,
        role="Software Engineer"
    )
    test_db.add(interview)
    await test_db.commit()
    
    # Try to submit answer to non-existent question
    with pytest.raises(ValueError, match="Question 999 does not exist"):
        await answer_service.submit_answer(
            db=test_db,
            interview_id=interview.id,
            question_id=999,
            answer_text="Some answer",
            user_id=user.id
        )


@pytest.mark.asyncio
async def test_submit_answer_question_wrong_interview(test_db: AsyncSession):
    """Test answer submission with question from different interview."""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    await test_db.flush()
    
    # Create two interviews
    interview1 = Interview(
        user_id=user.id,
        role="Software Engineer"
    )
    interview2 = Interview(
        user_id=user.id,
        role="Data Scientist"
    )
    test_db.add_all([interview1, interview2])
    await test_db.flush()
    
    # Create question for interview2
    question = Question(
        interview_id=interview2.id,
        question_text="What is Python?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    
    # Try to submit answer to interview1 with question from interview2
    with pytest.raises(
        ValueError,
        match=f"Question {question.id} does not belong to interview {interview1.id}"
    ):
        await answer_service.submit_answer(
            db=test_db,
            interview_id=interview1.id,
            question_id=question.id,
            answer_text="Some answer",
            user_id=user.id
        )


@pytest.mark.asyncio
async def test_submit_answer_unauthorized_user(test_db: AsyncSession):
    """Test answer submission by unauthorized user."""
    # Create two users
    user1 = User(
        username="user1",
        email="user1@example.com",
        hashed_password="hashed_password"
    )
    user2 = User(
        username="user2",
        email="user2@example.com",
        hashed_password="hashed_password"
    )
    test_db.add_all([user1, user2])
    await test_db.flush()
    
    # Create interview for user1
    interview = Interview(
        user_id=user1.id,
        role="Software Engineer"
    )
    test_db.add(interview)
    await test_db.flush()
    
    # Create question
    question = Question(
        interview_id=interview.id,
        question_text="What is Python?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    
    # Try to submit answer as user2
    with pytest.raises(
        PermissionError,
        match=f"User does not have access to interview {interview.id}"
    ):
        await answer_service.submit_answer(
            db=test_db,
            interview_id=interview.id,
            question_id=question.id,
            answer_text="Some answer",
            user_id=user2.id
        )


@pytest.mark.asyncio
async def test_get_answer_with_evaluation_success(test_db: AsyncSession):
    """Test retrieving answer with evaluation."""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    await test_db.flush()
    
    # Create test interview
    interview = Interview(
        user_id=user.id,
        role="Software Engineer"
    )
    test_db.add(interview)
    await test_db.flush()
    
    # Create test question
    question = Question(
        interview_id=interview.id,
        question_text="What is Python?",
        question_order=1
    )
    test_db.add(question)
    await test_db.flush()
    
    # Create test answer
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="Python is a programming language."
    )
    test_db.add(answer)
    await test_db.commit()
    
    # Retrieve answer
    retrieved_answer = await answer_service.get_answer_with_evaluation(
        db=test_db,
        answer_id=answer.id,
        user_id=user.id
    )
    
    # Verify answer was retrieved
    assert retrieved_answer is not None
    assert retrieved_answer.id == answer.id
    assert retrieved_answer.answer_text == "Python is a programming language."


@pytest.mark.asyncio
async def test_get_answer_not_found(test_db: AsyncSession):
    """Test retrieving non-existent answer."""
    retrieved_answer = await answer_service.get_answer_with_evaluation(
        db=test_db,
        answer_id=999
    )
    
    assert retrieved_answer is None


@pytest.mark.asyncio
async def test_get_answer_unauthorized_user(test_db: AsyncSession):
    """Test retrieving answer by unauthorized user."""
    # Create two users
    user1 = User(
        username="user1",
        email="user1@example.com",
        hashed_password="hashed_password"
    )
    user2 = User(
        username="user2",
        email="user2@example.com",
        hashed_password="hashed_password"
    )
    test_db.add_all([user1, user2])
    await test_db.flush()
    
    # Create interview for user1
    interview = Interview(
        user_id=user1.id,
        role="Software Engineer"
    )
    test_db.add(interview)
    await test_db.flush()
    
    # Create question
    question = Question(
        interview_id=interview.id,
        question_text="What is Python?",
        question_order=1
    )
    test_db.add(question)
    await test_db.flush()
    
    # Create answer by user1
    answer = Answer(
        question_id=question.id,
        user_id=user1.id,
        answer_text="Python is a programming language."
    )
    test_db.add(answer)
    await test_db.commit()
    
    # Try to retrieve answer as user2
    retrieved_answer = await answer_service.get_answer_with_evaluation(
        db=test_db,
        answer_id=answer.id,
        user_id=user2.id
    )
    
    # Should return None due to authorization failure
    assert retrieved_answer is None
