"""Test data models validation"""

import pytest
from src.models import ClientMessage, ServerMessage


class TestClientMessage:
    """Test ClientMessage validation"""
    
    def test_valid_message(self):
        """Should accept valid message"""
        msg = ClientMessage(text="What is AI?")
        assert msg.text == "What is AI?"
    
    def test_empty_message_rejected(self):
        """Should reject empty message"""
        with pytest.raises(ValueError):
            ClientMessage(text="")
    
    def test_too_long_message_rejected(self):
        """Should reject message > 2000 chars"""
        with pytest.raises(ValueError):
            ClientMessage(text="a" * 2001)


class TestServerMessage:
    """Test ServerMessage creation"""
    
    def test_audio_response(self):
        """Should create audio response"""
        msg = ServerMessage(
            type="audio",
            audio_data="base64data",
            llm_text="Response"
        )
        assert msg.type == "audio"
        assert msg.audio_data == "base64data"
    
    def test_error_response(self):
        """Should create error response"""
        msg = ServerMessage(
            type="error",
            error_message="API error"
        )
        assert msg.type == "error"
        assert msg.error_message == "API error"
    
    def test_none_values_removed(self):
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
