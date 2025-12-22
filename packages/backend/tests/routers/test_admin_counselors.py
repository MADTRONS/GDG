"""Tests for admin counselor management endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.admin import Admin, AdminRole
from app.models.audit_log import AuditLog, AuditAction
from app.models.counselor_category import CounselorCategory
from app.utils.admin_jwt import create_admin_access_token


@pytest_asyncio.fixture
async def super_admin(db_session: AsyncSession) -> Admin:
    """Create a test super admin."""
    from app.utils.security import hash_password
    
    admin = Admin(
        email='super@test.com',
        password_hash=hash_password('SuperPass123!'),
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
    from app.utils.security import hash_password
    
    admin = Admin(
        email='content@test.com',
        password_hash=hash_password('ContentPass123!'),
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
    from app.utils.security import hash_password
    
    admin = Admin(
        email='monitor@test.com',
        password_hash=hash_password('MonitorPass123!'),
        role=AdminRole.SYSTEM_MONITOR,
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
        name='Test Health',
        description='Test health counselor description',
        icon_name='heart',
        system_prompt='You are a test health counselor.',
        enabled=True
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.mark.asyncio
async def test_get_all_categories_admin(client: AsyncClient, super_admin: Admin, test_category: CounselorCategory):
    """Test getting all categories including disabled ones."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    response = await client.get(
        '/api/admin/counselors/categories',
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check test category is present
    test_cat = next((c for c in data if c['name'] == 'Test Health'), None)
    assert test_cat is not None
    assert test_cat['description'] == 'Test health counselor description'
    assert test_cat['icon'] == 'heart'
    assert test_cat['enabled'] is True


