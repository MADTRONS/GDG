"""Tests for admin user management endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin, AdminRole
from app.utils.admin_jwt import create_admin_access_token
from app.utils.security import hash_password


@pytest_asyncio.fixture
async def super_admin(db_session: AsyncSession) -> Admin:
    """Create a test super admin."""
    admin = Admin(
        email="superadmin@test.com",
        password_hash=hash_password("SuperPass123!"),
        role=AdminRole.SUPER_ADMIN,
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


@pytest.mark.asyncio
async def test_list_admin_users_super_admin(
    client: AsyncClient,
    super_admin: Admin,
    content_manager: Admin
):
    """Test listing admin users as super admin."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.get(
        "/api/admin/users",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 2  # At least super_admin and content_manager
    
    # Verify structure
    for admin in data:
        assert "id" in admin
        assert "email" in admin
        assert "role" in admin
        assert "is_active" in admin
        assert "created_at" in admin


@pytest.mark.asyncio
async def test_list_admin_users_content_manager_forbidden(
    client: AsyncClient,
    content_manager: Admin
):
    """Test content manager cannot list admin users."""
    token = create_admin_access_token(
        content_manager.id,
        content_manager.email,
        content_manager.role.value
    )
    
    response = await client.get(
        "/api/admin/users",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_admin_users_unauthorized(client: AsyncClient):
    """Test listing admin users without authentication fails."""
    response = await client.get("/api/admin/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_admin_user_success(
    client: AsyncClient,
    super_admin: Admin
):
    """Test creating new admin user."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.post(
        "/api/admin/users",
        json={"email": "newadmin@test.com", "role": "CONTENT_MANAGER"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["email"] == "newadmin@test.com"
    assert data["role"] == "CONTENT_MANAGER"
    assert "temporary_password" in data
    assert len(data["temporary_password"]) > 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_admin_user_duplicate_email(
    client: AsyncClient,
    super_admin: Admin,
    content_manager: Admin
):
    """Test creating admin with existing email fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.post(
        "/api/admin/users",
        json={"email": content_manager.email, "role": "SYSTEM_MONITOR"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_admin_user_invalid_role(
    client: AsyncClient,
    super_admin: Admin
):
    """Test creating admin with invalid role fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.post(
        "/api/admin/users",
        json={"email": "test@test.com", "role": "INVALID_ROLE"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Invalid role" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_admin_user_content_manager_forbidden(
    client: AsyncClient,
    content_manager: Admin
):
    """Test content manager cannot create admin users."""
    token = create_admin_access_token(
        content_manager.id,
        content_manager.email,
        content_manager.role.value
    )
    
    response = await client.post(
        "/api/admin/users",
        json={"email": "test@test.com", "role": "CONTENT_MANAGER"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_admin_user_role(
    client: AsyncClient,
    super_admin: Admin,
    content_manager: Admin
):
    """Test updating admin user role."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        f"/api/admin/users/{content_manager.id}",
        json={"role": "SYSTEM_MONITOR"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_update_admin_user_active_status(
    client: AsyncClient,
    super_admin: Admin,
    content_manager: Admin
):
    """Test updating admin user active status."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        f"/api/admin/users/{content_manager.id}",
        json={"is_active": False},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_update_admin_user_invalid_id(
    client: AsyncClient,
    super_admin: Admin
):
    """Test updating admin with invalid ID fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        "/api/admin/users/invalid-id",
        json={"role": "CONTENT_MANAGER"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Invalid admin ID" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_admin_user_not_found(
    client: AsyncClient,
    super_admin: Admin
):
    """Test updating non-existent admin fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.put(
        f"/api/admin/users/{fake_id}",
        json={"role": "CONTENT_MANAGER"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_admin_user(
    client: AsyncClient,
    super_admin: Admin,
    content_manager: Admin
):
    """Test deactivating admin user."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.delete(
        f"/api/admin/users/{content_manager.id}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    assert "deactivated successfully" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_deactivate_self_forbidden(
    client: AsyncClient,
    super_admin: Admin
):
    """Test admin cannot deactivate themselves."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.delete(
        f"/api/admin/users/{super_admin.id}",
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Cannot deactivate your own account" in response.json()["detail"]


@pytest.mark.asyncio
async def test_reset_own_password(
    client: AsyncClient,
    super_admin: Admin
):
    """Test admin can reset their own password."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        "/api/admin/auth/reset-password",
        params={"current_password": "SuperPass123!", "new_password": "NewPassword123!"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    assert "Password reset successful" in response.json()["message"]


@pytest.mark.asyncio
async def test_reset_own_password_wrong_current(
    client: AsyncClient,
    super_admin: Admin
):
    """Test password reset with wrong current password fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        "/api/admin/auth/reset-password",
        params={"current_password": "WrongPassword", "new_password": "NewPassword123!"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_own_password_too_short(
    client: AsyncClient,
    super_admin: Admin
):
    """Test password reset with short password fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        "/api/admin/auth/reset-password",
        params={"current_password": "SuperPass123!", "new_password": "short"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_force_reset_password(
    client: AsyncClient,
    super_admin: Admin,
    content_manager: Admin
):
    """Test super admin can force reset password for other admin."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        f"/api/admin/auth/force-reset-password/{content_manager.id}",
        params={"new_password": "ForcedNewPass123!"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 200
    assert "Password reset successful" in response.json()["message"]


@pytest.mark.asyncio
async def test_force_reset_password_content_manager_forbidden(
    client: AsyncClient,
    content_manager: Admin,
    system_monitor: Admin
):
    """Test content manager cannot force reset passwords."""
    token = create_admin_access_token(
        content_manager.id,
        content_manager.email,
        content_manager.role.value
    )
    
    response = await client.put(
        f"/api/admin/auth/force-reset-password/{system_monitor.id}",
        params={"new_password": "NewPass123!"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_force_reset_password_invalid_id(
    client: AsyncClient,
    super_admin: Admin
):
    """Test force reset with invalid ID fails."""
    token = create_admin_access_token(
        super_admin.id,
        super_admin.email,
        super_admin.role.value
    )
    
    response = await client.put(
        "/api/admin/auth/force-reset-password/invalid-id",
        params={"new_password": "NewPass123!"},
        cookies={"admin_token": token}
    )
    
    assert response.status_code == 400
    assert "Invalid admin ID" in response.json()["detail"]