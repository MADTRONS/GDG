"""Tests for database connection and configuration."""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession) -> None:
    """Test that database connection works."""
    result = await db_session.execute(text('SELECT 1 as value'))
    row = result.fetchone()
    
    assert row is not None
    assert row[0] == 1


@pytest.mark.asyncio
async def test_database_pool_configuration() -> None:
    """Test that connection pool settings are correct."""
    assert engine.pool.size() == 5  # pool_size
    assert engine.pool._max_overflow == 10  # max_overflow
    assert engine.pool._pre_ping is True  # pool_pre_ping


@pytest.mark.asyncio
async def test_async_session_creation() -> None:
    """Test that async session can be created."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('SELECT 1'))
        assert result.fetchone()[0] == 1