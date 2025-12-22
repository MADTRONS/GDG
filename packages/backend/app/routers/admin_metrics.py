"""Admin metrics router for system monitoring dashboard."""
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import AdminRole
from app.models.counselor_category import CounselorCategory
from app.models.session import Session
from app.utils.admin_dependencies import require_admin_role

admin_metrics_router = APIRouter(
    prefix="/api/admin/metrics",
    tags=["admin-metrics"]
)


class CurrentMetricsResponse(BaseModel):
    """Response schema for current system metrics."""
    active_sessions_count: int
    avg_connection_quality: str
    error_rate_last_hour: float
    api_response_time_p95: float
    db_pool_active: int
    db_pool_size: int
    system_health: str


class SessionMetricsResponse(BaseModel):
    """Response schema for session metrics."""
    total_sessions: int
    sessions_by_category: dict[str, int]
    connection_quality_distribution: dict[str, float]


class ExternalServicesResponse(BaseModel):
    """Response schema for external services status."""
    daily_co: str
    livekit: str
    beyond_presence: str


@admin_metrics_router.get("/current", response_model=CurrentMetricsResponse)
async def get_current_metrics(
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.SYSTEM_MONITOR
    )),
    db: AsyncSession = Depends(get_db)
) -> CurrentMetricsResponse:
    """
    Get current system metrics including active sessions and health indicators.
    
    Accessible by SYSTEM_MONITOR and SUPER_ADMIN roles only.
    """
    try:
        # Active sessions (sessions started in last 30 minutes that haven't ended)
        active_threshold = datetime.now(UTC) - timedelta(minutes=30)
        active_query = select(func.count(Session.id)).where(
            and_(
                Session.started_at >= active_threshold,
                Session.ended_at.is_(None)
            )
        )
        active_result = await db.execute(active_query)
        active_sessions = active_result.scalar() or 0
        
        # Average connection quality from recent sessions
        recent_threshold = datetime.now(UTC) - timedelta(hours=1)
        recent_query = select(Session.quality_metrics).where(
            and_(
                Session.started_at >= recent_threshold,
                Session.quality_metrics.isnot(None)
            )
        ).limit(100)
        recent_result = await db.execute(recent_query)
        recent_sessions = recent_result.scalars().all()
        
        # Calculate average quality
        quality_scores = {
            "excellent": 4,
            "good": 3,
            "fair": 2,
            "poor": 1
        }
        total_score = 0
        count = 0
        for metrics in recent_sessions:
            if metrics and "connection_quality_average" in metrics:
                quality = metrics.get("connection_quality_average")
                if quality:
                    total_score += quality_scores.get(quality, 2)
                    count += 1
        
        avg_score = total_score / count if count > 0 else 3
        if avg_score >= 3.5:
            avg_quality = "excellent"
        elif avg_score >= 2.5:
            avg_quality = "good"
        elif avg_score >= 1.5:
            avg_quality = "fair"
        else:
            avg_quality = "poor"
        
        # Error rate (placeholder - would integrate with actual error logging system)
        # For MVP, we use a mock value
        error_rate = 0.01  # 1% error rate
        
        # API response time (placeholder - would integrate with actual monitoring)
        # For MVP, we use a mock value
        api_p95 = 250.0  # milliseconds
        
        # Database connection pool status
        pool = db.get_bind().pool
        pool_active = pool.checkedout() if hasattr(pool, "checkedout") else 0
        pool_size = pool.size()
        
        # System health determination
        if error_rate > 0.05 or api_p95 > 1000:
            system_health = "critical"
        elif error_rate > 0.02 or api_p95 > 500:
            system_health = "degraded"
        else:
            system_health = "healthy"
        
        return CurrentMetricsResponse(
            active_sessions_count=active_sessions,
            avg_connection_quality=avg_quality,
            error_rate_last_hour=error_rate,
            api_response_time_p95=api_p95,
            db_pool_active=pool_active,
            db_pool_size=pool_size,
            system_health=system_health
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch current metrics: {str(e)}"
        )


@admin_metrics_router.get("/sessions", response_model=SessionMetricsResponse)
async def get_session_metrics(
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.SYSTEM_MONITOR
    )),
    db: AsyncSession = Depends(get_db)
) -> SessionMetricsResponse:
    """
    Get aggregated session metrics by counselor category (no PII).
    
    Accessible by SYSTEM_MONITOR and SUPER_ADMIN roles only.
    """
    try:
        # Total sessions (last 30 days)
        recent_threshold = datetime.now(UTC) - timedelta(days=30)
        total_query = select(func.count(Session.id)).where(
            Session.started_at >= recent_threshold
        )
        total_result = await db.execute(total_query)
        total_sessions = total_result.scalar() or 0
        
        # Sessions by category
        category_query = (
            select(
                CounselorCategory.name,
                func.count(Session.id).label("count")
            )
            .join(CounselorCategory, Session.counselor_category == CounselorCategory.name)
            .where(Session.started_at >= recent_threshold)
            .group_by(CounselorCategory.name)
        )
        category_result = await db.execute(category_query)
        sessions_by_category = {row[0]: row[1] for row in category_result.all()}
        
        # Connection quality distribution
        quality_query = select(Session.quality_metrics).where(
            and_(
                Session.started_at >= recent_threshold,
                Session.quality_metrics.isnot(None)
            )
        )
        quality_result = await db.execute(quality_query)
        quality_sessions = quality_result.scalars().all()
        
        quality_counts = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        for metrics in quality_sessions:
            if metrics and "connection_quality_average" in metrics:
                quality = metrics["connection_quality_average"]
                if quality in quality_counts:
                    quality_counts[quality] += 1
        
        total_quality = sum(quality_counts.values())
        quality_distribution = {
            k: round((v / total_quality) * 100, 1) if total_quality > 0 else 0
            for k, v in quality_counts.items()
        }
        
        return SessionMetricsResponse(
            total_sessions=total_sessions,
            sessions_by_category=sessions_by_category,
            connection_quality_distribution=quality_distribution
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch session metrics: {str(e)}"
        )


@admin_metrics_router.get("/external-services", response_model=ExternalServicesResponse)
async def check_external_services(
    current_admin: dict = Depends(require_admin_role(
        AdminRole.SUPER_ADMIN,
        AdminRole.SYSTEM_MONITOR
    ))
) -> ExternalServicesResponse:
    """
    Check health status of external services.
    
    Accessible by SYSTEM_MONITOR and SUPER_ADMIN roles only.
    """
    services_status = {
        "daily_co": "unknown",
        "livekit": "unknown",
        "beyond_presence": "unknown"
    }
    
    # Check Daily.co API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.daily.co/v1/",
                timeout=5.0
            )
            services_status["daily_co"] = "operational" if response.status_code < 500 else "degraded"
    except Exception:
        services_status["daily_co"] = "down"
    
    # For MVP, LiveKit and Beyond Presence checks are placeholders
    # In production, these would make actual health check requests
    services_status["livekit"] = "operational"
    services_status["beyond_presence"] = "operational"
    
    return ExternalServicesResponse(**services_status)
