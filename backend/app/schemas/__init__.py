"""
Pydantic schemas for request/response validation.
Exports all schema classes for easy importing throughout the application.
"""
from app.schemas.auth_schemas import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse
)
from app.schemas.interview_schemas import (
    InterviewCreate,
    QuestionResponse,
    InterviewResponse
)
from app.schemas.answer_schemas import (
    AnswerSubmit,
    EvaluationScores,
    EvaluationResponse,
    AnswerResponse
)
from app.schemas.report_schemas import (
    QuestionWithAnswer,
    InterviewReport
)

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "UserResponse",
    # Interview schemas
    "InterviewCreate",
    "QuestionResponse",
    "InterviewResponse",
    # Answer schemas
    "AnswerSubmit",
    "EvaluationScores",
    "EvaluationResponse",
    "AnswerResponse",
    # Report schemas
    "QuestionWithAnswer",
    "InterviewReport",
]
