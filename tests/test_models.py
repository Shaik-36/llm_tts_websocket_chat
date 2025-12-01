"""Test data models validation"""

import pytest
from src.models import ClientMessage, ServerMessage


# ================================================================
# TEST 1: ClientMessage - Valid message
# ================================================================


def test_valid_message():
    """Should accept valid message"""
    msg = ClientMessage(text="What is AI?")
    assert msg.text == "What is AI?"


# ================================================================
# TEST 2: ClientMessage - Empty message validation
# ================================================================


def test_empty_message_rejected():
    """Should reject empty message"""
    with pytest.raises(ValueError):
        ClientMessage(text="")


# ================================================================
# TEST 3: ClientMessage - Length validation
# ================================================================


def test_too_long_message_rejected():
    """Should reject message > 2000 chars"""
    with pytest.raises(ValueError):
        ClientMessage(text="a" * 2001)


# ================================================================
# TEST 4: ServerMessage - Audio response
# ================================================================


def test_audio_response():
    """Should create audio response"""
    msg = ServerMessage(
        type="audio",
        audio_data="base64data",
        llm_text="Response"
    )
    assert msg.type == "audio"
    assert msg.audio_data == "base64data"


# ================================================================
# TEST 5: ServerMessage - Error response
# ================================================================


def test_error_response():
    """Should create error response"""
    msg = ServerMessage(
        type="error",
        error_message="API error"
    )
    assert msg.type == "error"
    assert msg.error_message == "API error"


# ================================================================
# TEST 6: ServerMessage - None values handling
# ================================================================


def test_none_values_removed():
    """Should remove None values from response"""
    msg = ServerMessage(
        type="audio",
        audio_data="data",
        llm_text=None,
        error_message=None
    )
    dumped = msg.model_dump()
    assert "llm_text" not in dumped
    assert "error_message" not in dumped
