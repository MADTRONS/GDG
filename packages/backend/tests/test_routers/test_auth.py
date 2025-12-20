"""Tests for authentication endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import hash_password


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with valid credentials."""
    user = User(
        username=r'\COLLEGE\testuser',
        password_hash=hash_password('correctpassword'),
        is_blocked=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def blocked_user(db_session: AsyncSession) -> User:
    """Create a blocked test user."""
    user = User(
        username=r'\COLLEGE\blockeduser',
        password_hash=hash_password('password'),
        is_blocked=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login with correct credentials."""
    response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    
    # Check status code
    assert response.status_code == 200
    
    # Check response body
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert 'user' in data
    assert data['user']['username'] == test_user.username
    assert data['user']['is_blocked'] is False
    
    # Check cookie is set
    assert 'set-cookie' in response.headers
    cookie_header = response.headers['set-cookie']
    assert 'access_token=' in cookie_header
    assert 'HttpOnly' in cookie_header
    assert 'SameSite=lax' in cookie_header


@pytest.mark.asyncio
async def test_login_invalid_format(client: AsyncClient):
    """Test login fails with invalid username format."""
    response = await client.post('/api/auth/login', json={
        'username': 'invalidformat',
        'password': 'password'
    })
    
    # Should return 422 (Pydantic validation error)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_format_missing_domain(client: AsyncClient):
    """Test login fails with username missing domain."""
    response = await client.post('/api/auth/login', json={
        'username': 'justusername',
        'password': 'password'
    })
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    """Test login fails for nonexistent user with generic error."""
    response = await client.post('/api/auth/login', json={
        'username': r'\COLLEGE\nonexistent',
        'password': 'password'
    })
    
    # Should return 401
    assert response.status_code == 401
    
    # Should have generic error message
    data = response.json()
    assert data['detail'] == 'Invalid username or password'


@pytest.mark.asyncio
async def test_login_blocked_user(client: AsyncClient, blocked_user: User):
    """Test login fails for blocked user with specific error."""
    response = await client.post('/api/auth/login', json={
        'username': blocked_user.username,
        'password': 'password'
    })
    
    # Should return 403
    assert response.status_code == 403
    
    # Should have specific blocked message
    data = response.json()
    assert 'blocked' in data['detail'].lower()
    assert 'support' in data['detail'].lower()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """Test login fails for incorrect password with generic error."""
    response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'wrongpassword'
    })
    
    # Should return 401
    assert response.status_code == 401
    
    # Should have generic error message (no user enumeration)
    data = response.json()
    assert data['detail'] == 'Invalid username or password'


@pytest.mark.asyncio
async def test_login_empty_password(client: AsyncClient, test_user: User):
    """Test login fails for empty password."""
    response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': ''
    })
    
    # Should return 422 or 401
    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_login_missing_fields(client: AsyncClient):
    """Test login fails when required fields are missing."""
    # Missing password
    response = await client.post('/api/auth/login', json={
        'username': r'\COLLEGE\testuser'
    })
    assert response.status_code == 422
    
    # Missing username
    response = await client.post('/api/auth/login', json={
        'password': 'password'
    })
    assert response.status_code == 422
    
    # Missing both
    response = await client.post('/api/auth/login', json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_jwt_token_structure(client: AsyncClient, test_user: User):
    """Test JWT token has correct structure and claims."""
    from jose import jwt
    from app.config import get_settings
    
    settings = get_settings()
    
    response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    
    assert response.status_code == 200
    
    # Decode token
    token = response.json()['access_token']
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    # Check claims
    assert 'user_id' in decoded
    assert 'username' in decoded
    assert decoded['username'] == test_user.username
    assert 'exp' in decoded
    assert 'iat' in decoded


@pytest.mark.asyncio
async def test_login_case_sensitive_password(client: AsyncClient, test_user: User):
    """Test password is case-sensitive."""
    response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'CORRECTPASSWORD'
    })
    
    assert response.status_code == 401

# Logout endpoint tests


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, test_user: User):
    """Test successful logout with valid authentication."""
    # Login first
    login_response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    assert login_response.status_code == 200
    
    # Logout
    logout_response = await client.post('/api/auth/logout')
    assert logout_response.status_code == 200
    
    # Check response
    data = logout_response.json()
    assert 'message' in data
    assert data['message'] == 'Successfully logged out'


@pytest.mark.asyncio
async def test_logout_clears_cookie(client: AsyncClient, test_user: User):
    """Test logout clears the authentication cookie."""
    # Login first
    login_response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    assert login_response.status_code == 200
    
    # Logout
    logout_response = await client.post('/api/auth/logout')
    assert logout_response.status_code == 200
    
    # Check cookie is cleared (set-cookie header present with max_age=0)
    assert 'set-cookie' in logout_response.headers
    cookie_header = logout_response.headers['set-cookie']
    assert 'access_token=' in cookie_header
    assert 'Max-Age=0' in cookie_header or 'max-age=0' in cookie_header.lower()


@pytest.mark.asyncio
async def test_logout_without_authentication(client: AsyncClient):
    """Test logout fails without authentication."""
    # Attempt logout without being logged in
    response = await client.post('/api/auth/logout')
    
    # Should return 401
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


@pytest.mark.asyncio
async def test_logout_prevents_further_access(client: AsyncClient, test_user: User):
    """Test subsequent requests fail after logout."""
    # Login
    login_response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    assert login_response.status_code == 200
    
    # Access protected endpoint - should work
    me_response = await client.get('/api/auth/me')
    assert me_response.status_code == 200
    
    # Logout
    logout_response = await client.post('/api/auth/logout')
    assert logout_response.status_code == 200
    
    # Try to access protected endpoint after logout - should fail
    me_response_after = await client.get('/api/auth/me')
    assert me_response_after.status_code == 401


# /me endpoint tests


@pytest.mark.asyncio
async def test_me_endpoint_authenticated(client: AsyncClient, test_user: User):
    """Test /me endpoint returns user info when authenticated."""
    # Login first
    login_response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    assert login_response.status_code == 200
    
    # Call /me endpoint
    response = await client.get('/api/auth/me')
    assert response.status_code == 200
    
    # Check response
    data = response.json()
    assert 'user_id' in data
    assert 'username' in data
    assert data['username'] == test_user.username
    assert data['user_id'] == str(test_user.id)


@pytest.mark.asyncio
async def test_me_endpoint_unauthenticated(client: AsyncClient):
    """Test /me endpoint fails without authentication."""
    response = await client.get('/api/auth/me')
    
    # Should return 401
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


# Integration tests


@pytest.mark.asyncio
async def test_full_authentication_flow(client: AsyncClient, test_user: User):
    """Test full flow: login -> access protected -> logout -> fail to access."""
    # Step 1: Login
    login_response = await client.post('/api/auth/login', json={
        'username': test_user.username,
        'password': 'correctpassword'
    })
    assert login_response.status_code == 200
    
    # Step 2: Access protected resource
    me_response = await client.get('/api/auth/me')
    assert me_response.status_code == 200
    assert me_response.json()['username'] == test_user.username
    
    # Step 3: Logout
    logout_response = await client.post('/api/auth/logout')
    assert logout_response.status_code == 200
    
    # Step 4: Fail to access protected resource
    me_response_after = await client.get('/api/auth/me')
    assert me_response_after.status_code == 401


@pytest.mark.asyncio
async def test_multiple_login_logout_cycles(client: AsyncClient, test_user: User):
    """Test multiple login/logout cycles work correctly."""
    for _ in range(3):
        # Login
        login_response = await client.post('/api/auth/login', json={
            'username': test_user.username,
            'password': 'correctpassword'
        })
        assert login_response.status_code == 200
        
        # Access protected endpoint
        me_response = await client.get('/api/auth/me')
        assert me_response.status_code == 200
        
        # Logout
        logout_response = await client.post('/api/auth/logout')
        assert logout_response.status_code == 200
        
        # Verify logout worked
        me_response_after = await client.get('/api/auth/me')
        assert me_response_after.status_code == 401
