"""Tests for counselor repository."""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.counselor_repository import CounselorRepository
from app.models.counselor_category import CounselorCategory


async def seed_categories(session: AsyncSession):
    """Seed test categories."""
    categories = [
        CounselorCategory(
            name="Health",
            description="Mental health support",
            icon_name="heart-pulse",
            enabled=True
        ),
        CounselorCategory(
            name="Career",
            description="Career guidance",
            icon_name="briefcase",
            enabled=True
        ),
        CounselorCategory(
            name="Academic",
            description="Academic help",
            icon_name="graduation-cap",
            enabled=True
        ),
        CounselorCategory(
            name="Financial",
            description="Financial advice",
            icon_name="dollar-sign",
            enabled=True
        ),
        CounselorCategory(
            name="Social",
            description="Social support",
            icon_name="users",
            enabled=True
        ),
        CounselorCategory(
            name="Personal Development",
            description="Personal growth",
            icon_name="star",
            enabled=True
        ),
    ]
    session.add_all(categories)
    await session.commit()


@pytest.mark.asyncio
class TestCounselorRepository:
    """Test cases for CounselorRepository."""
    
    async def test_get_enabled_categories_returns_only_enabled(
        self, db_session: AsyncSession
    ):
        """Test that get_enabled_categories returns only enabled categories."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        
        # Disable one category for testing
        stmt = select(CounselorCategory).where(CounselorCategory.name == "Health")
        result = await db_session.execute(stmt)
        health = result.scalar_one_or_none()
        if health:
            health.enabled = False
            await db_session.commit()
        
        # Act
        categories = await repo.get_enabled_categories()
        
        # Assert
        assert len(categories) == 5  # 6 seeded minus 1 disabled
        assert all(cat.enabled for cat in categories)
        assert not any(cat.name == "Health" for cat in categories)
    
    async def test_get_enabled_categories_alphabetical_order(
        self, db_session: AsyncSession
    ):
        """Test that categories are returned in alphabetical order."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        
        # Act
        categories = await repo.get_enabled_categories()
        
        # Assert
        category_names = [cat.name for cat in categories]
        assert category_names == sorted(category_names)
    
    async def test_get_enabled_categories_returns_all_fields(
        self, db_session: AsyncSession
    ):
        """Test that all required fields are returned."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        
        # Act
        categories = await repo.get_enabled_categories()
        
        # Assert
        assert len(categories) > 0
        first_cat = categories[0]
        assert hasattr(first_cat, "id")
        assert hasattr(first_cat, "name")
        assert hasattr(first_cat, "description")
        assert hasattr(first_cat, "icon_name")
        assert hasattr(first_cat, "enabled")
        assert first_cat.id is not None
        assert first_cat.name
        assert first_cat.description
        assert first_cat.icon_name
    
    async def test_get_by_id_returns_correct_category(
        self, db_session: AsyncSession
    ):
        """Test that get_by_id returns the correct category."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        categories = await repo.get_enabled_categories()
        test_id = categories[0].id
        
        # Act
        category = await repo.get_by_id(test_id)
        
        # Assert
        assert category is not None
        assert category.id == test_id
        assert category.name == categories[0].name
    
    async def test_get_by_id_returns_none_for_invalid_id(
        self, db_session: AsyncSession
    ):
        """Test that get_by_id returns None for non-existent ID."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        invalid_id = uuid4()
        
        # Act
        category = await repo.get_by_id(invalid_id)
        
        # Assert
        assert category is None
    
    async def test_get_all_categories_includes_disabled(
        self, db_session: AsyncSession
    ):
        """Test that get_all_categories returns both enabled and disabled."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        
        # Disable one category
        stmt = select(CounselorCategory).where(CounselorCategory.name == "Health")
        result = await db_session.execute(stmt)
        health = result.scalar_one_or_none()
        if health:
            health.enabled = False
            await db_session.commit()
        
        # Act
        categories = await repo.get_all_categories()
        
        # Assert
        assert len(categories) == 6  # All seeded categories
        disabled_cats = [cat for cat in categories if not cat.enabled]
        assert len(disabled_cats) == 1
        assert disabled_cats[0].name == "Health"
    
    async def test_get_all_categories_alphabetical_order(
        self, db_session: AsyncSession
    ):
        """Test that all categories are returned in alphabetical order."""
        # Arrange
        await seed_categories(db_session)
        repo = CounselorRepository(db_session)
        
        # Act
        categories = await repo.get_all_categories()
        
        # Assert
        category_names = [cat.name for cat in categories]
        assert category_names == sorted(category_names)
