"""Test LLM Endpoint"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from src.llm_service import get_llm_response


# ================================================================
# TEST 1: Happy Path - Valid LLM Response
# ================================================================

@pytest.mark.asyncio
async def test_llm_valid_response():
    """
    Test that get_llm_response returns a valid response string
    when the OpenAI API call succeeds.
    """
    
    # Mock response from OpenAI
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the LLM."
                }
            }
        ]
    }
    
    # Patch httpx.AsyncClient
    with patch('src.llm_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = mock_response
        
        # Call the function
        result = await get_llm_response("Hello, how are you?")
        
        # Verify results
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "test response" in result.lower()


# ================================================================
# TEST 2: Error Path - 401 Authentication Error
# ================================================================

@pytest.mark.asyncio
async def test_llm_api_auth_error():
    """
    Test that get_llm_response handles 401 Unauthorized error gracefully.
    """
    
    # Create a 401 error response
    error_response = httpx.Response(
        status_code=401,
        text="Unauthorized: Invalid API key",
        request=MagicMock()
    )
    error_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("401 Unauthorized", request=MagicMock(), response=error_response)
    )
    
    # Patch httpx.AsyncClient
    with patch('src.llm_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = error_response
        
        # Call should raise an exception
        with pytest.raises(Exception) as exc_info:
            await get_llm_response("Test message")
        
        # Verify exception details
        assert "api" in str(exc_info.value).lower() or "auth" in str(exc_info.value).lower()


# ================================================================
# TEST 3: Error Path - 500 Server Error
# ================================================================

@pytest.mark.asyncio
async def test_llm_api_server_error():
    """
    Test that get_llm_response handles 500 Internal Server Error gracefully.
    """
    
    # Create a 500 error response
    error_response = httpx.Response(
        status_code=500,
        text="Internal Server Error",
        request=MagicMock()
    )
    error_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("500 Server Error", request=MagicMock(), response=error_response)
    )
    
    # Patch httpx.AsyncClient
    with patch('src.llm_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = error_response
        
        # Call should raise an exception
        with pytest.raises(Exception) as exc_info:
            await get_llm_response("Test message")
        
        # Verify exception is about server error
        assert "500" in str(exc_info.value) or "server" in str(exc_info.value).lower()


# ================================================================
# TEST 4: Error Path - Timeout
# ================================================================

@pytest.mark.asyncio
async def test_llm_timeout_error():
    """
    Test that get_llm_response handles timeout gracefully.
    """
    
    # Patch httpx.AsyncClient to raise timeout
    with patch('src.llm_service.httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        
        # Call should raise timeout exception
        with pytest.raises((httpx.TimeoutException, Exception)):
            await get_llm_response("Test message")


# ================================================================
# TEST 5: Error Path - Malformed Response
# ================================================================

@pytest.mark.asyncio
async def test_llm_malformed_response():
    """
    Test that get_llm_response handles malformed API response gracefully.
    """
    
    # Mock malformed response (missing 'choices' key)
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "error": "Malformed response"
    }
    
    # Patch httpx.AsyncClient
    with patch('src.llm_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = mock_response
        
        # Call should handle gracefully
        with pytest.raises(Exception):
            await get_llm_response("Test message")