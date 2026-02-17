"""
Unit tests for Pydantic schemas.
Tests validation rules, field constraints, and schema instantiation.

Feature: ai-interview-platform
Task: 2.3 Create Pydantic schemas for request/response validation
Requirements: 7.5
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    InterviewCreate, QuestionResponse, InterviewResponse,
    AnswerSubmit, EvaluationScores, EvaluationResponse, AnswerResponse,
    QuestionWithAnswer, InterviewReport
)


class TestAuthSchemas:
    """Test authentication schemas."""
    
    def test_user_register_valid(self):
        """Test UserRegister with valid data."""
        user = UserRegister(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
    
    def test_user_register_invalid_email(self):
        """Test UserRegister rejects invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                username="testuser",
                email="invalid-email",
                password="password123"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_user_register_short_password(self):
        """Test UserRegister rejects password shorter than 8 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="short"
            )
        assert "password" in str(exc_info.value).lower()
    
    def test_user_register_short_username(self):
        """Test UserRegister rejects username shorter than 3 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                username="ab",
                email="test@example.com",
                password="password123"
            )
        assert "username" in str(exc_info.value).lower()
    
    def test_user_login_valid(self):
        """Test UserLogin with valid data."""
        login = UserLogin(username="testuser", password="password123")
        assert login.username == "testuser"
        assert login.password == "password123"
    
    def test_token_valid(self):
        """Test Token schema."""
        token = Token(access_token="abc123xyz", token_type="bearer")
        assert token.access_token == "abc123xyz"
        assert token.token_type == "bearer"
    
    def test_token_default_type(self):
        """Test Token uses default token_type."""
        token = Token(access_token="abc123xyz")
        assert token.token_type == "bearer"
    
    def test_user_response_valid(self):
        """Test UserResponse schema."""
        user = UserResponse(id=1, username="testuser", email="test@example.com")
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"


class TestInterviewSchemas:
    """Test interview schemas."""
    
    def test_interview_create_valid(self):
        """Test InterviewCreate with valid data."""
        interview = InterviewCreate(role="Python Developer", num_questions=5)
        assert interview.role == "Python Developer"
        assert interview.num_questions == 5
    
    def test_interview_create_min_questions(self):
        """Test InterviewCreate rejects num_questions < 1."""
        with pytest.raises(ValidationError) as exc_info:
            InterviewCreate(role="Developer", num_questions=0)
        assert "num_questions" in str(exc_info.value).lower()
    
    def test_interview_create_max_questions(self):
        """Test InterviewCreate rejects num_questions > 10."""
        with pytest.raises(ValidationError) as exc_info:
            InterviewCreate(role="Developer", num_questions=11)
        assert "num_questions" in str(exc_info.value).lower()
    
    def test_interview_create_empty_role(self):
        """Test InterviewCreate rejects empty role."""
        with pytest.raises(ValidationError) as exc_info:
            InterviewCreate(role="", num_questions=5)
        assert "role" in str(exc_info.value).lower()
    
    def test_question_response_valid(self):
        """Test QuestionResponse schema."""
        question = QuestionResponse(
            id=1,
            question_text="What is Python?",
            question_order=1
        )
        assert question.id == 1
        assert question.question_text == "What is Python?"
        assert question.question_order == 1
    
    def test_interview_response_valid(self):
        """Test InterviewResponse with questions."""
        question = QuestionResponse(
            id=1,
            question_text="What is Python?",
            question_order=1
        )
        interview = InterviewResponse(
            id=1,
            role="Python Developer",
            created_at=datetime.now(),
            questions=[question]
        )
        assert interview.id == 1
        assert interview.role == "Python Developer"
        assert len(interview.questions) == 1
        assert interview.questions[0].id == 1
    
    def test_interview_response_empty_questions(self):
        """Test InterviewResponse with no questions."""
        interview = InterviewResponse(
            id=1,
            role="Python Developer",
            created_at=datetime.now(),
            questions=[]
        )
        assert len(interview.questions) == 0


