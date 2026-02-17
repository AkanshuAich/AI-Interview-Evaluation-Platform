"""
Pydantic schemas for interview reports.
Handles response validation for complete interview reports with questions, answers, and evaluations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.answer_schemas import AnswerResponse


class QuestionWithAnswer(BaseModel):
    """
    Schema for question with associated answer in report.
    Combines question data with optional answer and evaluation.
    
    Requirements: 7.5
    """
    question_id: int = Field(..., description="Question ID")
    question_text: str = Field(..., description="The question text")
    question_order: int = Field(..., description="Order of question in interview")
    answer: Optional[AnswerResponse] = Field(None, description="Answer data (if submitted)")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "question_id": 1,
                    "question_text": "Explain the difference between a list and a tuple in Python.",
                    "question_order": 1,
                    "answer": {
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
                }
            ]
        }
    }


class InterviewReport(BaseModel):
    """
    Schema for complete interview report.
    Includes interview metadata, all questions with answers, and overall score.
    
    Requirements: 7.5, 6.1, 6.2, 6.3
    """
    interview_id: int = Field(..., description="Interview ID")
    role: str = Field(..., description="Job role")
    created_at: datetime = Field(..., description="Interview creation timestamp")
    questions: List[QuestionWithAnswer] = Field(default_factory=list, description="All questions with answers and evaluations")
    overall_score: Optional[float] = Field(None, ge=0, le=10, description="Average score across all evaluations (if available)")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "interview_id": 1,
                    "role": "Senior Python Developer",
                    "created_at": "2024-01-15T10:00:00Z",
                    "questions": [
                        {
                            "question_id": 1,
                            "question_text": "Explain the difference between a list and a tuple in Python.",
                            "question_order": 1,
                            "answer": {
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
                        }
                    ],
                    "overall_score": 8.125
                }
            ]
        }
    }
