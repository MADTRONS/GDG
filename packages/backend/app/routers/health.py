"""Health check endpoint for monitoring database connectivity."""
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(tags=['health'])


@router.get('/health', status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Health check endpoint that verifies database connectivity.

    Returns:
        dict: Health status with database connection state and timestamp

    Raises:
        HTTPException: 503 Service Unavailable if database is not accessible
    """
    try:
        # Test database connection with simple query
        await db.execute(text('SELECT 1'))

        return {
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.now(UTC).isoformat(),
            }
        ) from e
