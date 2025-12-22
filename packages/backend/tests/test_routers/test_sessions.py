"""Tests for session endpoints."""
import uuid
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.user import User
from app.models.counselor_category import CounselorCategory


@pytest_asyncio.fixture
async def test_user_with_auth(db_session: AsyncSession):
    """Create a test user for session tests."""
    from app.utils.security import hash_password
    
    user = User(
        username=r'\COLLEGE\testuser',
        password_hash=hash_password('testpassword'),
        is_blocked=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_for_user(test_user_with_auth: User) -> dict:
    """Create authentication cookies for test_user_with_auth."""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(user_id=test_user_with_auth.id, username=test_user_with_auth.username)
    # Auth uses cookies, not headers
    return {"cookies": {"access_token": token}}


@pytest.mark.asyncio
async def test_save_session_success(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test saving a session successfully."""
    # Create a test session
    session_id = uuid.uuid4()
    test_session = Session(
        id=session_id,
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow()
    )
    db_session.add(test_session)
    await db_session.commit()
    
    # Save the session
    response = await client.post(
        "/api/v1/sessions/save",
        json={
            "session_id": str(session_id),
            "transcript": [
                {"timestamp": "2025-12-22T14:30:00Z", "speaker": "user", "text": "Hello"},
                {"timestamp": "2025-12-22T14:30:05Z", "speaker": "bot", "text": "Hi there"}
            ],
            "duration": 300,
            "crisis_detected": False
        },
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["session_id"] == str(session_id)
    assert data["message"] == "Session saved successfully"


@pytest.mark.asyncio
async def test_save_session_unauthorized(client: AsyncClient):
    """Test saving session without authentication."""
    response = await client.post(
        "/api/v1/sessions/save",
        json={
            "session_id": str(uuid.uuid4()),
            "transcript": [],
            "duration": 0
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_save_session_not_found(
    client: AsyncClient,
    auth_headers_for_user: dict
):
    """Test saving a non-existent session."""
    response = await client.post(
        "/api/v1/sessions/save",
        json={
            "session_id": str(uuid.uuid4()),
            "transcript": [],
            "duration": 0
        },
        **auth_headers_for_user
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


@pytest.mark.asyncio
async def test_save_session_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test saving another user's session."""
    # Create another user
    other_user = User(
        id=uuid.uuid4(),
        username=r"\COLLEGE\otheruser",
        password_hash="hashed"
    )
    db_session.add(other_user)
    await db_session.commit()
    
    # Create session for other user
    session_id = uuid.uuid4()
    other_session = Session(
        id=session_id,
        user_id=other_user.id,
        counselor_category="Career",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow()
    )
    db_session.add(other_session)
    await db_session.commit()
    
    # Try to save other user's session
    response = await client.post(
        "/api/v1/sessions/save",
        json={
            "session_id": str(session_id),
            "transcript": [],
            "duration": 0
        },
        **auth_headers_for_user
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to save this session"


@pytest.mark.asyncio
async def test_save_session_already_ended(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test saving a session that's already ended."""
    # Create a session that's already ended
    session_id = uuid.uuid4()
    test_session = Session(
        id=session_id,
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300
    )
    db_session.add(test_session)
    await db_session.commit()
    
    response = await client.post(
        "/api/v1/sessions/save",
        json={
            "session_id": str(session_id),
            "transcript": [],
            "duration": 300
        },
        **auth_headers_for_user
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Session already ended"


@pytest.mark.asyncio
async def test_get_sessions(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test retrieving user's sessions."""
    # Create multiple sessions
    sessions = []
    for i, category in enumerate(["Health", "Career", "Academic"]):
        session = Session(
            id=uuid.uuid4(),
            user_id=test_user_with_auth.id,
            counselor_category=category,
            mode="voice" if i % 2 == 0 else "video",
            room_name=f"test-room-{i}",
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            duration_seconds=300 + i * 60
        )
        sessions.append(session)
        db_session.add(session)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert len(data["sessions"]) >= 3
    assert all("counselor_category" in s for s in data["sessions"])
    assert all("mode" in s for s in data["sessions"])


@pytest.mark.asyncio
async def test_get_sessions_filtered_by_mode(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test filtering sessions by mode."""
    # Create voice and video sessions
    voice_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"voice-room-{uuid.uuid4()}",
        started_at=datetime.utcnow()
    )
    video_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Career",
        mode="video",
        room_name=f"video-room-{uuid.uuid4()}",
        started_at=datetime.utcnow()
    )
    db_session.add_all([voice_session, video_session])
    await db_session.commit()
    
    # Filter by voice
    response = await client.get(
        "/api/v1/sessions/?mode=voice",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(s["mode"] == "voice" for s in data["sessions"])


@pytest.mark.asyncio
async def test_get_sessions_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test session pagination."""
    # Create many sessions
    for i in range(10):
        session = Session(
            id=uuid.uuid4(),
            user_id=test_user_with_auth.id,
            counselor_category="Health",
            mode="voice",
            room_name=f"test-room-{i}-{uuid.uuid4()}",
            started_at=datetime.utcnow()
        )
        db_session.add(session)
    await db_session.commit()
    
    # Get first page
    response = await client.get(
        "/api/v1/sessions/?limit=5&offset=0",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) <= 5


@pytest.mark.asyncio
async def test_get_session_details(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test retrieving detailed session information."""
    # First create counselor category
    from app.models.counselor_category import CounselorCategory
    category = CounselorCategory(
        name='Health',
        description='Health counseling',
        icon_name='heart-pulse',
        enabled=True
    )
    db_session.add(category)
    await db_session.commit()
    
    # Create a session with transcript
    session_id = uuid.uuid4()
    test_session = Session(
        id=session_id,
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300,
        transcript=[
            {"timestamp": "2025-12-22T14:30:00Z", "speaker": "user", "text": "Hello"},
            {"timestamp": "2025-12-22T14:30:05Z", "speaker": "bot", "text": "Hi"}
        ],
        crisis_detected=False
    )
    db_session.add(test_session)
    await db_session.commit()
    
    response = await client.get(
        f"/api/v1/sessions/{session_id}",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == str(session_id)
    assert data["counselor_category"] == "Health"
    assert data["counselor_icon"] == "heart-pulse"
    assert data["transcript"] is not None
    assert len(data["transcript"]) == 2


@pytest.mark.asyncio
async def test_get_session_details_not_found(
    client: AsyncClient,
    auth_headers_for_user: dict
):
    """Test getting details of non-existent session."""
    response = await client.get(
        f"/api/v1/sessions/{uuid.uuid4()}",
        **auth_headers_for_user
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_session_details_not_owner(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test getting details of another user's session."""
    # Create counselor category
    from app.models.counselor_category import CounselorCategory
    category = CounselorCategory(
        name='Career',
        description='Career counseling',
        icon_name='briefcase',
        enabled=True
    )
    db_session.add(category)
    await db_session.commit()
    
    # Create another user and their session
    other_user = User(
        id=uuid.uuid4(),
        username=r"\COLLEGE\otheruser",
        password_hash="hashed"
    )
    db_session.add(other_user)
    await db_session.commit()
    
    session_id = uuid.uuid4()
    other_session = Session(
        id=session_id,
        user_id=other_user.id,
        counselor_category="Career",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow()
    )
    db_session.add(other_session)
    await db_session.commit()
    
    response = await client.get(
        f"/api/v1/sessions/{session_id}",
        **auth_headers_for_user
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_save_session_invalid_speaker(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test saving session with invalid speaker value."""
    session_id = uuid.uuid4()
    test_session = Session(
        id=session_id,
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow()
    )
    db_session.add(test_session)
    await db_session.commit()
    
    response = await client.post(
        "/api/v1/sessions/save",
        json={
            "session_id": str(session_id),
            "transcript": [
                {"timestamp": "2025-12-22T14:30:00Z", "speaker": "invalid", "text": "Hello"}
            ],
            "duration": 300
        },
        **auth_headers_for_user
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# Story 5.2 Tests: Backend Session History API with Filters and Pagination
# ============================================================================

@pytest_asyncio.fixture
async def test_counselor_categories(db_session: AsyncSession):
    """Create test counselor categories."""
    categories = [
        CounselorCategory(
            name="Health",
            description="Health and wellness counseling",
            icon_name="health-icon",
            enabled=True
        ),
        CounselorCategory(
            name="Career",
            description="Career guidance and planning",
            icon_name="career-icon",
            enabled=True
        ),
        CounselorCategory(
            name="Academic",
            description="Academic support and tutoring",
            icon_name="academic-icon",
            enabled=True
        )
    ]
    for cat in categories:
        db_session.add(cat)
    await db_session.commit()
    for cat in categories:
        await db_session.refresh(cat)
    return categories


@pytest.mark.asyncio
async def test_get_sessions_with_pagination_metadata(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test that endpoint returns pagination metadata."""
    # Create 5 sessions
    for i in range(5):
        session = Session(
            id=uuid.uuid4(),
            user_id=test_user_with_auth.id,
            counselor_category="Health",
            mode="voice",
            room_name=f"test-room-{i}-{uuid.uuid4()}",
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            duration_seconds=300
        )
        db_session.add(session)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/sessions/?page=1&limit=3",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert data["page"] == 1
    assert data["limit"] == 3
    assert data["total_count"] >= 5
    assert len(data["sessions"]) <= 3


@pytest.mark.asyncio
async def test_get_sessions_requires_authentication(client: AsyncClient):
    """Test that endpoint requires authentication."""
    response = await client.get("/api/v1/sessions/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_sessions_only_returns_user_sessions(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test that users only see their own sessions."""
    from app.utils.security import hash_password
    
    # Create another user
    other_user = User(
        username=r'\COLLEGE\otheruser',
        password_hash=hash_password('password'),
        is_blocked=False
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    
    # Create sessions for both users
    session1 = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-1-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300,
        transcript=[{"timestamp": "2025-12-22T14:30:00Z", "speaker": "user", "text": "Test user session"}]
    )
    session2 = Session(
        id=uuid.uuid4(),
        user_id=other_user.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-2-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300,
        transcript=[{"timestamp": "2025-12-22T14:30:00Z", "speaker": "user", "text": "Other user session"}]
    )
    db_session.add_all([session1, session2])
    await db_session.commit()
    
    # test_user should only see their session
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["session_id"] == str(session1.id)


@pytest.mark.asyncio
async def test_filter_by_category(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test filtering sessions by counselor category."""
    # Create sessions for different categories
    health_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"health-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300
    )
    career_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Career",
        mode="voice",
        room_name=f"career-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300
    )
    db_session.add_all([health_session, career_session])
    await db_session.commit()
    
    # Filter by Health category
    response = await client.get(
        "/api/v1/sessions/?category=Health",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["counselor_category"] == "Health"


@pytest.mark.asyncio
async def test_filter_by_mode(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test filtering sessions by mode (voice/video)."""
    # Create voice and video sessions
    voice_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"voice-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300
    )
    video_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="video",
        room_name=f"video-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300
    )
    db_session.add_all([voice_session, video_session])
    await db_session.commit()
    
    # Filter by video mode
    response = await client.get(
        "/api/v1/sessions/?mode=video",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(s["mode"] == "video" for s in data["sessions"])


@pytest.mark.asyncio
async def test_filter_by_date_range(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test filtering sessions by date range."""
    now = datetime.utcnow()
    
    # Create sessions at different times
    old_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"old-room-{uuid.uuid4()}",
        started_at=now - timedelta(days=10),
        ended_at=now - timedelta(days=10),
        duration_seconds=300
    )
    recent_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"recent-room-{uuid.uuid4()}",
        started_at=now - timedelta(days=2),
        ended_at=now - timedelta(days=2),
        duration_seconds=300
    )
    db_session.add_all([old_session, recent_session])
    await db_session.commit()
    
    # Filter sessions from last 5 days
    start_date = (now - timedelta(days=5)).isoformat()
    response = await client.get(
        f"/api/v1/sessions/?start_date={start_date}",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should only get the recent session
    assert all(
        datetime.fromisoformat(s["started_at"].replace('Z', '+00:00')) >= (now - timedelta(days=5))
        for s in data["sessions"]
    )


@pytest.mark.asyncio
async def test_pagination_works_correctly(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test pagination works correctly."""
    # Create 25 sessions
    for i in range(25):
        session = Session(
            id=uuid.uuid4(),
            user_id=test_user_with_auth.id,
            counselor_category="Health",
            mode="voice",
            room_name=f"test-room-{i}-{uuid.uuid4()}",
            started_at=datetime.utcnow() - timedelta(minutes=i),
            ended_at=datetime.utcnow() - timedelta(minutes=i),
            duration_seconds=300
        )
        db_session.add(session)
    await db_session.commit()
    
    # Page 1
    response = await client.get(
        "/api/v1/sessions/?page=1&limit=20",
        **auth_headers_for_user
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 20
    assert data["total_count"] == 25
    assert data["page"] == 1
    assert data["limit"] == 20
    
    # Page 2
    response = await client.get(
        "/api/v1/sessions/?page=2&limit=20",
        **auth_headers_for_user
    )
    data = response.json()
    assert len(data["sessions"]) == 5
    assert data["page"] == 2
    assert data["total_count"] == 25


@pytest.mark.asyncio
async def test_sessions_sorted_by_date_descending(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test sessions are sorted by started_at descending (newest first)."""
    now = datetime.utcnow()
    
    # Create sessions at different times
    sessions_data = []
    for i in range(5):
        session = Session(
            id=uuid.uuid4(),
            user_id=test_user_with_auth.id,
            counselor_category="Health",
            mode="voice",
            room_name=f"test-room-{i}-{uuid.uuid4()}",
            started_at=now - timedelta(hours=i),
            ended_at=now - timedelta(hours=i),
            duration_seconds=300
        )
        sessions_data.append(session)
        db_session.add(session)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify descending order
    timestamps = [datetime.fromisoformat(s["started_at"].replace('Z', '+00:00')) for s in data["sessions"]]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_transcript_preview_limited_to_100_chars(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test transcript preview is limited to 100 characters."""
    # Create session with long transcript
    long_text = "A" * 200  # 200 character text
    session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300,
        transcript=[
            {"timestamp": "2025-12-22T14:30:00Z", "speaker": "user", "text": long_text}
        ]
    )
    db_session.add(session)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 1
    assert len(data["sessions"][0]["transcript_preview"]) == 100


@pytest.mark.asyncio
async def test_response_includes_counselor_icon(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test response includes counselor category name and icon."""
    session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"test-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300
    )
    db_session.add(session)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["counselor_category"] == "Health"
    assert data["sessions"][0]["counselor_icon"] == "health-icon"


@pytest.mark.asyncio
async def test_soft_deleted_sessions_excluded(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test that soft-deleted sessions are excluded from results."""
    # Create active and deleted sessions
    active_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"active-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300,
        deleted_at=None
    )
    deleted_session = Session(
        id=uuid.uuid4(),
        user_id=test_user_with_auth.id,
        counselor_category="Health",
        mode="voice",
        room_name=f"deleted-room-{uuid.uuid4()}",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        duration_seconds=300,
        deleted_at=datetime.utcnow()
    )
    db_session.add_all([active_session, deleted_session])
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["sessions"][0]["session_id"] == str(active_session.id)


@pytest.mark.asyncio
async def test_invalid_date_format_returns_400(
    client: AsyncClient,
    auth_headers_for_user: dict
):
    """Test that invalid date format returns 400."""
    response = await client.get(
        "/api/v1/sessions/?start_date=invalid-date",
        **auth_headers_for_user
    )
    assert response.status_code == 400
    assert "Invalid start_date format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_mode_returns_422(
    client: AsyncClient,
    auth_headers_for_user: dict
):
    """Test that invalid mode value returns validation error."""
    response = await client.get(
        "/api/v1/sessions/?mode=invalid",
        **auth_headers_for_user
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_empty_results(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    test_counselor_categories: list[CounselorCategory],
    auth_headers_for_user: dict
):
    """Test endpoint returns empty list when no sessions exist."""
    response = await client.get(
        "/api/v1/sessions/",
        **auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sessions"] == []
    assert data["total_count"] == 0
    assert data["page"] == 1
    assert data["limit"] == 20




