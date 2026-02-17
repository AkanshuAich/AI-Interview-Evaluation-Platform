"""
Authentication router for user registration, login, and profile endpoints.

Endpoints:
    - POST /api/auth/register: Register a new user
    - POST /api/auth/login: Authenticate and receive JWT token
    - GET /api/auth/me: Get current user profile (protected)

Requirements:
    - 1.1: Generate JWT tokens for valid credentials
    - 1.2: Return authentication errors for invalid credentials
    - 1.3: Validate JWT tokens on protected endpoints
    - 1.4: Reject expired JWT tokens
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth_schemas import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (username, email, password)
        db: Database session
        
    Returns:
        Success message with user_id
        
    Raises:
        HTTPException 409: If username or email already exists
        
    Requirements:
        - 1.5: Store user credentials securely using password hashing
    """
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    try:
        hashed_pwd = hash_password(user_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "user_id": new_user.id,
        "message": "User registered successfully"
    }


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    Args:
        credentials: User login credentials (username, password)
        db: Database session
        
    Returns:
        JWT access token and token type
        
    Raises:
        HTTPException 401: If credentials are invalid
        
    Requirements:
        - 1.1: Generate JWT tokens for valid credentials
        - 1.2: Return authentication errors for invalid credentials
    """
    # Fetch user by username
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate JWT token with user ID as subject
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile information.
    
    Args:
        current_user: Current user extracted from JWT token
        
    Returns:
        User profile data (id, username, email)
        
    Requirements:
        - 1.3: Validate JWT tokens on protected endpoints
        - 1.4: Reject expired JWT tokens
        
    Note:
        This endpoint requires a valid JWT token in the Authorization header.
        The get_current_user dependency handles token validation and user extraction.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )
