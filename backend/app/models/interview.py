"""
Interview model for storing interview sessions.
Each interview belongs to a user and contains multiple questions.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Interview(Base):
    """
    Interview model representing a collection of role-based questions.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to the user who created the interview
        role: The job role for which questions were generated
        created_at: Timestamp of interview creation
        user: Relationship to the User who created this interview
        questions: Relationship to all questions in this interview
    
    Requirements:
        - 8.4: Database models for interviews
        - 2.3: Persist interview with generated questions
        - 2.5: Associate interview with authenticated user
    """
    __tablename__ = "interviews"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Interview details
    role = Column(String(100), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan", order_by="Question.question_order")
    
    def __repr__(self):
        return f"<Interview(id={self.id}, role='{self.role}', user_id={self.user_id})>"
