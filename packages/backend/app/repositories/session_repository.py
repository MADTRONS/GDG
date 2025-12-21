"""Repository for session data access."""
from uuid import UUID
from datetime import datetime
from typing import Optional
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
            mode: ''voice'' or ''video''
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
