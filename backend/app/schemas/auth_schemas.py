"""
Pydantic schemas for authentication and user management.
Handles request/response validation for user registration, login, and profile data.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    """
    Schema for user registration request.
    
    Validates:
        - Username is provided
        - Email is valid format
        - Password meets minimum length requirement
        - Password does not exceed bcrypt's 72-byte limit
    
    Requirements: 7.5
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for login")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 characters, bcrypt limit)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "johndoe",
                    "email": "john@example.com",
                    "password": "securepass123"
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    Requirements: 7.5
    """
    username: str = Field(..., min_length=1, description="Username for authentication")
    password: str = Field(..., min_length=1, description="User password")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "johndoe",
                    "password": "securepass123"
                }
            ]
        }
    }


class Token(BaseModel):
    """
    Schema for JWT token response.
    
    Requirements: 7.5
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """
    Schema for user profile response.
    Returns user information without sensitive data (no password).
    
    Requirements: 7.5
    """
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john@example.com"
                }
            ]
        }
    }
