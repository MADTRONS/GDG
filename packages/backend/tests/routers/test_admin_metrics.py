"""Tests for admin metrics endpoints."""
import pytest
import pytest_asyncio
from datetime import UTC, datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin, AdminRole
from app.models.counselor_category import CounselorCategory
from app.models.session import Session
from app.models.user import User
from app.utils.admin_jwt import create_admin_access_token
from app.utils.security import hash_password


@pytest_asyncio.fixture
async def super_admin(db_session: AsyncSession) -> Admin:
    """Create a test super admin."""
    admin = Admin(
        email="super@test.com",
        password_hash=hash_password("SuperPass123!"),
        role=AdminRole.SUPER_ADMIN,
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def system_monitor(db_session: AsyncSession) -> Admin:
    """Create a test system monitor."""
    admin = Admin(
        email="monitor@test.com",
        password_hash=hash_password("MonitorPass123!"),
        role=AdminRole.SYSTEM_MONITOR,
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def content_manager(db_session: AsyncSession) -> Admin:
    """Create a test content manager."""
    admin = Admin(
        email="content@test.com",
        password_hash=hash_password("ContentPass123!"),
        role=AdminRole.CONTENT_MANAGER,
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession) -> CounselorCategory:
    """Create a test counselor category."""
    category = CounselorCategory(
        name="Test Health",
        description="Test health counselor",
        icon_name="heart",
        system_prompt="You are a test health counselor.",
        enabled=True
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def active_session(db_session: AsyncSession, test_category: CounselorCategory) -> Session:
    """Create a test active session."""
    # Create test user
    user = User(
        username="\\testdomain\\teststudent",
        password_hash=hash_password("TestPass123!")
    )
    db_session.add(user)
    await db_session.commit()
    
    # Create active session (started recently, no end time)
    session = Session(
        user_id=user.id,
        counselor_category=test_category.name,
        mode="voice",
        room_name=f"test_room_{user.id}",
        started_at=datetime.now(UTC) - timedelta(minutes=10),
        quality_metrics={"connection_quality_average": "good"}
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest.mark.asyncio
async def test_get_current_metrics_super_admin(
    client: AsyncClient,
    super_admin: Admin,
    active_session: Session
):
    """Test getting current metrics as super admin."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/current",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "active_sessions_count" in data
    assert "avg_connection_quality" in data
    assert "error_rate_last_hour" in data
    assert "api_response_time_p95" in data
    assert "db_pool_active" in data
    assert "db_pool_size" in data
    assert "system_health" in data
    
    # Verify data types
    assert isinstance(data["active_sessions_count"], int)
    assert isinstance(data["avg_connection_quality"], str)
    assert isinstance(data["error_rate_last_hour"], float)
    assert isinstance(data["api_response_time_p95"], float)
    assert isinstance(data["system_health"], str)
    
    # Verify at least one active session
    assert data["active_sessions_count"] >= 1


@pytest.mark.asyncio
async def test_get_current_metrics_system_monitor(
    client: AsyncClient,
    system_monitor: Admin
):
    """Test getting current metrics as system monitor."""
    token = create_admin_access_token(
        system_monitor.id,
        system_monitor.email,
        system_monitor.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/current",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "active_sessions_count" in data


@pytest.mark.asyncio
async def test_get_current_metrics_unauthorized(client: AsyncClient):
    """Test getting metrics without authentication fails."""
    response = await client.get("/api/admin/metrics/current")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_metrics_content_manager_forbidden(
    client: AsyncClient,
    content_manager: Admin
):
    """Test content manager cannot access metrics."""
    token = create_admin_access_token(
        content_manager.id,
        content_manager.email,
        content_manager.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/current",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_session_metrics(
    client: AsyncClient,
    super_admin: Admin,
    active_session: Session
):
    """Test getting session metrics."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/sessions",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "total_sessions" in data
    assert "sessions_by_category" in data
    assert "connection_quality_distribution" in data
    
    # Verify data types
    assert isinstance(data["total_sessions"], int)
    assert isinstance(data["sessions_by_category"], dict)
    assert isinstance(data["connection_quality_distribution"], dict)
    
    # Verify at least one session
    assert data["total_sessions"] >= 1
    assert len(data["sessions_by_category"]) > 0


@pytest.mark.asyncio
async def test_get_session_metrics_unauthorized(client: AsyncClient):
    """Test getting session metrics without authentication fails."""
    response = await client.get("/api/admin/metrics/sessions")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_session_metrics_content_manager_forbidden(
    client: AsyncClient,
    content_manager: Admin
):
    """Test content manager cannot access session metrics."""
    token = create_admin_access_token(
        content_manager.id,
        content_manager.email,
        content_manager.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/sessions",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_external_services(
    client: AsyncClient,
    super_admin: Admin
):
    """Test getting external services status."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/external-services",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "daily_co" in data
    assert "livekit" in data
    assert "beyond_presence" in data
    
    # Verify status values are valid
    valid_statuses = ["operational", "degraded", "down", "unknown"]
    assert data["daily_co"] in valid_statuses
    assert data["livekit"] in valid_statuses
    assert data["beyond_presence"] in valid_statuses


@pytest.mark.asyncio
async def test_get_external_services_system_monitor(
    client: AsyncClient,
    system_monitor: Admin
):
    """Test system monitor can access external services status."""
    token = create_admin_access_token(
        system_monitor.id,
        system_monitor.email,
        system_monitor.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/external-services",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_system_health_determination(
    client: AsyncClient,
    super_admin: Admin
):
    """Test system health status is correctly determined."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/metrics/current",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify health status is one of the valid values
    valid_health = ["healthy", "degraded", "critical"]
    assert data["system_health"] in valid_health
    
    # With mock values (error_rate=0.01, api_p95=250), should be healthy
    assert data["system_health"] == "healthy"