class TestAnswerSchemas:
    """Test answer and evaluation schemas."""
    
    def test_answer_submit_valid(self):
        """Test AnswerSubmit with valid data."""
        answer = AnswerSubmit(
            interview_id=1,
            question_id=1,
            answer_text="Python is a high-level programming language."
        )
        assert answer.interview_id == 1
        assert answer.question_id == 1
        assert len(answer.answer_text) >= 10
    
    def test_answer_submit_short_text(self):
        """Test AnswerSubmit rejects answer_text shorter than 10 characters."""
        with pytest.raises(ValidationError) as exc_info:
            AnswerSubmit(
                interview_id=1,
                question_id=1,
                answer_text="short"
            )
        assert "answer_text" in str(exc_info.value).lower()
    
    def test_answer_submit_invalid_ids(self):
        """Test AnswerSubmit rejects non-positive IDs."""
        with pytest.raises(ValidationError):
            AnswerSubmit(
                interview_id=0,
                question_id=1,
                answer_text="Valid answer text here."
            )
        
        with pytest.raises(ValidationError):
            AnswerSubmit(
                interview_id=1,
                question_id=-1,
                answer_text="Valid answer text here."
            )
    
    def test_evaluation_scores_valid(self):
        """Test EvaluationScores with valid data."""
        scores = EvaluationScores(
            correctness=8.5,
            completeness=7.0,
            quality=9.0,
            communication=8.0
        )
        assert scores.correctness == 8.5
        assert scores.completeness == 7.0
        assert scores.quality == 9.0
        assert scores.communication == 8.0
    
    def test_evaluation_scores_min_validation(self):
        """Test EvaluationScores rejects scores < 0."""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationScores(
                correctness=-1.0,
                completeness=7.0,
                quality=9.0,
                communication=8.0
            )
        assert "correctness" in str(exc_info.value).lower()
    
    def test_evaluation_scores_max_validation(self):
        """Test EvaluationScores rejects scores > 10."""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationScores(
                correctness=11.0,
                completeness=7.0,
                quality=9.0,
                communication=8.0
            )
        assert "correctness" in str(exc_info.value).lower()
    
    def test_evaluation_scores_boundary_values(self):
        """Test EvaluationScores accepts boundary values 0 and 10."""
        scores_min = EvaluationScores(
            correctness=0.0,
            completeness=0.0,
            quality=0.0,
            communication=0.0
        )
        assert scores_min.correctness == 0.0
        
        scores_max = EvaluationScores(
            correctness=10.0,
            completeness=10.0,
            quality=10.0,
            communication=10.0
        )
        assert scores_max.correctness == 10.0
    
    def test_evaluation_response_valid(self):
        """Test EvaluationResponse with valid data."""
        scores = EvaluationScores(
            correctness=8.5,
            completeness=7.0,
            quality=9.0,
            communication=8.0
        )
        evaluation = EvaluationResponse(
            scores=scores,
            feedback="Good answer with clear explanation.",
            suggestions=["Add more examples", "Consider edge cases"],
            evaluated_at=datetime.now(),
            status="completed"
        )
        assert evaluation.scores.correctness == 8.5
        assert evaluation.feedback == "Good answer with clear explanation."
        assert len(evaluation.suggestions) == 2
        assert evaluation.status == "completed"
    
    def test_evaluation_response_empty_suggestions(self):
        """Test EvaluationResponse with empty suggestions list."""
        scores = EvaluationScores(
            correctness=8.5,
            completeness=7.0,
            quality=9.0,
            communication=8.0
        )
        evaluation = EvaluationResponse(
            scores=scores,
            feedback="Good answer.",
            suggestions=[],
            evaluated_at=datetime.now(),
            status="completed"
        )
        assert len(evaluation.suggestions) == 0
    
    def test_answer_response_with_evaluation(self):
        """Test AnswerResponse with evaluation."""
        scores = EvaluationScores(
            correctness=8.5,
            completeness=7.0,
            quality=9.0,
            communication=8.0
        )
        evaluation = EvaluationResponse(
            scores=scores,
            feedback="Good answer.",
            suggestions=["Add more details"],
            evaluated_at=datetime.now(),
            status="completed"
        )
        answer = AnswerResponse(
            id=1,
            answer_text="Python is a high-level programming language.",
            submitted_at=datetime.now(),
            evaluation=evaluation
        )
        assert answer.id == 1
        assert answer.evaluation is not None
        assert answer.evaluation.status == "completed"
    
    def test_answer_response_without_evaluation(self):
        """Test AnswerResponse without evaluation (pending)."""
        answer = AnswerResponse(
            id=1,
            answer_text="Python is a high-level programming language.",
            submitted_at=datetime.now(),
            evaluation=None
        )
        assert answer.id == 1
        assert answer.evaluation is None


