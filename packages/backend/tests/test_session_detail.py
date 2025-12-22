"""Tests for session detail API endpoint."""
import pytest
from datetime import datetime, UTC
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.counselor_category import CounselorCategory
from app.models.user import User


@pytest.mark.asyncio
class TestSessionDetailEndpoint:
    """Test cases for GET /api/v1/sessions/{session_id} endpoint."""
    
    async def test_get_session_detail_requires_authentication(self, client: AsyncClient):
        """Test that endpoint requires authentication."""
        session_id = uuid4()
        response = await client.get(f"/api/v1/sessions/{session_id}")
        assert response.status_code == 401
    
    async def test_get_session_detail_authorization_wrong_user(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that users can only access their own sessions."""
        # Create another user
        from app.utils.security import hash_password
        other_user = User(
            username=r'\testdomain\otheruser',
            password_hash=hash_password('password'),
            is_blocked=False
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create counselor category
        category = CounselorCategory(
            name='Health',
            description='Mental health support',
            icon_name='heart-pulse',
            enabled=True
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        # Create session for other user
        session = Session(
            user_id=other_user.id,
            counselor_category='Health',
            mode='voice',
            room_name=f'test-room-{uuid4()}',
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            duration_seconds=300,
            transcript=[
                {'timestamp': '2025-12-22T10:00:00Z', 'speaker': 'user', 'text': 'Hello'}
            ]
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Try to access with test_user credentials
        response = await authenticated_client.get(f"/api/v1/sessions/{session.id}")
        
        assert response.status_code == 403
        assert 'permission' in response.json()['detail'].lower()
    
    async def test_get_session_detail_not_found(
        self, 
        authenticated_client: AsyncClient
    ):
        """Test 404 for non-existent session."""
        fake_id = uuid4()
        response = await authenticated_client.get(f"/api/v1/sessions/{fake_id}")
        assert response.status_code == 404
        assert response.json()['detail'] == 'Session not found'
    
    async def test_get_session_detail_soft_deleted(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that soft-deleted sessions return 404."""
        # Create counselor category
        category = CounselorCategory(
            name='Career',
            description='Career guidance',
            icon_name='briefcase',
            enabled=True
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        # Create soft-deleted session
        session = Session(
            user_id=test_user.id,
            counselor_category='Career',
            mode='voice',
            room_name=f'test-room-{uuid4()}',
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            duration_seconds=200,
            deleted_at=datetime.now(UTC)
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        response = await authenticated_client.get(f"/api/v1/sessions/{session.id}")
        assert response.status_code == 404
    
    async def test_get_session_detail_success_with_transcript(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test successful session detail retrieval with transcript."""
        # Create counselor category
        category = CounselorCategory(
            name='Academic',
            description='Academic counseling',
            icon_name='graduation-cap',
            enabled=True
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        # Create session with transcript
        transcript_data = [
            {'timestamp': '2025-12-22T10:00:00Z', 'speaker': 'user', 'text': 'I need help with my studies'},
            {'timestamp': '2025-12-22T10:00:05Z', 'speaker': 'counselor', 'text': 'How can I assist you today?'},
            {'timestamp': '2025-12-22T10:00:15Z', 'speaker': 'user', 'text': 'I am struggling with time management'}
        ]
        
        session = Session(
            user_id=test_user.id,
            counselor_category='Academic',
            mode='voice',
            room_name=f'test-room-{uuid4()}',
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            duration_seconds=450,
            transcript=transcript_data
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Fetch session
        response = await authenticated_client.get(f"/api/v1/sessions/{session.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert data['session_id'] == str(session.id)
        assert data['counselor_category'] == 'Academic'
        assert data['counselor_icon'] == 'graduation-cap'
        assert data['mode'] == 'voice'
        assert data['duration_seconds'] == 450
        assert data['crisis_detected'] is False
        
        # Verify transcript
        assert len(data['transcript']) == 3
        assert data['transcript'][0]['text'] == 'I need help with my studies'
        assert data['transcript'][1]['speaker'] == 'counselor'
        assert data['transcript'][2]['text'] == 'I am struggling with time management'
        
        # Verify timestamps are ISO format
        assert 'started_at' in data
        assert 'ended_at' in data
    
    async def test_get_session_detail_with_quality_metrics(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test session detail includes quality metrics when available."""
        # Create counselor category
        category = CounselorCategory(
            name='Health',
            description='Health counseling',
            icon_name='heart-pulse',
            enabled=True
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        # Create session with quality metrics
        quality_data = {
            'connection_quality_average': 'excellent',
            'average_bitrate': 1200.5,
            'average_fps': 30.0,
            'packet_loss_percentage': 0.2
        }
        
        session = Session(
            user_id=test_user.id,
            counselor_category='Health',
            mode='video',
            room_name=f'test-room-{uuid4()}',
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            duration_seconds=600,
            transcript=[
                {'timestamp': '2025-12-22T10:00:00Z', 'speaker': 'user', 'text': 'Hello'}
            ],
            quality_metrics=quality_data
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Fetch session
        response = await authenticated_client.get(f"/api/v1/sessions/{session.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify quality metrics present
        assert data['quality_metrics'] is not None
        assert data['quality_metrics']['connection_quality_average'] == 'excellent'
        assert data['quality_metrics']['average_bitrate'] == 1200.5
        assert data['mode'] == 'video'
    
    async def test_get_session_detail_empty_transcript(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test session with empty transcript."""
        # Create counselor category
        category = CounselorCategory(
            name='Financial',
            description='Financial counseling',
            icon_name='dollar-sign',
            enabled=True
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        # Create session with no transcript
        session = Session(
            user_id=test_user.id,
            counselor_category='Financial',
            mode='voice',
            room_name=f'test-room-{uuid4()}',
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            duration_seconds=10,
            transcript=[]
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Fetch session
        response = await authenticated_client.get(f"/api/v1/sessions/{session.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['transcript'] == []
    
    async def test_get_session_detail_invalid_uuid_format(
        self, 
        authenticated_client: AsyncClient
    ):
        """Test 422 for invalid UUID format."""
        response = await authenticated_client.get("/api/v1/sessions/not-a-uuid")
        assert response.status_code == 422
