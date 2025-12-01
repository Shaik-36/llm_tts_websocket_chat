"""Test TTS Endpoint"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from src.tts_service import get_tts_audio


# ================================================================
# TEST 1: Happy Path - Valid TTS Audio Response
# ================================================================

@pytest.mark.asyncio
async def test_tts_valid_response():
    """
    Test that get_tts_audio returns valid audio bytes when
    the OpenAI TTS API call succeeds.
    """
    
    # Mock audio bytes (simulating MP3 data)
    mock_audio_bytes = b'\xff\xfb\x10\x00...' # Simulated MP3 header
    mock_response = MagicMock()
    mock_response.content = mock_audio_bytes
    
    # Patch httpx.AsyncClient
    with patch('src.tts_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = mock_response
        
        # Call the function
        result = await get_tts_audio("This is a test message for TTS.")
        
        # Verify results
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0


# ================================================================
# TEST 2: Error Path - 401 Authentication Error
# ================================================================

@pytest.mark.asyncio
async def test_tts_api_auth_error():
    """
    Test that get_tts_audio handles 401 Unauthorized error gracefully.
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
    with patch('src.tts_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = error_response
        
        # Call should raise an exception
        with pytest.raises(Exception) as exc_info:
            await get_tts_audio("Test audio message")
        
        # Verify exception is about auth/401

        assert "401" in str(exc_info.value) or "auth" in str(exc_info.value).lower() or "unauthorized" in str(exc_info.value).lower()


# ================================================================
# TEST 3: Error Path - 500 Server Error
# ================================================================

@pytest.mark.asyncio
async def test_tts_api_server_error():
    """
    Test that get_tts_audio handles 500 Internal Server Error gracefully.
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
    with patch('src.tts_service.httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = error_response
        
        # Call should raise an exception
        with pytest.raises(Exception) as exc_info:
            await get_tts_audio("Test audio message")
        
        # Verify exception is about server error
        assert "500" in str(exc_info.value) or "server" in str(exc_info.value).lower()


# ================================================================
# TEST 4: Error Path - Timeout
# ================================================================

@pytest.mark.asyncio
async def test_tts_timeout_error():
    """
    Test that get_tts_audio handles timeout gracefully.
    """
    
    # Patch httpx.AsyncClient to raise timeout
    with patch('src.tts_service.httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        
        # Call should raise timeout exception
        with pytest.raises((httpx.TimeoutException, Exception)):
            await get_tts_audio("Test audio message")


# ================================================================
# TEST 5: Error Path - Invalid Text Validation
# ================================================================

@pytest.mark.asyncio
async def test_tts_invalid_text_length():
    """
    Test that get_tts_audio handles invalid text (too short or empty).
    """
    
    # Test with empty string
    with pytest.raises(Exception):
        # Most TTS APIs reject empty strings
        await get_tts_audio("")
    
    # Test with None
    with pytest.raises(Exception):
        await get_tts_audio(None)
