"""Tests for admin audit log endpoints."""
import pytest
import pytest_asyncio
from datetime import UTC, datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin, AdminRole
from app.models.audit_log import AuditAction, AuditLog
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
async def test_audit_logs(
    db_session: AsyncSession,
    super_admin: Admin
) -> list[AuditLog]:
    """Create test audit log entries."""
    logs = []
    now = datetime.now(UTC)
    
    actions = [
        (AuditAction.CREATE, "counselor_category", {"name": "Mental Health"}),
        (AuditAction.UPDATE, "counselor_category", {"field": "description"}),
        (AuditAction.DELETE, "counselor_category", {"name": "Old Category"}),
        (AuditAction.LOGIN, "admin_auth", {"method": "password"}),
        (AuditAction.LOGOUT, "admin_auth", {}),
    ]
    
    for i, (action, resource_type, details) in enumerate(actions):
        log = AuditLog(
            admin_user_id=super_admin.id,
            action=action,
            resource_type=resource_type,
            details=details,
            ip_address="192.168.1.1",
            timestamp=now - timedelta(hours=i)
        )
        db_session.add(log)
        logs.append(log)
    
    await db_session.commit()
    for log in logs:
        await db_session.refresh(log)
    return logs


@pytest.mark.asyncio
async def test_get_audit_log_super_admin(
    client: AsyncClient,
    super_admin: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test getting audit log as super admin."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "logs" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "total_pages" in data
    
    assert isinstance(data["logs"], list)
    assert data["total_count"] == 5
    assert len(data["logs"]) == 5


@pytest.mark.asyncio
async def test_get_audit_log_unauthorized(
    client: AsyncClient,
    test_audit_logs: list[AuditLog]
):
    """Test getting audit log without authentication fails."""
    response = await client.get("/api/admin/audit-log")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_audit_log_system_monitor_forbidden(
    client: AsyncClient,
    system_monitor: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test system monitor cannot access audit log."""
    token = create_admin_access_token(
        system_monitor.id,
        system_monitor.email,
        system_monitor.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_audit_log_pagination(
    client: AsyncClient,
    super_admin: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test audit log pagination."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log?page=1&limit=2",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["logs"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total_count"] == 5
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_audit_log_filter_by_action(
    client: AsyncClient,
    super_admin: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test filtering audit log by action type."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log?action=CREATE",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 1
    assert all(log["action"] == "CREATE" for log in data["logs"])


@pytest.mark.asyncio
async def test_audit_log_filter_by_admin_user(
    client: AsyncClient,
    super_admin: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test filtering audit log by admin user ID."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        f"/api/admin/audit-log?admin_user_id={super_admin.id}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 5
    assert all(log["admin_email"] == super_admin.email for log in data["logs"])


@pytest.mark.asyncio
async def test_audit_log_filter_by_date_range(
    client: AsyncClient,
    super_admin: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test filtering audit log by date range."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    # Filter to today only
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    
    response = await client.get(
        f"/api/admin/audit-log?start_date={today}&end_date={today}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should get all logs since they were created in the last few hours
    assert data["total_count"] >= 1


@pytest.mark.asyncio
async def test_audit_log_invalid_action(
    client: AsyncClient,
    super_admin: Admin
):
    """Test invalid action filter returns 400."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log?action=INVALID",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Invalid action" in response.json()["detail"]


@pytest.mark.asyncio
async def test_audit_log_invalid_date_format(
    client: AsyncClient,
    super_admin: Admin
):
    """Test invalid date format returns 400."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log?start_date=invalid",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Invalid start_date format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_audit_log_entry_structure(
    client: AsyncClient,
    super_admin: Admin,
    test_audit_logs: list[AuditLog]
):
    """Test audit log entry has correct structure."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/audit-log?limit=1",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    log = data["logs"][0]
    assert "id" in log
    assert "admin_email" in log
    assert "action" in log
    assert "resource_type" in log
    assert "details" in log
    assert "ip_address" in log
    assert "timestamp" in log
    
    assert isinstance(log["details"], dict)
    assert log["admin_email"] == super_admin.email