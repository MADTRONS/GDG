"""Tests for admin analytics endpoints."""
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
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="\\testdomain\\teststudent",
        password_hash=hash_password("TestPass123!")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_categories(db_session: AsyncSession) -> list[CounselorCategory]:
    """Create test counselor categories."""
    categories = [
        CounselorCategory(
            name="Mental Health",
            description="Mental health counselor",
            icon_name="brain",
            system_prompt="You are a mental health counselor.",
            enabled=True
        ),
        CounselorCategory(
            name="Academic",
            description="Academic counselor",
            icon_name="book",
            system_prompt="You are an academic counselor.",
            enabled=True
        )
    ]
    for category in categories:
        db_session.add(category)
    await db_session.commit()
    for category in categories:
        await db_session.refresh(category)
    return categories


@pytest_asyncio.fixture
async def test_sessions(
    db_session: AsyncSession,
    test_user: User,
    test_categories: list[CounselorCategory]
) -> list[Session]:
    """Create test sessions with varied data."""
    now = datetime.now(UTC)
    sessions = []
    
    # Create sessions across different days, categories, and modes
    for i in range(10):
        session = Session(
            user_id=test_user.id,
            counselor_category=test_categories[i % 2].name,
            mode="voice" if i % 3 == 0 else "video",
            room_name=f"test_room_{i}",
            started_at=now - timedelta(days=i, hours=8 + (i % 12)),
            ended_at=now - timedelta(days=i, hours=8 + (i % 12), minutes=30),
            duration_seconds=1800 + (i * 60)  # 30-39 minutes
        )
        db_session.add(session)
        sessions.append(session)
    
    await db_session.commit()
    for session in sessions:
        await db_session.refresh(session)
    return sessions


@pytest.mark.asyncio
async def test_get_session_analytics_super_admin(
    client: AsyncClient,
    super_admin: Admin,
    test_sessions: list[Session]
):
    """Test getting session analytics as super admin."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    # Query last 30 days
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    start_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/analytics/sessions?start_date={start_date}&end_date={end_date}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "total_sessions" in data
    assert "avg_duration" in data
    assert "sessions_by_category" in data
    assert "sessions_by_mode" in data
    assert "peak_usage_hours" in data
    assert "daily_trend" in data
    assert "avg_duration_by_category" in data
    
    # Verify data types
    assert isinstance(data["total_sessions"], int)
    assert isinstance(data["avg_duration"], (int, float))
    assert isinstance(data["sessions_by_category"], dict)
    assert isinstance(data["sessions_by_mode"], dict)
    assert isinstance(data["peak_usage_hours"], dict)
    assert isinstance(data["daily_trend"], dict)
    assert isinstance(data["avg_duration_by_category"], dict)
    
    # Verify we got sessions
    assert data["total_sessions"] == 10


@pytest.mark.asyncio
async def test_get_session_analytics_unauthorized(
    client: AsyncClient,
    test_sessions: list[Session]
):
    """Test getting analytics without authentication fails."""
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    start_date = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/analytics/sessions?start_date={start_date}&end_date={end_date}"
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_session_analytics_system_monitor_forbidden(
    client: AsyncClient,
    system_monitor: Admin,
    test_sessions: list[Session]
):
    """Test system monitor cannot access analytics."""
    token = create_admin_access_token(
        system_monitor.id,
        system_monitor.email,
        system_monitor.role.value
    )
    
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    start_date = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/analytics/sessions?start_date={start_date}&end_date={end_date}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_analytics_invalid_date_format(
    client: AsyncClient,
    super_admin: Admin
):
    """Test analytics with invalid date format fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/analytics/sessions?start_date=invalid&end_date=2025-12-31",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_analytics_start_after_end(
    client: AsyncClient,
    super_admin: Admin
):
    """Test analytics with start date after end date fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/analytics/sessions?start_date=2025-12-31&end_date=2025-01-01",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "before or equal" in response.json()["detail"]


@pytest.mark.asyncio
async def test_analytics_date_range_too_large(
    client: AsyncClient,
    super_admin: Admin
):
    """Test analytics with date range > 365 days fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/analytics/sessions?start_date=2023-01-01&end_date=2025-01-01",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "cannot exceed 365 days" in response.json()["detail"]


@pytest.mark.asyncio
async def test_analytics_aggregation_by_category(
    client: AsyncClient,
    super_admin: Admin,
    test_sessions: list[Session]
):
    """Test sessions are correctly aggregated by category."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    start_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/analytics/sessions?start_date={start_date}&end_date={end_date}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have both categories
    assert "Mental Health" in data["sessions_by_category"]
    assert "Academic" in data["sessions_by_category"]
    
    # Should sum to total sessions
    total_by_category = sum(data["sessions_by_category"].values())
    assert total_by_category == data["total_sessions"]


@pytest.mark.asyncio
async def test_analytics_aggregation_by_mode(
    client: AsyncClient,
    super_admin: Admin,
    test_sessions: list[Session]
):
    """Test sessions are correctly aggregated by mode."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    start_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/analytics/sessions?start_date={start_date}&end_date={end_date}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have voice and video modes
    assert "voice" in data["sessions_by_mode"]
    assert "video" in data["sessions_by_mode"]
    
    # Should sum to total sessions
    total_by_mode = sum(data["sessions_by_mode"].values())
    assert total_by_mode == data["total_sessions"]


@pytest.mark.asyncio
async def test_analytics_no_pii_exposure(
    client: AsyncClient,
    super_admin: Admin,
    test_sessions: list[Session]
):
    """Test analytics response contains no PII."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    start_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/analytics/sessions?start_date={start_date}&end_date={end_date}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Convert to string to check for any PII
    response_str = str(data)
    
    # Should not contain user IDs, room names, or transcript data
    assert "user_id" not in response_str
    assert "room_name" not in response_str
    assert "transcript" not in response_str
    
    # Should only have aggregated data
    assert all(isinstance(v, (int, float, dict)) for v in data.values())