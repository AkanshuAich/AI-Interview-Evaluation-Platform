"""
Evaluation model for storing LLM-powered assessment results.
Each evaluation belongs to one answer and contains structured scoring data.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Evaluation(Base):
    """
    Evaluation model representing the LLM assessment of an answer.
    
    Attributes:
        id: Primary key
        answer_id: Foreign key to the answer being evaluated (unique - one-to-one)
        scores: JSONB field containing numerical scores (correctness, completeness, quality, communication)
        feedback: Text feedback explaining the scoring rationale
        suggestions: JSONB field containing array of improvement suggestions
        evaluated_at: Timestamp of evaluation completion
        status: Evaluation status (pending, completed, failed)
        answer: One-to-one relationship to the Answer being evaluated
    
    Requirements:
        - 8.4: Database models for evaluations
        - 4.3: Store evaluation results with structured JSON
        - 5.1, 5.2, 5.3: Store scores, feedback, and suggestions
    """
    __tablename__ = "evaluations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to answer (unique for one-to-one relationship)
    answer_id = Column(Integer, ForeignKey("answers.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Evaluation data stored as JSON
    # scores format: {"correctness": float, "completeness": float, "quality": float, "communication": float}
    scores = Column(JSONB, nullable=False)
    
    # Feedback text
    feedback = Column(Text, nullable=False)
    
    # Suggestions stored as JSON array
    # suggestions format: ["suggestion 1", "suggestion 2", ...]
    suggestions = Column(JSONB, nullable=False)
    
    # Timestamp
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Status tracking
    status = Column(String(20), nullable=False, default="pending", index=True)
    
    # Relationships
    answer = relationship("Answer", back_populates="evaluation")
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, answer_id={self.answer_id}, status='{self.status}')>"
