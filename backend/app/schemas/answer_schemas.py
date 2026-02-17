"""
Pydantic schemas for answer submission and evaluation.
Handles request/response validation for answer submission and evaluation results.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AnswerSubmit(BaseModel):
    """
    Schema for answer submission request.
    
    Validates:
        - Interview ID and question ID are provided
        - Answer text meets minimum length requirement
    
    Requirements: 7.5
    """
    interview_id: int = Field(..., gt=0, description="ID of the interview")
    question_id: int = Field(..., gt=0, description="ID of the question being answered")
    answer_text: str = Field(..., min_length=10, description="Answer text (min 10 characters)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "interview_id": 1,
                    "question_id": 1,
                    "answer_text": "A list is mutable and can be modified after creation, while a tuple is immutable and cannot be changed once created. Lists use square brackets [] while tuples use parentheses ()."
                }
            ]
        }
    }


class EvaluationScores(BaseModel):
    """
    Schema for evaluation scores.
    
    Validates:
        - All scores are within valid range (0-10)
        - All required scoring dimensions are present
    
    Requirements: 7.5, 5.1
    """
    correctness: float = Field(..., ge=0, le=10, description="Correctness score (0-10)")
    completeness: float = Field(..., ge=0, le=10, description="Completeness score (0-10)")
    quality: float = Field(..., ge=0, le=10, description="Code/answer quality score (0-10)")
    communication: float = Field(..., ge=0, le=10, description="Communication clarity score (0-10)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "correctness": 8.5,
                    "completeness": 7.0,
                    "quality": 9.0,
                    "communication": 8.0
                }
            ]
        }
    }


class EvaluationResponse(BaseModel):
    """
    Schema for evaluation data in responses.
    
    Requirements: 7.5, 5.1, 5.2, 5.3
    """
    scores: EvaluationScores = Field(..., description="Structured evaluation scores")
    feedback: str = Field(..., min_length=1, description="Detailed feedback text")
    suggestions: List[str] = Field(default_factory=list, description="List of improvement suggestions")
    evaluated_at: datetime = Field(..., description="Evaluation completion timestamp")
    status: str = Field(..., description="Evaluation status (pending, completed, failed)")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "scores": {
                        "correctness": 8.5,
                        "completeness": 7.0,
                        "quality": 9.0,
                        "communication": 8.0
                    },
                    "feedback": "Good understanding of the fundamental differences between lists and tuples. The answer correctly identifies mutability as the key distinction.",
                    "suggestions": [
                        "Consider mentioning performance implications",
                        "Could add examples of when to use each data structure"
                    ],
                    "evaluated_at": "2024-01-15T10:35:00Z",
                    "status": "completed"
                }
            ]
        }
    }


class AnswerResponse(BaseModel):
    """
    Schema for answer data in responses.
    Includes the answer details and optional evaluation results.
    
    Requirements: 7.5
    """
    id: int = Field(..., description="Answer ID")
    answer_text: str = Field(..., description="The submitted answer text")
    submitted_at: datetime = Field(..., description="Answer submission timestamp")
    evaluation: Optional[EvaluationResponse] = Field(None, description="Evaluation results (if completed)")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "answer_text": "A list is mutable and can be modified after creation, while a tuple is immutable.",
                    "submitted_at": "2024-01-15T10:30:00Z",
                    "evaluation": {
                        "scores": {
                            "correctness": 8.5,
                            "completeness": 7.0,
                            "quality": 9.0,
                            "communication": 8.0
                        },
                        "feedback": "Good understanding of the fundamental differences.",
                        "suggestions": ["Consider mentioning performance implications"],
                        "evaluated_at": "2024-01-15T10:35:00Z",
                        "status": "completed"
                    }
                }
            ]
        }
    }
