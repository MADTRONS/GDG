"""Session management API endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import Session
from app.repositories.session_repository import SessionRepository
from app.schemas.session import (
    SaveSessionRequest,
    SaveSessionResponse,
    SessionSummary,
    SessionDetail,
    SessionPreview,
    SessionsListResponse
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
    response_model=SessionsListResponse,
    summary="Get user sessions with filters and pagination",
    description="Retrieve paginated list of user's past counseling sessions with optional filters."
)
async def get_sessions(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    category: Optional[str] = Query(None, description="Filter by counselor category name"),
    mode: Optional[str] = Query(None, regex="^(voice|video)$", description="Filter by session mode"),
    start_date: Optional[str] = Query(None, description="Filter sessions after this date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter sessions before this date (ISO format)"),
    current_user: dict[str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SessionsListResponse:
    """
    Get paginated list of sessions for authenticated user with optional filters.
    
    Returns session preview data suitable for list display including:
    - Session metadata (ID, category, mode, timestamps)
    - Counselor category name and icon
    - First 100 characters of transcript preview
    - Pagination metadata
    
    Query params:
    - page: Page number (default 1)
    - limit: Results per page (default 20, max 100)
    - category: Filter by counselor category name (optional)
    - mode: Filter by 'voice' or 'video' (optional)
    - start_date: Filter sessions after this date ISO format (optional)
    - end_date: Filter sessions before this date ISO format (optional)
    """
    repo = SessionRepository(db)
    
    # Parse date filters if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (e.g., 2025-12-22T00:00:00Z)."
            )
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (e.g., 2025-12-22T23:59:59Z)."
            )
    
    try:
        # Get filtered sessions with pagination
        rows, total_count = await repo.get_user_sessions_with_filters(
            user_id=UUID(current_user["user_id"]),
            category=category,
            mode=mode,
            start_date=start_datetime,
            end_date=end_datetime,
            page=page,
            limit=limit
        )
        
        # Format response
        sessions = []
        for session, category_name, category_icon in rows:
            # Extract transcript preview (first 100 characters)
            transcript_preview = ""
            if session.transcript and isinstance(session.transcript, list) and len(session.transcript) > 0:
                # Get text from first message
                first_message = session.transcript[0]
                if isinstance(first_message, dict) and 'text' in first_message:
                    transcript_preview = first_message['text'][:100]
            
            sessions.append(SessionPreview(
                session_id=str(session.id),
                counselor_category=category_name,
                counselor_icon=category_icon,
                mode=session.mode,
                started_at=session.started_at.isoformat(),
                duration_seconds=session.duration_seconds or 0,
                transcript_preview=transcript_preview
            ))
        
        return SessionsListResponse(
            sessions=sessions,
            total_count=total_count,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sessions: {str(e)}"
        )


@router.get(
    "/legacy",
    response_model=list[SessionSummary],
    summary="Get user sessions (legacy endpoint)",
    description="Legacy endpoint - use GET / instead for enhanced filtering."
)
async def get_sessions_legacy(
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
    from app.models.counselor_category import CounselorCategory
    
    # Query session with counselor category join
    query = (
        select(Session, CounselorCategory)
        .join(CounselorCategory, Session.counselor_category == CounselorCategory.name)
        .where(
            and_(
                Session.id == session_id,
                Session.deleted_at.is_(None)
            )
        )
    )
    
    result = await db.execute(query)
    row = result.first()
    
    # Check if session exists
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session, category = row
    
    # Verify ownership
    if str(session.user_id) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this session"
        )
    
    # Format transcript messages
    transcript_data = session.transcript if isinstance(session.transcript, list) else []
    
    # Get quality metrics if available
    quality_metrics = None
    if hasattr(session, 'quality_metrics') and session.quality_metrics:
        quality_metrics = session.quality_metrics
    
    return SessionDetail(
        session_id=session.id,
        counselor_category=category.name,
        counselor_icon=category.icon_name,
        mode=session.mode,
        started_at=session.started_at.isoformat(),
        ended_at=session.ended_at.isoformat() if session.ended_at else None,
        duration_seconds=session.duration_seconds,
        transcript=transcript_data,
        quality_metrics=quality_metrics,
        crisis_detected=session.crisis_detected
    )
