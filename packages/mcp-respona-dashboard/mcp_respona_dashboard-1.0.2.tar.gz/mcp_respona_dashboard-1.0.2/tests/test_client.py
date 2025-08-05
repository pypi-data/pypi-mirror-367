"""Tests for API client module."""

import pytest
from unittest.mock import AsyncMock, patch
from respona_mcp_server.client import ResponaAPIClient, APIError


@pytest.fixture
def client():
    """Create a test client instance."""
    return ResponaAPIClient(base_url="http://test.example.com:3001")


@pytest.mark.asyncio
async def test_client_initialization(client):
    """Test client initialization."""
    assert client.base_url == "http://test.example.com:3001/"
    assert client.timeout == 30
    assert client.max_retries == 3


@pytest.mark.asyncio
async def test_successful_get_request(client):
    """Test successful GET request."""
    mock_response = {"success": True, "data": {"tickets": []}}
    
    with patch('httpx.AsyncClient') as mock_async_client:
        mock_client = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client
        
        # Mock successful response
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_client.request.return_value = mock_response_obj
        
        result = await client.get("/api/tickets")
        
        assert result == mock_response
        mock_client.request.assert_called_once()


@pytest.mark.asyncio
async def test_api_error_handling(client):
    """Test API error handling."""
    with patch('httpx.AsyncClient') as mock_async_client:
        mock_client = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client
        
        # Mock error response
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 404
        mock_response_obj.reason_phrase = "Not Found"
        mock_response_obj.json.return_value = {"message": "Resource not found"}
        mock_client.request.return_value = mock_response_obj
        
        with pytest.raises(APIError) as exc_info:
            await client.get("/api/nonexistent")
        
        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)


@pytest.mark.asyncio 
async def test_parameter_cleaning(client):
    """Test that None parameters are removed."""
    mock_response = {"success": True, "data": {}}
    
    with patch('httpx.AsyncClient') as mock_async_client:
        mock_client = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client
        
        mock_response_obj = AsyncMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_client.request.return_value = mock_response_obj
        
        await client.get("/api/tickets", params={"status": "open", "priority": None})
        
        # Check that the call was made with cleaned parameters
        call_args = mock_client.request.call_args
        assert call_args[1]["params"] == {"status": "open"} 