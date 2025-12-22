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
    
    async def get_user_sessions_with_filters(
        self,
        user_id: UUID,
        category: Optional[str] = None,
        mode: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20
    ) -> tuple[list[tuple[Session, str, str]], int]:
        """
        Get user's sessions with enhanced filtering and pagination.
        Returns sessions with counselor category name and icon.
        
        Args:
            user_id: User UUID
            category: Filter by counselor category name
            mode: Filter by mode ('voice' or 'video')
            start_date: Filter sessions after this date
            end_date: Filter sessions before this date
            page: Page number (1-indexed)
            limit: Results per page
            
        Returns:
            Tuple of (list of (Session, category_name, category_icon), total_count)
        """
        from app.models.counselor_category import CounselorCategory
        from sqlalchemy import and_, func
        
        # Build base query with join
        query = (
            select(Session, CounselorCategory.name, CounselorCategory.icon_name)
            .join(CounselorCategory, Session.counselor_category == CounselorCategory.name)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.deleted_at.is_(None)
                )
            )
        )
        
        # Apply filters
        if category:
            query = query.where(CounselorCategory.name == category)
        
        if mode:
            query = query.where(Session.mode == mode)
        
        if start_date:
            query = query.where(Session.started_at >= start_date)
        
        if end_date:
            query = query.where(Session.started_at <= end_date)
        
        # Get total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar() or 0
        
        # Apply sorting and pagination
        offset = (page - 1) * limit
        query = query.order_by(Session.started_at.desc()).offset(offset).limit(limit)
        
        # Execute query
        result = await self.session.execute(query)
        rows = result.all()
        
        return rows, total_count

