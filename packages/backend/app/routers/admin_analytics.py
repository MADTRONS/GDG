"""Admin analytics router for usage reporting and trends."""
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import AdminRole
from app.models.session import Session
from app.utils.admin_dependencies import require_admin_role

admin_analytics_router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["admin-analytics"]
)


class SessionAnalyticsResponse(BaseModel):
    """Response schema for session analytics."""
    total_sessions: int
    avg_duration: float  # in seconds
    sessions_by_category: dict[str, int]
    sessions_by_mode: dict[str, int]
    peak_usage_hours: dict[int, int]
    daily_trend: dict[str, int]
    avg_duration_by_category: dict[str, float]


@admin_analytics_router.get("/sessions", response_model=SessionAnalyticsResponse)
async def get_session_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> SessionAnalyticsResponse:
    """
    Get aggregated session analytics for a date range.
    
    Only accessible by SUPER_ADMIN role.
    Returns aggregated data with no PII.
    """
    try:
        # Parse and validate dates
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=UTC
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
            )
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before or equal to end date"
            )
        
        # Validate date range (max 1 year)
        if (end_dt - start_dt).days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days"
            )
        
        # Base filter for date range (only completed sessions)
        base_filter = and_(
            Session.started_at >= start_dt,
            Session.started_at <= end_dt,
            Session.ended_at.isnot(None),
            Session.deleted_at.is_(None)
        )
        
        # Total sessions
        total_query = select(func.count(Session.id)).where(base_filter)
        total_result = await db.execute(total_query)
        total_sessions = total_result.scalar() or 0
        
        # Average duration (exclude nulls)
        avg_duration_query = select(
            func.avg(Session.duration_seconds)
        ).where(
            and_(
                base_filter,
                Session.duration_seconds.isnot(None)
            )
        )
        avg_result = await db.execute(avg_duration_query)
        avg_duration = float(avg_result.scalar() or 0)
        
        # Sessions by category
        category_query = (
            select(
                Session.counselor_category,
                func.count(Session.id).label("count")
            )
            .where(base_filter)
            .group_by(Session.counselor_category)
        )
        category_result = await db.execute(category_query)
        sessions_by_category = {
            row[0]: row[1] for row in category_result.all()
        }
        
        # Sessions by mode
        mode_query = (
            select(
                Session.mode,
                func.count(Session.id).label("count")
            )
            .where(base_filter)
            .group_by(Session.mode)
        )
        mode_result = await db.execute(mode_query)
        sessions_by_mode = {
            row[0]: row[1] for row in mode_result.all()
        }
        
        # Peak usage hours (hour of day, 0-23)
        hour_query = (
            select(
                extract("hour", Session.started_at).label("hour"),
                func.count(Session.id).label("count")
            )
            .where(base_filter)
            .group_by("hour")
        )
        hour_result = await db.execute(hour_query)
        peak_usage_hours = {
            int(row[0]): row[1] for row in hour_result.all()
        }
        
        # Daily trend (sessions per day)
        daily_query = (
            select(
                func.date(Session.started_at).label("day"),
                func.count(Session.id).label("count")
            )
            .where(base_filter)
            .group_by("day")
            .order_by("day")
        )
        daily_result = await db.execute(daily_query)
        daily_trend = {
            str(row[0]): row[1] for row in daily_result.all()
        }
        
        # Average duration by category
        avg_duration_category_query = (
            select(
                Session.counselor_category,
                func.avg(Session.duration_seconds).label("avg_duration")
            )
            .where(
                and_(
                    base_filter,
                    Session.duration_seconds.isnot(None)
                )
            )
            .group_by(Session.counselor_category)
        )
        avg_duration_result = await db.execute(avg_duration_category_query)
        avg_duration_by_category = {
            row[0]: float(row[1] or 0) for row in avg_duration_result.all()
        }
        
        return SessionAnalyticsResponse(
            total_sessions=total_sessions,
            avg_duration=avg_duration,
            sessions_by_category=sessions_by_category,
            sessions_by_mode=sessions_by_mode,
            peak_usage_hours=peak_usage_hours,
            daily_trend=daily_trend,
            avg_duration_by_category=avg_duration_by_category
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )