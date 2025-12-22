"""Admin counselor management router for CRUD operations on categories."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import AdminRole
from app.models.audit_log import AuditAction, AuditLog
from app.models.counselor_category import CounselorCategory
from app.utils.admin_dependencies import get_current_admin, require_admin_role

admin_counselors_router = APIRouter(
    prefix='/api/admin/counselors',
    tags=['admin-counselors']
)


class CategoryResponse(BaseModel):
    """Response schema for counselor category."""
    category_id: str
    name: str
    description: str
    icon: str
    system_prompt: str
    enabled: bool


class CategoryCreateRequest(BaseModel):
    """Request schema for creating counselor category."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    icon: str = Field(..., min_length=1, max_length=10)
    system_prompt: str = Field(..., min_length=1, max_length=5000)
    enabled: bool = True


class CategoryUpdateRequest(BaseModel):
    """Request schema for updating counselor category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    icon: Optional[str] = Field(None, min_length=1, max_length=10)
    system_prompt: Optional[str] = Field(None, min_length=1, max_length=5000)
    enabled: Optional[bool] = None


async def create_audit_log(
    db: AsyncSession,
    admin_id: uuid.UUID,
    action: AuditAction,
    resource_type: str,
    resource_id: Optional[uuid.UUID],
    details: Optional[dict],
    request: Request
) -> None:
    """Create audit log entry for admin action."""
    audit_entry = AuditLog(
        admin_user_id=admin_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=request.client.host if request.client else None
    )
    db.add(audit_entry)


@admin_counselors_router.get('/categories', response_model=list[CategoryResponse])
async def get_all_categories_admin(
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.CONTENT_MANAGER,
        AdminRole.SYSTEM_MONITOR
    )),
    db: AsyncSession = Depends(get_db)
) -> list[CategoryResponse]:
    """
    Get all counselor categories including disabled ones (admin only).
    
    Requires SUPER_ADMIN, CONTENT_MANAGER, or SYSTEM_MONITOR role.
    """
    try:
        # Query all categories (no enabled filter)
        query = select(CounselorCategory).order_by(CounselorCategory.name)
        result = await db.execute(query)
        categories = result.scalars().all()
        
        return [
            CategoryResponse(
                category_id=str(cat.id),
                name=cat.name,
                description=cat.description,
                icon=cat.icon_name,
                system_prompt=cat.system_prompt or '',
                enabled=cat.enabled
            )
            for cat in categories
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to fetch categories: {str(e)}'
        )


@admin_counselors_router.post('/categories', response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreateRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.CONTENT_MANAGER
    )),
    db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    """
    Create new counselor category (CONTENT_MANAGER or SUPER_ADMIN).
    """
    try:
        # Check if category name already exists
        query = select(CounselorCategory).where(CounselorCategory.name == category_data.name)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Category with name "{category_data.name}" already exists'
            )
        
        # Create category
        new_category = CounselorCategory(
            name=category_data.name,
            description=category_data.description,
            icon_name=category_data.icon,
            system_prompt=category_data.system_prompt,
            enabled=category_data.enabled
        )
        
        db.add(new_category)
        
        # Create audit log
        await create_audit_log(
            db=db,
            admin_id=uuid.UUID(current_admin['admin_id']),
            action=AuditAction.CREATE,
            resource_type='CounselorCategory',
            resource_id=new_category.id,
            details={'name': category_data.name},
            request=request
        )
        
        await db.commit()
        await db.refresh(new_category)
        
        return CategoryResponse(
            category_id=str(new_category.id),
            name=new_category.name,
            description=new_category.description,
            icon=new_category.icon_name,
            system_prompt=new_category.system_prompt or '',
            enabled=new_category.enabled
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create category: {str(e)}'
        )


@admin_counselors_router.put('/categories/{category_id}', response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdateRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.CONTENT_MANAGER
    )),
    db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    """
    Update existing counselor category (CONTENT_MANAGER or SUPER_ADMIN).
    """
    try:
        # Validate UUID
        try:
            cat_uuid = uuid.UUID(category_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid category ID format'
            )
        
        # Fetch category
        query = select(CounselorCategory).where(CounselorCategory.id == cat_uuid)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found'
            )
        
        # Track changes for audit log
        changes = {}
        
        # Update fields if provided
        if category_data.name is not None:
            changes['name'] = {'old': category.name, 'new': category_data.name}
            category.name = category_data.name
        if category_data.description is not None:
            changes['description'] = {'old': category.description[:50], 'new': category_data.description[:50]}
            category.description = category_data.description
        if category_data.icon is not None:
            changes['icon'] = {'old': category.icon_name, 'new': category_data.icon}
            category.icon_name = category_data.icon
        if category_data.system_prompt is not None:
            changes['system_prompt_updated'] = True
            category.system_prompt = category_data.system_prompt
        if category_data.enabled is not None:
            changes['enabled'] = {'old': category.enabled, 'new': category_data.enabled}
            category.enabled = category_data.enabled
        
        # Create audit log
        await create_audit_log(
            db=db,
            admin_id=uuid.UUID(current_admin['admin_id']),
            action=AuditAction.UPDATE,
            resource_type='CounselorCategory',
            resource_id=category.id,
            details=changes,
            request=request
        )
        
        await db.commit()
        await db.refresh(category)
        
        return CategoryResponse(
            category_id=str(category.id),
            name=category.name,
            description=category.description,
            icon=category.icon_name,
            system_prompt=category.system_prompt or '',
            enabled=category.enabled
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update category: {str(e)}'
        )


@admin_counselors_router.delete('/categories/{category_id}')
async def disable_category(
    category_id: str,
    request: Request,
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.CONTENT_MANAGER
    )),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Disable counselor category (soft delete by setting enabled=false).
    """
    try:
        # Validate UUID
        try:
            cat_uuid = uuid.UUID(category_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid category ID format'
            )
        
        # Fetch category
        query = select(CounselorCategory).where(CounselorCategory.id == cat_uuid)
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found'
            )
        
        # Soft delete
        category.enabled = False
        
        # Create audit log
        await create_audit_log(
            db=db,
            admin_id=uuid.UUID(current_admin['admin_id']),
            action=AuditAction.DELETE,
            resource_type='CounselorCategory',
            resource_id=category.id,
            details={'name': category.name},
            request=request
        )
        
        await db.commit()
        
        return {'message': 'Category disabled successfully'}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to disable category: {str(e)}'
        )
