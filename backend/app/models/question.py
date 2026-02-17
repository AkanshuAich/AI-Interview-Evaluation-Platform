"""
Question model for storing interview questions.
Each question belongs to an interview and can have multiple answers.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    """
    Question model representing a single question in an interview.
    
    Attributes:
        id: Primary key
        interview_id: Foreign key to the interview this question belongs to
        question_text: The actual question text
        question_order: Order of this question in the interview (1-indexed)
        interview: Relationship to the Interview this question belongs to
        answers: Relationship to all answers submitted for this question
    
    Requirements:
        - 8.4: Database models for questions
        - 2.3: Store questions with interview relationship
    """
    __tablename__ = "questions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to interview
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, interview_id={self.interview_id}, order={self.question_order})>"
