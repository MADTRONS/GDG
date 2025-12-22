"""Test fixtures and configuration for the test suite."""
import asyncio
import sys
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.models.base import Base
from app.database import get_db


# Windows-specific: Use SelectorEventLoop for psycopg compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Test database URL (can be overridden by environment variable)
TEST_DATABASE_URL = 'postgresql+psycopg://counseling:devpassword@localhost:5432/counseling_platform_test'

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope='function')
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    Creates tables, yields session, then drops tables.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Provide session for test
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
    
    # Clean up - drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Create authentication headers with a valid JWT token."""
    from app.utils.jwt import create_access_token
    from uuid import uuid4
    
    token = create_access_token(user_id=uuid4(), username="testdomain\\testuser")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    from app.models.user import User
    from app.utils.security import hash_password
    
    user = User(
        username=r'\testdomain\testuser',
        password_hash=hash_password('testpassword'),
        is_blocked=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, test_user) -> AsyncClient:
    """Create an authenticated test client by logging in."""
    # Login to get cookie
    response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'testpassword'
    })
    assert response.status_code == 200
    return client


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession):
    """Create a test counselor category."""
    from app.models.counselor_category import CounselorCategory
    
    category = CounselorCategory(
        name='Test Category',
        description='A test category for counseling',
        icon_name='test_icon',
        system_prompt='You are a friendly counselor',
        enabled=True
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category