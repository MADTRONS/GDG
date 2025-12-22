"""Session management API endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import Session
from app.models.counselor_category import CounselorCategory
from app.repositories.session_repository import SessionRepository
from app.schemas.session import (
    SaveSessionRequest,
    SaveSessionResponse,
    SessionSummary,
    SessionDetail,
    SessionPreview,
    SessionsListResponse,
    SessionStatsResponse
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


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="Soft-delete a session by setting deleted_at timestamp. Only the session owner can delete their session."
)
async def delete_session(
    session_id: UUID,
    current_user: dict[str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a session (soft delete by setting deleted_at timestamp).
    
    Only the session owner can delete their session.
    """
    # Query session (excluding already deleted sessions)
    query = select(Session).where(
        and_(
            Session.id == session_id,
            Session.deleted_at.is_(None)
        )
    )
    
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    # Check if session exists
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check authorization - user must own the session
    if str(session.user_id) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this session"
        )
    
    # Soft delete: set deleted_at timestamp
    session.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return None  # 204 No Content


@router.get(
    "/stats",
    response_model=SessionStatsResponse,
    summary="Get session statistics",
    description="Get aggregated session statistics for the authenticated user including total sessions, hours, top category, and last session date."
)
async def get_session_stats(
    current_user: dict[str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SessionStatsResponse:
    """
    Get aggregated session statistics for authenticated user.
    
    Returns:
    - total_sessions: Count of all non-deleted sessions
    - total_hours: Sum of session durations in hours
    - top_category: Most frequently used counselor category
    - top_category_icon: Icon for the top category
    - last_session_date: Date of most recent session
    """
    # Base filter for user's non-deleted sessions
    base_filter = and_(
        Session.user_id == UUID(current_user["user_id"]),
        Session.deleted_at.is_(None)
    )
    
    # Total sessions count
    count_query = select(func.count(Session.id)).where(base_filter)
    total_result = await db.execute(count_query)
    total_sessions = total_result.scalar() or 0
    
    # Total hours (sum of duration_seconds converted to hours)
    hours_query = select(func.sum(Session.duration_seconds)).where(base_filter)
    hours_result = await db.execute(hours_query)
    total_seconds = hours_result.scalar() or 0
    total_hours = round(total_seconds / 3600, 1) if total_seconds else 0.0
    
    # Most used category
    category_query = (
        select(
            CounselorCategory.name,
            CounselorCategory.icon_name,
            func.count(Session.id).label('count')
        )
        .join(CounselorCategory, Session.counselor_category == CounselorCategory.name)
        .where(base_filter)
        .group_by(CounselorCategory.id, CounselorCategory.name, CounselorCategory.icon_name)
        .order_by(desc('count'))
        .limit(1)
    )
    category_result = await db.execute(category_query)
    top_category_row = category_result.first()
    
    top_category = None
    top_category_icon = None
    if top_category_row:
        top_category = top_category_row[0]
        top_category_icon = top_category_row[1]
    
    # Last session date
    date_query = select(func.max(Session.started_at)).where(base_filter)
    date_result = await db.execute(date_query)
    last_session = date_result.scalar()
    last_session_date = last_session.isoformat() if last_session else None
    
    return SessionStatsResponse(
        total_sessions=total_sessions,
        total_hours=total_hours,
        top_category=top_category,
        top_category_icon=top_category_icon,
        last_session_date=last_session_date
    )
