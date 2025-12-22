"""Tests for session endpoints."""
import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.user import User


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
    """Create authentication headers for test_user_with_auth."""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(user_id=test_user_with_auth.id, username=test_user_with_auth.username)
    return {"Authorization": f"Bearer {token}"}


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
        headers=auth_headers_for_user
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
        headers=auth_headers_for_user
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
        headers=auth_headers_for_user
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
        headers=auth_headers_for_user
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Session already ended"


@pytest.mark.asyncio
async def test_get_sessions(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
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
        headers=auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all("counselor_category" in s for s in data)
    assert all("mode" in s for s in data)


@pytest.mark.asyncio
async def test_get_sessions_filtered_by_mode(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
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
        headers=auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(s["mode"] == "voice" for s in data)


@pytest.mark.asyncio
async def test_get_sessions_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
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
        headers=auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


@pytest.mark.asyncio
async def test_get_session_details(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user_with_auth: User,
    auth_headers_for_user: dict
):
    """Test retrieving detailed session information."""
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
        headers=auth_headers_for_user
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == str(session_id)
    assert data["counselor_category"] == "Health"
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
        headers=auth_headers_for_user
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
        headers=auth_headers_for_user
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
        headers=auth_headers_for_user
    )
    assert response.status_code == 422  # Validation error


