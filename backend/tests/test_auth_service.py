"""
Unit tests for authentication service.
Tests password hashing, token generation, and validation.
"""
import pytest
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from app.core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_returns_different_hash(self):
        """Test that hashing the same password twice produces different hashes (due to salt)."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to unique salts
        assert hash1 != hash2
        assert hash1 != password  # Hash should not equal plain text
    
    def test_verify_password_with_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_with_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password("wrong_password", hashed) is False
    
    def test_hash_password_with_empty_string(self):
        """Test hashing an empty string."""
        hashed = hash_password("")
        assert hashed != ""
        assert verify_password("", hashed) is True


class TestTokenGeneration:
    """Test JWT token creation and validation."""
    
    def test_create_access_token_with_default_expiration(self):
        """Test creating a token with default expiration time."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify contents
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "123"
        assert "exp" in payload
    
    def test_create_access_token_with_custom_expiration(self):
        """Test creating a token with custom expiration time."""
        data = {"sub": "456"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        # Decode and verify expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "456"
        assert "exp" in payload
    
    def test_verify_token_with_valid_token(self):
        """Test verifying a valid token."""
        data = {"sub": "789"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "789"
        assert "exp" in payload
    
    def test_verify_token_with_invalid_token(self):
        """Test that verify_token raises HTTPException for invalid token."""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    def test_verify_token_with_expired_token(self):
        """Test that verify_token raises HTTPException for expired token."""
        data = {"sub": "999"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
    
    def test_verify_token_with_wrong_secret(self):
        """Test that a token signed with different secret is rejected."""
        # Create token with different secret
        data = {"sub": "111"}
        wrong_token = jwt.encode(data, "wrong_secret_key", algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(wrong_token)
        
        assert exc_info.value.status_code == 401


class TestTokenPayload:
    """Test token payload handling."""
    
    def test_token_contains_all_claims(self):
        """Test that token contains all expected claims."""
        data = {"sub": "123", "username": "testuser", "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
    
    def test_token_with_minimal_data(self):
        """Test creating token with only required 'sub' claim."""
        data = {"sub": "456"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "456"
        assert "exp" in payload
