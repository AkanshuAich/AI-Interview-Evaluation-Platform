"""
Pydantic schemas for interview management.
Handles request/response validation for interview creation and retrieval.
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class InterviewCreate(BaseModel):
    """
    Schema for interview creation request.
    
    Validates:
        - Role is provided
        - Number of questions is within valid range (1-10)
    
    Requirements: 7.5
    """
    role: str = Field(..., min_length=1, max_length=100, description="Job role for interview questions")
    num_questions: int = Field(..., ge=1, le=10, description="Number of questions to generate (1-10)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "Senior Python Developer",
                    "num_questions": 5
                }
            ]
        }
    }


class QuestionResponse(BaseModel):
    """
    Schema for question data in responses.
    
    Requirements: 7.5
    """
    id: int = Field(..., description="Question ID")
    question_text: str = Field(..., description="The question text")
    question_order: int = Field(..., description="Order of question in interview (1-indexed)")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "question_text": "Explain the difference between a list and a tuple in Python.",
                    "question_order": 1
                }
            ]
        }
    }


class InterviewResponse(BaseModel):
    """
    Schema for interview data in responses.
    Includes the interview details and all associated questions.
    
    Requirements: 7.5
    """
    id: int = Field(..., description="Interview ID")
    role: str = Field(..., description="Job role")
    created_at: datetime = Field(..., description="Interview creation timestamp")
    questions: List[QuestionResponse] = Field(default_factory=list, description="List of questions in this interview")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "role": "Senior Python Developer",
                    "created_at": "2024-01-15T10:30:00Z",
                    "questions": [
                        {
                            "id": 1,
                            "question_text": "Explain the difference between a list and a tuple in Python.",
                            "question_order": 1
                        },
                        {
                            "id": 2,
                            "question_text": "What is a decorator in Python?",
                            "question_order": 2
                        }
                    ]
                }
            ]
        }
    }
