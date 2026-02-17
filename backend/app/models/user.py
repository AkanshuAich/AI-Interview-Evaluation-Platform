"""
User model for authentication and authorization.
Stores user credentials and manages relationships with interviews and answers.
"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    User model representing authenticated users in the system.
    
    Attributes:
        id: Primary key
        username: Unique username for login
        email: Unique email address
        hashed_password: Bcrypt hashed password (never store plain text)
        created_at: Timestamp of user registration
        interviews: Relationship to interviews created by this user
        answers: Relationship to answers submitted by this user
    
    Requirements:
        - 8.4: Database models for users
        - 1.5: Secure password storage using hashing
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials - unique constraints ensure no duplicates
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
