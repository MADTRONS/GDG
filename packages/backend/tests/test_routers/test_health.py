"""Tests for health check endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_success(client: AsyncClient) -> None:
    """Test health endpoint returns 200 when database is connected."""
    response = await client.get('/health')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    assert 'timestamp' in data


@pytest.mark.asyncio
async def test_health_check_format(client: AsyncClient) -> None:
    """Test health endpoint returns correct JSON format."""
    response = await client.get('/health')

    data = response.json()
    assert 'status' in data
    assert 'database' in data
    assert 'timestamp' in data
    assert isinstance(data['timestamp'], str)