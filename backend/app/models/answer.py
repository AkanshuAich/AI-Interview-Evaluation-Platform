"""
Answer model for storing candidate responses to interview questions.
Each answer belongs to a question and a user, and has one evaluation.
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Answer(Base):
    """
    Answer model representing a candidate's response to a question.
    
    Attributes:
        id: Primary key
        question_id: Foreign key to the question being answered
        user_id: Foreign key to the user who submitted the answer
        answer_text: The candidate's answer text
        submitted_at: Timestamp of answer submission
        question: Relationship to the Question being answered
        user: Relationship to the User who submitted the answer
        evaluation: One-to-one relationship to the Evaluation of this answer
    
    Requirements:
        - 8.4: Database models for answers
        - 3.2: Store answer with question and user relationships
    """
    __tablename__ = "answers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Answer details
    answer_text = Column(Text, nullable=False)
    
    # Timestamp
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")
    evaluation = relationship("Evaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, user_id={self.user_id})>"
