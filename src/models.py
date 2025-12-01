"""
Data Models - Request/Response validation
"""

from pydantic import BaseModel, Field
from typing import Optional


class ClientMessage(BaseModel):
    """Message from client to server."""
    text: str = Field(..., min_length=1, max_length=2000)


class ServerMessage(BaseModel):
    """Message from server to client."""
    type: str  # "audio" or "error"
    audio_data: Optional[str] = None
    llm_text: Optional[str] = None
    error_message: Optional[str] = None
    
    def model_dump(self, **kwargs):
        """Remove None values from response."""
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None}