@pytest.mark.asyncio
async def test_get_categories_unauthorized(client: AsyncClient):
    """Test getting categories without authentication fails."""
    response = await client.get('/api/admin/counselors/categories')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_category_success(
    client: AsyncClient,
    super_admin: Admin,
    db_session: AsyncSession
):
    """Test creating a new counselor category."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    new_category_data = {
        'name': 'New Career',
        'description': 'Career counseling support',
        'icon': 'briefcase',
        'system_prompt': 'You are a career counselor.',
        'enabled': True
    }
    
    response = await client.post(
        '/api/admin/counselors/categories',
        json=new_category_data,
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'New Career'
    assert data['description'] == 'Career counseling support'
    assert data['icon'] == 'briefcase'
    assert data['enabled'] is True
    assert 'category_id' in data
    
    # Verify audit log was created
    query = select(AuditLog).where(
        AuditLog.admin_user_id == super_admin.id,
        AuditLog.action == AuditAction.CREATE,
        AuditLog.resource_type == 'CounselorCategory'
    )
    result = await db_session.execute(query)
    audit_log = result.scalar_one_or_none()
    assert audit_log is not None
    assert audit_log.details['name'] == 'New Career'


@pytest.mark.asyncio
async def test_create_category_duplicate_name(
    client: AsyncClient,
    super_admin: Admin,
    test_category: CounselorCategory
):
    """Test creating category with duplicate name fails."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    duplicate_data = {
        'name': 'Test Health',  # Same as test_category
        'description': 'Another description',
        'icon': 'health',
        'system_prompt': 'System prompt',
        'enabled': True
    }
    
    response = await client.post(
        '/api/admin/counselors/categories',
        json=duplicate_data,
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 400
    assert 'already exists' in response.json()['detail']


@pytest.mark.asyncio
async def test_create_category_system_monitor_forbidden(
    client: AsyncClient,
    system_monitor: Admin
):
    """Test system monitor cannot create categories."""
    token = create_admin_access_token(system_monitor.id, system_monitor.email, system_monitor.role.value)
    
    new_category_data = {
        'name': 'Unauthorized Category',
        'description': 'Should fail',
        'icon': 'cross',
        'system_prompt': 'Test',
        'enabled': True
    }
    
    response = await client.post(
        '/api/admin/counselors/categories',
        json=new_category_data,
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_category_success(
    client: AsyncClient,
    content_manager: Admin,
    test_category: CounselorCategory,
    db_session: AsyncSession
):
    """Test updating an existing category."""
    token = create_admin_access_token(content_manager.id, content_manager.email, content_manager.role.value)
    
    update_data = {
        'name': 'Updated Health',
        'description': 'Updated description',
        'enabled': False
    }
    
    response = await client.put(
        f'/api/admin/counselors/categories/{test_category.id}',
        json=update_data,
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Updated Health'
    assert data['description'] == 'Updated description'
    assert data['enabled'] is False
    
    # Verify audit log
    query = select(AuditLog).where(
        AuditLog.admin_user_id == content_manager.id,
        AuditLog.action == AuditAction.UPDATE,
        AuditLog.resource_id == test_category.id
    )
    result = await db_session.execute(query)
    audit_log = result.scalar_one_or_none()
    assert audit_log is not None


@pytest.mark.asyncio
async def test_update_category_not_found(
    client: AsyncClient,
    super_admin: Admin
):
    """Test updating non-existent category fails."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    fake_uuid = '00000000-0000-0000-0000-000000000000'
    response = await client.put(
        f'/api/admin/counselors/categories/{fake_uuid}',
        json={'name': 'Updated'},
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_category_invalid_uuid(
    client: AsyncClient,
    super_admin: Admin
):
    """Test updating with invalid UUID fails."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    response = await client.put(
        '/api/admin/counselors/categories/invalid-uuid',
        json={'name': 'Updated'},
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_disable_category_success(
    client: AsyncClient,
    super_admin: Admin,
    test_category: CounselorCategory,
    db_session: AsyncSession
):
    """Test disabling a category (soft delete)."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    response = await client.delete(
        f'/api/admin/counselors/categories/{test_category.id}',
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 200
    assert 'disabled' in response.json()['message'].lower()
    
    # Verify category is disabled in database
    await db_session.refresh(test_category)
    assert test_category.enabled is False
    
    # Verify audit log
    query = select(AuditLog).where(
        AuditLog.admin_user_id == super_admin.id,
        AuditLog.action == AuditAction.DELETE,
        AuditLog.resource_id == test_category.id
    )
    result = await db_session.execute(query)
    audit_log = result.scalar_one_or_none()
    assert audit_log is not None
    assert audit_log.details['name'] == test_category.name


@pytest.mark.asyncio
async def test_disable_category_not_found(
    client: AsyncClient,
    super_admin: Admin
):
    """Test disabling non-existent category fails."""
    token = create_admin_access_token(super_admin.id, super_admin.email, super_admin.role.value)
    
    fake_uuid = '00000000-0000-0000-0000-000000000000'
    response = await client.delete(
        f'/api/admin/counselors/categories/{fake_uuid}',
        cookies={'admin_token': token}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_content_manager_can_manage_categories(
    client: AsyncClient,
    content_manager: Admin
):
    """Test that content manager has full CRUD access."""
    token = create_admin_access_token(content_manager.id, content_manager.email, content_manager.role.value)
    
    # GET should work
    response = await client.get(
        '/api/admin/counselors/categories',
        cookies={'admin_token': token}
    )
    assert response.status_code == 200
    
    # POST should work
    response = await client.post(
        '/api/admin/counselors/categories',
        json={
            'name': 'CM Test Category',
            'description': 'Test',
            'icon': 'pencil',
            'system_prompt': 'Test prompt',
            'enabled': True
        },
        cookies={'admin_token': token}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_system_monitor_read_only(
    client: AsyncClient,
    system_monitor: Admin,
    test_category: CounselorCategory
):
    """Test that system monitor can only read, not modify."""
    token = create_admin_access_token(system_monitor.id, system_monitor.email, system_monitor.role.value)
    
    # GET should work
    response = await client.get(
        '/api/admin/counselors/categories',
        cookies={'admin_token': token}
    )
    assert response.status_code == 200
    
    # POST should fail
    response = await client.post(
        '/api/admin/counselors/categories',
        json={
            'name': 'Monitor Test',
            'description': 'Test',
            'icon': 'eye',
            'system_prompt': 'Test',
            'enabled': True
        },
        cookies={'admin_token': token}
    )
    assert response.status_code == 403
    
    # PUT should fail
    response = await client.put(
        f'/api/admin/counselors/categories/{test_category.id}',
        json={'name': 'Updated'},
        cookies={'admin_token': token}
    )
    assert response.status_code == 403
    
    # DELETE should fail
    response = await client.delete(
        f'/api/admin/counselors/categories/{test_category.id}',
        cookies={'admin_token': token}
    )
    assert response.status_code == 403
