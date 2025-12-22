"""Tests for admin authentication endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from app.models.admin import Admin, AdminRole


def hash_admin_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> Admin:
    """Create a test admin with valid credentials."""
    admin = Admin(
        email='admin@test.com',
        password_hash=hash_admin_password('AdminPass123!'),
        role=AdminRole.SUPER_ADMIN,
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def inactive_admin(db_session: AsyncSession) -> Admin:
    """Create an inactive test admin."""
    admin = Admin(
        email='inactive@test.com',
        password_hash=hash_admin_password('InactivePass123!'),
        role=AdminRole.SYSTEM_MONITOR,
        is_active=False
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def content_manager_admin(db_session: AsyncSession) -> Admin:
    """Create a content manager admin."""
    admin = Admin(
        email='content@test.com',
        password_hash=hash_admin_password('ContentPass123!'),
        role=AdminRole.CONTENT_MANAGER,
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.mark.asyncio
async def test_admin_login_success(client: AsyncClient, test_admin: Admin):
    """Test successful admin login with correct credentials."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPass123!'
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['message'] == 'Login successful'
    assert data['email'] == 'admin@test.com'
    assert data['role'] == 'SUPER_ADMIN'
    
    # Check cookie is set
    assert 'set-cookie' in response.headers
    cookie_header = response.headers['set-cookie']
    assert 'admin_token=' in cookie_header
    assert 'HttpOnly' in cookie_header
    assert 'SameSite=lax' in cookie_header


@pytest.mark.asyncio
async def test_admin_login_case_insensitive_email(client: AsyncClient, test_admin: Admin):
    """Test admin login is case-insensitive for email."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'ADMIN@TEST.COM',
        'password': 'AdminPass123!'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == 'admin@test.com'


@pytest.mark.asyncio
async def test_admin_login_invalid_password(client: AsyncClient, test_admin: Admin):
    """Test admin login fails with incorrect password."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'admin@test.com',
        'password': 'WrongPassword!'
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data['detail'] == 'Invalid email or password'


@pytest.mark.asyncio
async def test_admin_login_nonexistent_email(client: AsyncClient, test_admin: Admin):
    """Test admin login fails for nonexistent email."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'nobody@test.com',
        'password': 'SomePassword!'
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data['detail'] == 'Invalid email or password'


@pytest.mark.asyncio
async def test_admin_login_inactive_admin(client: AsyncClient, inactive_admin: Admin):
    """Test admin login fails for inactive admin account."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'inactive@test.com',
        'password': 'InactivePass123!'
    })
    
    assert response.status_code == 403
    data = response.json()
    assert 'deactivated' in data['detail'].lower()


@pytest.mark.asyncio
async def test_admin_login_missing_email(client: AsyncClient):
    """Test admin login fails with missing email."""
    response = await client.post('/api/admin/auth/login', json={
        'password': 'SomePassword!'
    })
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_admin_login_missing_password(client: AsyncClient, test_admin: Admin):
    """Test admin login fails with missing password."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'admin@test.com'
    })
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_admin_logout_success(client: AsyncClient, test_admin: Admin):
    """Test successful admin logout clears cookie."""
    # First login
    login_response = await client.post('/api/admin/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPass123!'
    })
    assert login_response.status_code == 200
    
    # Extract the cookie from login response
    cookies = login_response.cookies
    
    # Now logout
    logout_response = await client.post(
        '/api/admin/auth/logout',
        cookies=cookies
    )
    
    assert logout_response.status_code == 200
    data = logout_response.json()
    assert data['message'] == 'Logout successful'
    
    # Check cookie is cleared (max-age=0 or expires in past)
    assert 'set-cookie' in logout_response.headers


@pytest.mark.asyncio
async def test_admin_me_success(client: AsyncClient, test_admin: Admin):
    """Test getting current admin info with valid token."""
    # First login to get token
    login_response = await client.post('/api/admin/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPass123!'
    })
    assert login_response.status_code == 200
    cookies = login_response.cookies
    
    # Get current admin info
    me_response = await client.get('/api/admin/auth/me', cookies=cookies)
    
    assert me_response.status_code == 200
    data = me_response.json()
    assert data['email'] == 'admin@test.com'
    assert data['role'] == 'SUPER_ADMIN'
    assert 'admin_id' in data


@pytest.mark.asyncio
async def test_admin_me_no_token(client: AsyncClient):
    """Test getting admin info without token fails."""
    response = await client.get('/api/admin/auth/me')
    
    assert response.status_code == 401
    data = response.json()
    assert 'not authenticated' in data['detail'].lower() or 'token' in data['detail'].lower()


@pytest.mark.asyncio
async def test_admin_me_invalid_token(client: AsyncClient):
    """Test getting admin info with invalid token fails."""
    response = await client.get(
        '/api/admin/auth/me',
        cookies={'admin_token': 'invalid.token.here'}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_login_different_roles(client: AsyncClient, content_manager_admin: Admin):
    """Test login works for different admin roles."""
    response = await client.post('/api/admin/auth/login', json={
        'email': 'content@test.com',
        'password': 'ContentPass123!'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['role'] == 'CONTENT_MANAGER'


@pytest.mark.asyncio
async def test_admin_login_updates_last_login(client: AsyncClient, test_admin: Admin, db_session: AsyncSession):
    """Test that login updates last_login_at timestamp."""
    assert test_admin.last_login_at is None
    
    response = await client.post('/api/admin/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPass123!'
    })
    
    assert response.status_code == 200
    
    # Refresh the admin from database
    await db_session.refresh(test_admin)
    assert test_admin.last_login_at is not None
