"""
Authentication service for JWT-based user authentication.
Handles password hashing, token generation, and user verification.

Requirements:
    - 1.1: Generate JWT tokens for valid credentials
    - 1.2: Return authentication errors for invalid credentials
    - 1.3: Validate JWT tokens before processing requests
    - 1.4: Reject expired JWT tokens
    - 1.5: Store user credentials securely using password hashing
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string with salt
        
    Raises:
        ValueError: If password exceeds bcrypt's 72-byte limit
        
    Requirements:
        - 1.5: Secure password storage using hashing
        
    Note:
        Bcrypt automatically generates a unique salt for each hash,
        so the same password will produce different hashes.
        Bcrypt has a 72-byte limit for passwords.
    """
    # Bcrypt has a 72-byte limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError("Password cannot exceed 72 bytes")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
        
    Requirements:
        - 1.2: Verify credentials for authentication
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a JWT access token with expiration.
    
    Args:
        data: Dictionary of claims to encode in the token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time, defaults to ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        Encoded JWT token string
        
    Requirements:
        - 1.1: Generate JWT tokens for valid credentials
        - 1.4: Include expiration time in tokens
        
    Note:
        The token includes an "exp" claim for expiration validation.
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode JWT token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Dictionary of decoded token claims
        
    Raises:
        HTTPException: If token is invalid, expired, or malformed
        
    Requirements:
        - 1.3: Validate JWT tokens before processing requests
        - 1.4: Reject expired JWT tokens
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and verify token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        # Token is invalid, expired, or malformed
        raise credentials_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract and validate the current user from JWT token.
    
    Args:
        token: JWT token extracted from Authorization header
        db: Database session
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
        
    Requirements:
        - 1.3: Validate JWT tokens on protected endpoints
        - 1.4: Reject expired tokens
        
    Usage:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify and decode token
    payload = verify_token(token)
    
    # Extract user ID from token
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user
