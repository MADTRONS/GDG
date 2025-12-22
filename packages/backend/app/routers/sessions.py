"""Session management API endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.session_repository import SessionRepository
from app.schemas.session import (
    SaveSessionRequest,
    SaveSessionResponse,
    SessionSummary,
    SessionDetail
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post(
    "/save",
    response_model=SaveSessionResponse,
    summary="Save session data",
    description="Save session transcript and metadata when session ends."
)
async def save_session(
    request: SaveSessionRequest,
    current_user: dict[str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SaveSessionResponse:
    """
    Save session data including transcript and metadata.
    
    Validates:
    1. Session exists
    2. User owns the session
    3. Session not already ended
    """
    repo = SessionRepository(db)
    
    # Get session
    session = await repo.get_by_id(request.session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify ownership
    if str(session.user_id) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to save this session"
        )
    
    # Check if already ended
    if session.ended_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session already ended"
        )
    
    # Convert transcript to dict format for JSONB
    transcript_data = [msg.model_dump() for msg in request.transcript]
    
    # Update session
    updated_session = await repo.update_session(
        session_id=request.session_id,
        ended_at=datetime.utcnow(),
        duration_seconds=request.duration,
        transcript=transcript_data,
        crisis_detected=request.crisis_detected
    )
    
    return SaveSessionResponse(
        success=True,
        session_id=updated_session.id,
        message="Session saved successfully"
    )


@router.get(
    "/",
    response_model=list[SessionSummary],
    summary="Get user sessions",
    description="Retrieve list of user's past counseling sessions."
)
async def get_sessions(
    mode: Optional[str] = Query(None, description="Filter by mode: 'voice' or 'video'"),
    limit: int = Query(50, ge=1, le=100, description="Max sessions to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: dict[str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[SessionSummary]:
    """
    Get user's session history.
    
    Query params:
    - mode: Filter by 'voice' or 'video' (optional)
    - limit: Max sessions to return (default 50, max 100)
    - offset: Pagination offset (default 0)
    """
    repo = SessionRepository(db)
    
    sessions = await repo.get_user_sessions(
        user_id=UUID(current_user["user_id"]),
        mode=mode,
        limit=limit,
        offset=offset
    )
    
    return [
        SessionSummary(
            session_id=session.id,
            counselor_category=session.counselor_category,
            mode=session.mode,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_seconds=session.duration_seconds,
            crisis_detected=session.crisis_detected
        )
        for session in sessions
    ]


@router.get(
    "/{session_id}",
    response_model=SessionDetail,
    summary="Get session details",
    description="Get full session data including transcript."
)
async def get_session_details(
    session_id: UUID,
    current_user: dict[str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SessionDetail:
    """
    Get full session details including transcript.
    Used in Epic 5 Session History page.
    """
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify ownership
    if str(session.user_id) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this session"
        )
    
    return SessionDetail(
        session_id=session.id,
        counselor_category=session.counselor_category,
        mode=session.mode,
        started_at=session.started_at.isoformat(),
        ended_at=session.ended_at.isoformat() if session.ended_at else None,
        duration_seconds=session.duration_seconds,
        transcript=session.transcript if isinstance(session.transcript, list) else [],
        crisis_detected=session.crisis_detected
    )
