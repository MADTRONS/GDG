"""Tests for user repository database operations."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        username=r'\COLLEGE\testuser',
        password_hash=hash_password('testpassword'),
        is_blocked=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_get_by_username_exists(db_session: AsyncSession, test_user: User):
    """Test finding an existing user by username."""
    repo = UserRepository(db_session)
    
    # Find the user
    found_user = await repo.get_by_username(test_user.username)
    
    # Verify user was found
    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.username == test_user.username
    assert found_user.is_blocked == test_user.is_blocked


@pytest.mark.asyncio
async def test_get_by_username_not_found(db_session: AsyncSession):
    """Test returns None for nonexistent user."""
    repo = UserRepository(db_session)
    
    # Try to find non-existent user
    found_user = await repo.get_by_username(r'\COLLEGE\nonexistent')
    
    # Should return None
    assert found_user is None


@pytest.mark.asyncio
async def test_get_by_username_case_sensitive(db_session: AsyncSession, test_user: User):
    """Test username lookup is case-sensitive."""
    repo = UserRepository(db_session)
    
    # Try different case
    found_user = await repo.get_by_username(test_user.username.upper())
    
    # Should not find user (case-sensitive)
    assert found_user is None
    
    # Exact case should work
    found_user = await repo.get_by_username(test_user.username)
    assert found_user is not None


@pytest.mark.asyncio
async def test_get_blocked_user(db_session: AsyncSession):
    """Test finding a blocked user."""
    # Create blocked user
    blocked_user = User(
        username=r'\COLLEGE\blocked',
        password_hash=hash_password('password'),
        is_blocked=True
    )
    db_session.add(blocked_user)
    await db_session.commit()
    await db_session.refresh(blocked_user)
    
    repo = UserRepository(db_session)
    found_user = await repo.get_by_username(blocked_user.username)
    
    # Should find user and reflect blocked status
    assert found_user is not None
    assert found_user.is_blocked is True