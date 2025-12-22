"""Repository for session data access."""
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    """Repository for managing session data."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_session(
        self,
        session_id: UUID,
        user_id: UUID,
        counselor_category: str,
        mode: str,
        room_name: str
    ) -> Session:
        """
        Create a new session record.
        
        Args:
            session_id: Unique session identifier
            user_id: User ID
            counselor_category: Category name
            mode: 'voice' or 'video'
            room_name: Daily.co room name
            
        Returns:
            Created session object
        """
        session_obj = Session(
            id=session_id,
            user_id=user_id,
            counselor_category=counselor_category,
            mode=mode,
            room_name=room_name,
            started_at=datetime.utcnow()
        )
        self.session.add(session_obj)
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj
    
    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def update_session_end(
        self,
        session_id: UUID,
        transcript: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ) -> Optional[Session]:
        """Update session when it ends."""
        session_obj = await self.get_by_id(session_id)
        if session_obj:
            session_obj.ended_at = datetime.utcnow()
            if transcript:
                session_obj.transcript = transcript
            if duration_seconds is not None:
                session_obj.duration_seconds = duration_seconds
            await self.session.commit()
            await self.session.refresh(session_obj)
        return session_obj
    
    async def update_session(
        self,
        session_id: UUID,
        ended_at: datetime,
        duration_seconds: int,
        transcript: list[dict[str, Any]],
        crisis_detected: bool
    ) -> Session:
        """
        Update session with end data.
        
        Args:
            session_id: Session UUID
            ended_at: End timestamp
            duration_seconds: Duration in seconds
            transcript: List of transcript messages
            crisis_detected: Whether crisis was detected
            
        Returns:
            Updated session object
        """
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        session_obj = result.scalar_one()
        
        session_obj.ended_at = ended_at
        session_obj.duration_seconds = duration_seconds
        session_obj.transcript = transcript
        session_obj.crisis_detected = crisis_detected
        
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        mode: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Session]:
        """
        Get user's sessions with optional filtering.
        
        Args:
            user_id: User UUID
            mode: Filter by mode ('voice' or 'video')
            limit: Maximum number of sessions to return
            offset: Pagination offset
            
        Returns:
            List of session objects
        """
        query = select(Session).where(Session.user_id == user_id)
        
        if mode:
            query = query.where(Session.mode == mode)
        
        query = query.order_by(Session.started_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

