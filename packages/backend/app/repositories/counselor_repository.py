"""Counselor repository for data access operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.models.counselor_category import CounselorCategory


class CounselorRepository:
    """Repository for counselor category data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_enabled_categories(self) -> List[CounselorCategory]:
        """
        Retrieve all enabled counselor categories, ordered by name.

        Returns:
            List of CounselorCategory objects
        """
        stmt = (
            select(CounselorCategory)
            .where(CounselorCategory.enabled == True)
            .order_by(CounselorCategory.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: uuid.UUID) -> CounselorCategory | None:
        """
        Retrieve a counselor category by ID.

        Args:
            category_id: UUID of the category

        Returns:
            CounselorCategory object or None
        """
        stmt = select(CounselorCategory).where(CounselorCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_categories(self) -> List[CounselorCategory]:
        """
        Retrieve all counselor categories (including disabled), ordered by name.

        Returns:
            List of CounselorCategory objects
        """
        stmt = select(CounselorCategory).order_by(CounselorCategory.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
