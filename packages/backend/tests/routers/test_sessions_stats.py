"""Tests for session statistics endpoint."""
import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.models.session import Session
from app.models.user import User
from app.models.counselor_category import CounselorCategory


class TestGetSessionStats:
    """Tests for GET /api/v1/sessions/stats endpoint."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(
        self, client, test_user, auth_headers
    ):
        """Test stats endpoint with no sessions."""
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 0
        assert data["total_hours"] == 0.0
        assert data["top_category"] is None
        assert data["top_category_icon"] is None
        assert data["last_session_date"] is None

    @pytest.mark.asyncio
    async def test_get_stats_single_session(
        self, client, test_user, test_category, db_session, auth_headers
    ):
        """Test stats with a single session."""
        # Create a session
        session = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="voice",
            room_name=f"test-room-{uuid4()}",
            duration_seconds=1800,  # 30 minutes = 0.5 hours
            started_at=datetime.utcnow() - timedelta(hours=1),
            ended_at=datetime.utcnow()
        )
        db_session.add(session)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 1
        assert data["total_hours"] == 0.5
        assert data["top_category"] == test_category.name
        assert data["top_category_icon"] == test_category.icon_name
        assert data["last_session_date"] is not None

    @pytest.mark.asyncio
    async def test_get_stats_multiple_sessions(
        self, client, test_user, test_category, db_session, auth_headers
    ):
        """Test stats with multiple sessions."""
        # Create 3 sessions with different durations
        sessions = [
            Session(
                user_id=test_user.id,
                counselor_category=test_category.name,
                mode="voice",
                room_name=f"test-room-{uuid4()}",
                duration_seconds=3600,  # 1 hour
                started_at=datetime.utcnow() - timedelta(days=3),
                ended_at=datetime.utcnow() - timedelta(days=3, hours=-1)
            ),
            Session(
                user_id=test_user.id,
                counselor_category=test_category.name,
                mode="video",
                room_name=f"test-room-{uuid4()}",
                duration_seconds=1800,  # 0.5 hours
                started_at=datetime.utcnow() - timedelta(days=2),
                ended_at=datetime.utcnow() - timedelta(days=2, hours=-0.5)
            ),
            Session(
                user_id=test_user.id,
                counselor_category=test_category.name,
                mode="voice",
                room_name=f"test-room-{uuid4()}",
                duration_seconds=5400,  # 1.5 hours
                started_at=datetime.utcnow() - timedelta(days=1),
                ended_at=datetime.utcnow() - timedelta(days=1, hours=-1.5)
            ),
        ]
        
        for session in sessions:
            db_session.add(session)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 3
        assert data["total_hours"] == 3.0  # 1 + 0.5 + 1.5
        assert data["top_category"] == test_category.name

    @pytest.mark.asyncio
    async def test_get_stats_top_category(
        self, client, test_user, db_session, auth_headers
    ):
        """Test that top category is correctly identified."""
        # Create two categories
        category1 = CounselorCategory(
            name="Anxiety Support",
            description="Help with anxiety",
            icon_name="😰",
            system_prompt="You help with anxiety",
            enabled=True
        )
        category2 = CounselorCategory(
            name="Career Guidance",
            description="Career advice",
            icon_name="💼",
            system_prompt="You provide career guidance",
            enabled=True
        )
        db_session.add(category1)
        db_session.add(category2)
        await db_session.commit()
        
        # Create 3 sessions for category1 and 1 for category2
        for i in range(3):
            session = Session(
                user_id=test_user.id,
                counselor_category=category1.name,
                mode="voice",
                room_name=f"test-room-cat1-{i}",
                duration_seconds=1800,
                started_at=datetime.utcnow() - timedelta(hours=1),
                ended_at=datetime.utcnow()
            )
            db_session.add(session)
        
        session = Session(
            user_id=test_user.id,
            counselor_category=category2.name,
            mode="video",
            room_name=f"test-room-cat2",
            duration_seconds=1800,
            started_at=datetime.utcnow() - timedelta(hours=1),
            ended_at=datetime.utcnow()
        )
        db_session.add(session)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 4
        assert data["top_category"] == category1.name
        assert data["top_category_icon"] == category1.icon_name

    @pytest.mark.asyncio
    async def test_get_stats_excludes_deleted(
        self, client, test_user, test_category, db_session, auth_headers
    ):
        """Test that deleted sessions are excluded from stats."""
        # Create 2 active sessions and 1 deleted
        active1 = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="voice",
            room_name=f"test-room-active1-{uuid4()}",
            duration_seconds=3600,
            started_at=datetime.utcnow() - timedelta(days=2),
            ended_at=datetime.utcnow() - timedelta(days=2, hours=-1)
        )
        active2 = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="video",
            room_name=f"test-room-active2-{uuid4()}",
            duration_seconds=3600,
            started_at=datetime.utcnow() - timedelta(days=1),
            ended_at=datetime.utcnow() - timedelta(days=1, hours=-1)
        )
        deleted = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="voice",
            room_name=f"test-room-deleted-{uuid4()}",
            duration_seconds=3600,
            started_at=datetime.utcnow() - timedelta(days=3),
            ended_at=datetime.utcnow() - timedelta(days=3, hours=-1),
            deleted_at=datetime.utcnow()
        )
        
        db_session.add(active1)
        db_session.add(active2)
        db_session.add(deleted)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 2
        assert data["total_hours"] == 2.0

    @pytest.mark.asyncio
    async def test_get_stats_user_isolation(
        self, client, test_user, test_category, db_session, auth_headers
    ):
        """Test that stats only include authenticated user's sessions."""
        # Create another user
        other_user = User(
            email="other@example.com",
            hashed_password="hashedpass",
            first_name="Other",
            last_name="User"
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create sessions for both users
        test_user_session = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="voice",
            room_name=f"test-room-user1-{uuid4()}",
            duration_seconds=3600,
            started_at=datetime.utcnow() - timedelta(hours=1),
            ended_at=datetime.utcnow()
        )
        other_user_session = Session(
            user_id=other_user.id,
            counselor_category=test_category.name,
            mode="video",
            room_name=f"test-room-user2-{uuid4()}",
            duration_seconds=3600,
            started_at=datetime.utcnow() - timedelta(hours=1),
            ended_at=datetime.utcnow()
        )
        
        db_session.add(test_user_session)
        db_session.add(other_user_session)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 1
        assert data["total_hours"] == 1.0

    @pytest.mark.asyncio
    async def test_get_stats_unauthorized(self, client):
        """Test that stats endpoint requires authentication."""
        response = await client.get("/api/v1/sessions/stats")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_stats_last_session_date(
        self, client, test_user, test_category, db_session, auth_headers
    ):
        """Test that last_session_date is the most recent session."""
        # Create sessions at different times
        old_session = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="voice",
            room_name=f"test-room-old-{uuid4()}",
            duration_seconds=1800,
            started_at=datetime.utcnow() - timedelta(days=10),
            ended_at=datetime.utcnow() - timedelta(days=10, hours=-0.5)
        )
        recent_session = Session(
            user_id=test_user.id,
            counselor_category=test_category.name,
            mode="video",
            room_name=f"test-room-recent-{uuid4()}",
            duration_seconds=1800,
            started_at=datetime.utcnow() - timedelta(hours=2),
            ended_at=datetime.utcnow() - timedelta(hours=1.5)
        )
        
        db_session.add(old_session)
        db_session.add(recent_session)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/sessions/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Parse dates and compare
        last_date = datetime.fromisoformat(data["last_session_date"].replace('Z', '+00:00'))
        recent_start = recent_session.started_at
        
        # Should be within 1 second (account for microsecond differences)
        assert abs((last_date.replace(tzinfo=None) - recent_start).total_seconds()) < 1
