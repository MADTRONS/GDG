"""Tests for counselor router."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.counselor_category import CounselorCategory


async def seed_categories(session: AsyncSession):
    """Seed test categories."""
    categories = [
        CounselorCategory(
            name="Health",
            description="Mental health, stress management, wellness, and self-care support. Get help with anxiety, depression, sleep issues, and maintaining overall well-being.",
            icon_name="heart-pulse",
            enabled=True
        ),
        CounselorCategory(
            name="Career",
            description="Career exploration, job search strategies, resume help, and interview preparation. Plan your professional future with expert guidance.",
            icon_name="briefcase",
            enabled=True
        ),
        CounselorCategory(
            name="Academic",
            description="Study strategies, time management, course selection, and academic planning. Improve your learning effectiveness and achieve academic success.",
            icon_name="graduation-cap",
            enabled=True
        ),
        CounselorCategory(
            name="Financial",
            description="Budgeting, student loans, financial aid, and money management. Build healthy financial habits and navigate college expenses confidently.",
            icon_name="dollar-sign",
            enabled=True
        ),
        CounselorCategory(
            name="Social",
            description="Relationships, communication skills, campus involvement, and social well-being. Navigate friendships, roommate conflicts, and build meaningful connections.",
            icon_name="users",
            enabled=True
        ),
        CounselorCategory(
            name="Personal Development",
            description="Goal setting, self-awareness, life skills, and personal growth. Discover your strengths, values, and create a roadmap for your future.",
            icon_name="star",
            enabled=True
        ),
    ]
    session.add_all(categories)
    await session.commit()


@pytest.mark.asyncio
class TestCounselorRouter:
    """Test cases for counselor router endpoints."""
    
    async def test_get_categories_requires_authentication(self, client: AsyncClient, db_session: AsyncSession):
        """Test that GET /categories requires authentication."""
        # Arrange
        await seed_categories(db_session)
        
        # Act
        response = await client.get("/api/v1/counselors/categories")
        
        # Assert
        assert response.status_code == 401
    
    async def test_get_categories_returns_enabled_categories(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that GET /categories returns enabled categories."""
        # Arrange
        await seed_categories(db_session)
        
        # Act
        response = await authenticated_client.get("/api/v1/counselors/categories")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert data["total"] == 6
        assert len(data["categories"]) == 6
    
    async def test_get_categories_response_structure(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that response has correct structure."""
        # Arrange
        await seed_categories(db_session)
        
        # Act
        response = await authenticated_client.get("/api/v1/counselors/categories")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check each category has required fields
        for category in data["categories"]:
            assert "id" in category
            assert "name" in category
            assert "description" in category
            assert "icon_name" in category
            # These fields should NOT be in the response
            assert "enabled" not in category
            assert "created_at" not in category
            assert "updated_at" not in category
    
    async def test_get_categories_alphabetical_order(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that categories are returned in alphabetical order."""
        # Arrange
        await seed_categories(db_session)
        
        # Act
        response = await authenticated_client.get("/api/v1/counselors/categories")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        category_names = [cat["name"] for cat in data["categories"]]
        expected_order = [
            "Academic",
            "Career",
            "Financial",
            "Health",
            "Personal Development",
            "Social",
        ]
        assert category_names == expected_order
    
    async def test_get_categories_contains_expected_categories(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that all expected seeded categories are present."""
        # Arrange
        await seed_categories(db_session)
        
        # Act
        response = await authenticated_client.get("/api/v1/counselors/categories")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        category_names = {cat["name"] for cat in data["categories"]}
        expected_names = {
            "Health",
            "Career",
            "Academic",
            "Financial",
            "Social",
            "Personal Development",
        }
        assert category_names == expected_names
    
    async def test_get_categories_has_valid_icon_names(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that all categories have valid icon names."""
        # Arrange
        await seed_categories(db_session)
        
        # Act
        response = await authenticated_client.get("/api/v1/counselors/categories")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        expected_icons = {
            "Health": "heart-pulse",
            "Career": "briefcase",
            "Academic": "graduation-cap",
            "Financial": "dollar-sign",
            "Social": "users",
            "Personal Development": "star",
        }
        
        for category in data["categories"]:
            assert category["icon_name"] == expected_icons[category["name"]]
