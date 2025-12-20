"""Counselor routes for category and counselor management."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.counselor_repository import CounselorRepository
from app.schemas.counselor import CounselorCategoryResponse, CounselorCategoriesResponse
from app.schemas.user import UserResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix='/counselors', tags=['counselors'])


async def get_counselor_repository(session: AsyncSession = Depends(get_db)) -> CounselorRepository:
    """Dependency for counselor repository."""
    return CounselorRepository(session)


@router.get(
    '/categories',
    response_model=CounselorCategoriesResponse,
    summary='Get all enabled counselor categories',
    description='Retrieve list of available counselor categories for the dashboard.'
)
async def get_categories(
    current_user: UserResponse = Depends(get_current_user),
    repo: CounselorRepository = Depends(get_counselor_repository)
):
    """
    Get all enabled counselor categories.

    Requires authentication.

    Returns:
        List of counselor categories with id, name, description, and icon_name.
    """
    categories = await repo.get_enabled_categories()

    return CounselorCategoriesResponse(
        categories=[CounselorCategoryResponse.model_validate(cat) for cat in categories],
        total=len(categories)
    )
