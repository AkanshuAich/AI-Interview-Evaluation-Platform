"""
Unit tests for Interview, Question, Answer, and Evaluation models.
Tests model creation, relationships, and cascading deletes.
"""
import pytest
from sqlalchemy import select
from app.models import User, Interview, Question, Answer, Evaluation


@pytest.mark.asyncio
async def test_interview_creation(test_db):
    """Test creating an interview with user relationship."""
    # Create user first
    user = User(username="interviewer", email="interviewer@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create interview
    interview = Interview(user_id=user.id, role="Software Engineer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    assert interview.id is not None
    assert interview.user_id == user.id
    assert interview.role == "Software Engineer"
    assert interview.created_at is not None


@pytest.mark.asyncio
async def test_question_creation_with_ordering(test_db):
    """Test creating questions with proper ordering."""
    # Create user and interview
    user = User(username="user1", email="user1@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Backend Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    # Create questions
    q1 = Question(interview_id=interview.id, question_text="What is Python?", question_order=1)
    q2 = Question(interview_id=interview.id, question_text="Explain async/await", question_order=2)
    test_db.add_all([q1, q2])
    await test_db.commit()
    
    # Query questions
    result = await test_db.execute(
        select(Question).where(Question.interview_id == interview.id).order_by(Question.question_order)
    )
    questions = result.scalars().all()
    
    assert len(questions) == 2
    assert questions[0].question_order == 1
    assert questions[1].question_order == 2
    assert questions[0].question_text == "What is Python?"


@pytest.mark.asyncio
async def test_answer_creation_with_relationships(test_db):
    """Test creating an answer with question and user relationships."""
    # Create user, interview, and question
    user = User(username="candidate", email="candidate@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Data Scientist")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(interview_id=interview.id, question_text="What is ML?", question_order=1)
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    # Create answer
    answer = Answer(
        question_id=question.id,
        user_id=user.id,
        answer_text="Machine Learning is a subset of AI..."
    )
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    assert answer.id is not None
    assert answer.question_id == question.id
    assert answer.user_id == user.id
    assert answer.answer_text == "Machine Learning is a subset of AI..."
    assert answer.submitted_at is not None


@pytest.mark.asyncio
async def test_evaluation_creation_with_json_fields(test_db):
    """Test creating an evaluation with JSON scores and suggestions."""
    # Create full chain: user -> interview -> question -> answer
    user = User(username="eval_user", email="eval@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Frontend Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(interview_id=interview.id, question_text="What is React?", question_order=1)
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(question_id=question.id, user_id=user.id, answer_text="React is a library...")
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Create evaluation
    evaluation = Evaluation(
        answer_id=answer.id,
        scores={"correctness": 8.5, "completeness": 7.0, "quality": 9.0, "communication": 8.0},
        feedback="Good understanding of React fundamentals.",
        suggestions=["Add more details about hooks", "Mention virtual DOM"],
        status="completed"
    )
    test_db.add(evaluation)
    await test_db.commit()
    await test_db.refresh(evaluation)
    
    assert evaluation.id is not None
    assert evaluation.answer_id == answer.id
    assert evaluation.scores["correctness"] == 8.5
    assert evaluation.scores["completeness"] == 7.0
    assert len(evaluation.suggestions) == 2
    assert evaluation.feedback == "Good understanding of React fundamentals."
    assert evaluation.status == "completed"


@pytest.mark.asyncio
async def test_cascading_delete_interview(test_db):
    """Test that deleting an interview cascades to questions and answers."""
    # Create full chain
    user = User(username="cascade_user", email="cascade@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="DevOps Engineer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(interview_id=interview.id, question_text="What is Docker?", question_order=1)
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(question_id=question.id, user_id=user.id, answer_text="Docker is...")
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    interview_id = interview.id
    question_id = question.id
    answer_id = answer.id
    
    # Delete interview
    await test_db.delete(interview)
    await test_db.commit()
    
    # Verify cascade delete
    result = await test_db.execute(select(Question).where(Question.id == question_id))
    assert result.scalar_one_or_none() is None
    
    result = await test_db.execute(select(Answer).where(Answer.id == answer_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_cascading_delete_user(test_db):
    """Test that deleting a user cascades to interviews and answers."""
    # Create user with interview
    user = User(username="delete_user", email="delete@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="QA Engineer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    user_id = user.id
    interview_id = interview.id
    
    # Delete user
    await test_db.delete(user)
    await test_db.commit()
    
    # Verify cascade delete
    result = await test_db.execute(select(Interview).where(Interview.id == interview_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_evaluation_unique_constraint(test_db):
    """Test that answer_id is unique in evaluations (one-to-one relationship)."""
    # Create full chain
    user = User(username="unique_user", email="unique@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Security Engineer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(interview_id=interview.id, question_text="What is XSS?", question_order=1)
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(question_id=question.id, user_id=user.id, answer_text="XSS is...")
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    # Create first evaluation
    eval1 = Evaluation(
        answer_id=answer.id,
        scores={"correctness": 7.0, "completeness": 6.0, "quality": 7.5, "communication": 8.0},
        feedback="Good answer",
        suggestions=["Add examples"],
        status="completed"
    )
    test_db.add(eval1)
    await test_db.commit()
    
    # Try to create second evaluation for same answer
    eval2 = Evaluation(
        answer_id=answer.id,  # Same answer_id
        scores={"correctness": 8.0, "completeness": 7.0, "quality": 8.5, "communication": 9.0},
        feedback="Different feedback",
        suggestions=["Different suggestion"],
        status="completed"
    )
    test_db.add(eval2)
    
    with pytest.raises(Exception):  # Should raise IntegrityError due to unique constraint
        await test_db.commit()


@pytest.mark.asyncio
async def test_interview_questions_relationship(test_db):
    """Test the relationship between interview and questions."""
    # Create user and interview
    user = User(username="rel_user", email="rel@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Full Stack Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    # Create multiple questions
    for i in range(3):
        question = Question(
            interview_id=interview.id,
            question_text=f"Question {i+1}",
            question_order=i+1
        )
        test_db.add(question)
    await test_db.commit()
    
    # Refresh and check relationship
    await test_db.refresh(interview)
    result = await test_db.execute(
        select(Interview).where(Interview.id == interview.id)
    )
    loaded_interview = result.scalar_one()
    
    # Load questions relationship
    result = await test_db.execute(
        select(Question).where(Question.interview_id == loaded_interview.id).order_by(Question.question_order)
    )
    questions = result.scalars().all()
    
    assert len(questions) == 3
    assert questions[0].question_order == 1
    assert questions[2].question_order == 3


@pytest.mark.asyncio
async def test_answer_evaluation_one_to_one(test_db):
    """Test the one-to-one relationship between answer and evaluation."""
    # Create full chain
    user = User(username="one_to_one", email="onetoone@example.com", hashed_password="hash")
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    interview = Interview(user_id=user.id, role="Mobile Developer")
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    
    question = Question(interview_id=interview.id, question_text="What is Flutter?", question_order=1)
    test_db.add(question)
    await test_db.commit()
    await test_db.refresh(question)
    
    answer = Answer(question_id=question.id, user_id=user.id, answer_text="Flutter is...")
    test_db.add(answer)
    await test_db.commit()
    await test_db.refresh(answer)
    
    evaluation = Evaluation(
        answer_id=answer.id,
        scores={"correctness": 9.0, "completeness": 8.5, "quality": 9.5, "communication": 9.0},
        feedback="Excellent answer",
        suggestions=["Perfect!"],
        status="completed"
    )
    test_db.add(evaluation)
    await test_db.commit()
    
    # Query answer with evaluation
    result = await test_db.execute(
        select(Answer).where(Answer.id == answer.id)
    )
    loaded_answer = result.scalar_one()
    
    # Query evaluation
    result = await test_db.execute(
        select(Evaluation).where(Evaluation.answer_id == loaded_answer.id)
    )
    loaded_evaluation = result.scalar_one()
    
    assert loaded_evaluation.answer_id == loaded_answer.id
    assert loaded_evaluation.status == "completed"
