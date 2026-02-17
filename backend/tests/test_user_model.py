"""
Unit tests for User model.
Tests model creation, constraints, and basic functionality.
"""
import pytest
from sqlalchemy import select
from app.models.user import User


@pytest.mark.asyncio
async def test_user_creation(test_db):
    """Test creating a user with all required fields."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_here"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password_here"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_user_unique_username(test_db):
    """Test that username must be unique."""
    user1 = User(
        username="testuser",
        email="test1@example.com",
        hashed_password="hash1"
    )
    user2 = User(
        username="testuser",  # Same username
        email="test2@example.com",
        hashed_password="hash2"
    )
    
    test_db.add(user1)
    await test_db.commit()
    
    test_db.add(user2)
    with pytest.raises(Exception):  # Should raise IntegrityError
        await test_db.commit()


@pytest.mark.asyncio
async def test_user_unique_email(test_db):
    """Test that email must be unique."""
    user1 = User(
        username="testuser1",
        email="test@example.com",
        hashed_password="hash1"
    )
    user2 = User(
        username="testuser2",
        email="test@example.com",  # Same email
        hashed_password="hash2"
    )
    
    test_db.add(user1)
    await test_db.commit()
    
    test_db.add(user2)
    with pytest.raises(Exception):  # Should raise IntegrityError
        await test_db.commit()


@pytest.mark.asyncio
async def test_user_query_by_username(test_db):
    """Test querying user by username."""
    user = User(
        username="querytest",
        email="query@example.com",
        hashed_password="hash"
    )
    test_db.add(user)
    await test_db.commit()
    
    # Query by username
    result = await test_db.execute(
        select(User).where(User.username == "querytest")
    )
    found_user = result.scalar_one_or_none()
    
    assert found_user is not None
    assert found_user.username == "querytest"
    assert found_user.email == "query@example.com"


@pytest.mark.asyncio
async def test_user_query_by_email(test_db):
    """Test querying user by email."""
    user = User(
        username="emailtest",
        email="emailquery@example.com",
        hashed_password="hash"
    )
    test_db.add(user)
    await test_db.commit()
    
    # Query by email
    result = await test_db.execute(
        select(User).where(User.email == "emailquery@example.com")
    )
    found_user = result.scalar_one_or_none()
    
    assert found_user is not None
    assert found_user.username == "emailtest"
    assert found_user.email == "emailquery@example.com"
