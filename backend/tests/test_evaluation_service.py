"""
Unit tests for the evaluation service.

Tests cover:
- Background evaluation processing
- Evaluation result persistence
- Error handling and failed status
- Evaluation status retrieval
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.evaluation_service import evaluation_service
from app.services.llm_service import EvaluationResult, EvaluationScores
from app.models.answer import Answer
from app.models.question import Question
from app.models.interview import Interview
from app.models.evaluation import Evaluation
from app.models.user import User


@pytest.mark.asyncio
async def test_evaluate_answer_async_success(test_db: AsyncSession):
    """Test successful background evaluation of an answer."""
    # Create test data
    user = User(username="testuser", email="test@example.com", hashed_password="hashed")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Software Engineer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is polymorphism?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="Polymorphism is the ability of objects to take multiple forms."
    )
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Mock LLM service response
    mock_evaluation = EvaluationResult(
        scores=EvaluationScores(
            correctness=8.0,
            completeness=7.5,
            quality=8.5,
            communication=9.0
        ),
        feedback="Good explanation of polymorphism with clear examples.",
        suggestions=[
            "Add more specific examples",
            "Discuss different types of polymorphism",
            "Mention practical use cases"
        ]
    )
    
    with patch('app.services.evaluation_service.llm_service.evaluate_answer', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_evaluation
        
        # Execute evaluation
        await evaluation_service.evaluate_answer_async(test_db, answer.id)
    
    # Verify evaluation was created
    from sqlalchemy import select
    stmt = select(Evaluation).where(Evaluation.answer_id == answer.id)
    result = await test_db.execute(stmt)
    evaluation = result.scalar_one_or_none()
    
    assert evaluation is not None
    assert evaluation.status == "completed"
    assert evaluation.scores["correctness"] == 8.0
    assert evaluation.scores["completeness"] == 7.5
    assert evaluation.scores["quality"] == 8.5
    assert evaluation.scores["communication"] == 9.0
    assert "Good explanation" in evaluation.feedback
    assert len(evaluation.suggestions) == 3
    assert "Add more specific examples" in evaluation.suggestions


@pytest.mark.asyncio
async def test_evaluate_answer_async_llm_failure(test_db: AsyncSession):
    """Test evaluation handles LLM service failures gracefully."""
    # Create test data
    user = User(username="testuser2", email="test2@example.com", hashed_password="hashed")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Data Scientist")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="Explain gradient descent.",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="Gradient descent is an optimization algorithm."
    )
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Mock LLM service to raise an exception
    with patch('app.services.evaluation_service.llm_service.evaluate_answer', new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM API timeout")
        
        # Execute evaluation (should not raise exception)
        await evaluation_service.evaluate_answer_async(test_db, answer.id)
    
    # Verify failed evaluation was created
    from sqlalchemy import select
    stmt = select(Evaluation).where(Evaluation.answer_id == answer.id)
    result = await test_db.execute(stmt)
    evaluation = result.scalar_one_or_none()
    
    assert evaluation is not None
    assert evaluation.status == "failed"
    assert "Evaluation failed" in evaluation.feedback
    assert "LLM API timeout" in evaluation.feedback
    assert len(evaluation.suggestions) > 0


@pytest.mark.asyncio
async def test_evaluate_answer_async_answer_not_found(test_db: AsyncSession):
    """Test evaluation handles missing answer gracefully."""
    # Try to evaluate non-existent answer
    await evaluation_service.evaluate_answer_async(test_db, 99999)
    
    # Should not raise exception, just log error
    # Verify no evaluation was created
    from sqlalchemy import select
    stmt = select(Evaluation).where(Evaluation.answer_id == 99999)
    result = await test_db.execute(stmt)
    evaluation = result.scalar_one_or_none()
    
    assert evaluation is None


@pytest.mark.asyncio
async def test_get_evaluation_status_pending(test_db: AsyncSession):
    """Test getting evaluation status when no evaluation exists (pending)."""
    # Create test data without evaluation
    user = User(username="testuser3", email="test3@example.com", hashed_password="hashed")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="DevOps Engineer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is CI/CD?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="CI/CD stands for Continuous Integration and Continuous Deployment."
    )
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Get evaluation status
    status = await evaluation_service.get_evaluation_status(test_db, answer.id)
    
    assert status is not None
    assert status["status"] == "pending"
    assert status["evaluation"] is None


@pytest.mark.asyncio
async def test_get_evaluation_status_completed(test_db: AsyncSession):
    """Test getting evaluation status when evaluation is completed."""
    # Create test data with completed evaluation
    user = User(username="testuser4", email="test4@example.com", hashed_password="hashed")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Frontend Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is React?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="React is a JavaScript library for building user interfaces."
    )
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Create completed evaluation
    evaluation = Evaluation(
        answer_id=answer.id,
        scores={
            "correctness": 9.0,
            "completeness": 8.0,
            "quality": 8.5,
            "communication": 9.5
        },
        feedback="Excellent concise explanation.",
        suggestions=["Add examples", "Discuss virtual DOM"],
        status="completed"
    )
    test_db.add(evaluation)
    await test_db.commit()
    
    # Get evaluation status
    status = await evaluation_service.get_evaluation_status(test_db, answer.id)
    
    assert status is not None
    assert status["status"] == "completed"
    assert status["evaluation"] is not None
    assert status["evaluation"]["scores"]["correctness"] == 9.0
    assert "Excellent" in status["evaluation"]["feedback"]
    assert len(status["evaluation"]["suggestions"]) == 2


@pytest.mark.asyncio
async def test_get_evaluation_status_failed(test_db: AsyncSession):
    """Test getting evaluation status when evaluation failed."""
    # Create test data with failed evaluation
    user = User(username="testuser5", email="test5@example.com", hashed_password="hashed")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Backend Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(
        interview_id=interview.id,
        question_text="What is REST?",
        question_order=1
    )
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="REST is an architectural style."
    )
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Create failed evaluation
    evaluation = Evaluation(
        answer_id=answer.id,
        scores={
            "correctness": 0.0,
            "completeness": 0.0,
            "quality": 0.0,
            "communication": 0.0
        },
        feedback="Evaluation failed: API timeout",
        suggestions=["Please retry"],
        status="failed"
    )
    test_db.add(evaluation)
    await test_db.commit()
    
    # Get evaluation status
    status = await evaluation_service.get_evaluation_status(test_db, answer.id)
    
    assert status is not None
    assert status["status"] == "failed"
    assert status["evaluation"] is None  # Failed evaluations don't return data