class TestReportSchemas:
    """Test report schemas."""
    
    def test_question_with_answer_valid(self):
        """Test QuestionWithAnswer with answer and evaluation."""
        scores = EvaluationScores(
            correctness=8.5,
            completeness=7.0,
            quality=9.0,
            communication=8.0
        )
        evaluation = EvaluationResponse(
            scores=scores,
            feedback="Good answer.",
            suggestions=["Add more details"],
            evaluated_at=datetime.now(),
            status="completed"
        )
        answer = AnswerResponse(
            id=1,
            answer_text="Python is a high-level programming language.",
            submitted_at=datetime.now(),
            evaluation=evaluation
        )
        question = QuestionWithAnswer(
            question_id=1,
            question_text="What is Python?",
            question_order=1,
            answer=answer
        )
        assert question.question_id == 1
        assert question.answer is not None
        assert question.answer.evaluation is not None
    
    def test_question_with_answer_no_answer(self):
        """Test QuestionWithAnswer without answer (unanswered question)."""
        question = QuestionWithAnswer(
            question_id=1,
            question_text="What is Python?",
            question_order=1,
            answer=None
        )
        assert question.question_id == 1
        assert question.answer is None
    
    def test_interview_report_valid(self):
        """Test InterviewReport with complete data."""
        scores = EvaluationScores(
            correctness=8.5,
            completeness=7.0,
            quality=9.0,
            communication=8.0
        )
        evaluation = EvaluationResponse(
            scores=scores,
            feedback="Good answer.",
            suggestions=["Add more details"],
            evaluated_at=datetime.now(),
            status="completed"
        )
        answer = AnswerResponse(
            id=1,
            answer_text="Python is a high-level programming language.",
            submitted_at=datetime.now(),
            evaluation=evaluation
        )
        question = QuestionWithAnswer(
            question_id=1,
            question_text="What is Python?",
            question_order=1,
            answer=answer
        )
        report = InterviewReport(
            interview_id=1,
            role="Python Developer",
            created_at=datetime.now(),
            questions=[question],
            overall_score=8.125
        )
        assert report.interview_id == 1
        assert report.role == "Python Developer"
        assert len(report.questions) == 1
        assert report.overall_score == 8.125
    
    def test_interview_report_no_overall_score(self):
        """Test InterviewReport without overall score (no evaluations yet)."""
        question = QuestionWithAnswer(
            question_id=1,
            question_text="What is Python?",
            question_order=1,
            answer=None
        )
        report = InterviewReport(
            interview_id=1,
            role="Python Developer",
            created_at=datetime.now(),
            questions=[question],
            overall_score=None
        )
        assert report.interview_id == 1
        assert report.overall_score is None
    
    def test_interview_report_overall_score_validation(self):
        """Test InterviewReport validates overall_score range."""
        question = QuestionWithAnswer(
            question_id=1,
            question_text="What is Python?",
            question_order=1,
            answer=None
        )
        
        # Test invalid score > 10
        with pytest.raises(ValidationError):
            InterviewReport(
                interview_id=1,
                role="Python Developer",
                created_at=datetime.now(),
                questions=[question],
                overall_score=11.0
            )
        
        # Test invalid score < 0
        with pytest.raises(ValidationError):
            InterviewReport(
                interview_id=1,
                role="Python Developer",
                created_at=datetime.now(),
                questions=[question],
                overall_score=-1.0
            )
