"""
Data Models - Request/Response Validation

Defines the structure of data exchanged between client and server.

Pydantic models:
1. Automatic validation (rejects bad data before processing)
2. Type safety (IDE autocomplete, catches bugs early)
3. Self-documenting (models show exact data structure)
4. Clear error messages (tells client what's wrong)



"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class ClientMessage(BaseModel):
    """
    Message received from client via WebSocket.
    
    Example JSON:
    {
        "text": "What is artificial intelligence?"
    }
    
    Why this structure?
    - Simple: Only one required field
    - Clear: Obvious what client should send
    - Validated: Can't send empty or too-long text
    
    Design decisions:
    - No optional fields (keeping minimal)
    - No user_id (keeping minimal)
    - No session_id (keeping minimal)
    - Can add later if needed without breaking existing clients
    """
    
    text: str = Field(
        ...,  # Required field (the ... means "no default")
        min_length=1,
        max_length=1000,
        description="User's text input to process"
    )
    # Why max 1000? Balance between:
    # - User flexibility (1000 chars is ~200 words)
    # - API costs (longer = more expensive)
    # - Response time (longer = slower)
    
    @field_validator('text')
    @classmethod
    def text_must_not_be_whitespace(cls, v: str) -> str:
        """
        Custom validator: reject whitespace-only text.
        
        Why needed?
        Pydantic's min_length=1 would accept "   " (3 spaces).
        That would waste an OpenAI API call on meaningless input.
        
        How it works:
        1. Strip whitespace from both ends
        2. Check if anything remains
        3. Raise error if empty
        4. Return cleaned value
        
        This runs AFTER type validation, BEFORE model creation.
        """
        v = v.strip()  # Remove leading/trailing whitespace
        
        if not v:
            # If Empty after stripping - reject it
            raise ValueError('Text cannot be empty or only whitespace')
        
        return v  # Return cleaned value (whitespace removed)
    
    class Config:
        """Pydantic model configuration."""
        
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "text": "Explain quantum computing in simple terms"
            }
        }


class ServerMessage(BaseModel):
    """
    Message sent from server to client via WebSocket.
    
    Two types of messages:
    
    1. Success (audio response):
    {
        "type": "audio",
        "audio_data": "base64encodedstring...",
        "llm_text": "Quantum computing uses...",
        "timestamp": "2025-11-30T19:00:00.123456"
    }
    
    2. Error response:
    {
        "type": "error",
        "error_message": "OpenAI API timeout",
        "timestamp": "2025-11-30T19:00:00.123456"
    }
    
    Why this structure?
    - Discriminator field "type" (client knows how to handle)
    - Optional fields (present based on type)
    - Timestamp (debugging, ordering)
    - LLM text included (transparency, debugging)
    
    Design decisions:
    - Base64 audio (JSON compatible)
    - Include LLM text even with audio (useful for display)
    - UTC timestamp (commonly used)
    """
    
    type: Literal["audio", "error", "status"] = Field(
        ...,
        description="Message type for client-side routing"
    )
    # Why Literal? Restricts to exact values
    # Client can do: if (msg.type === "audio") { ... }
    # Typos like "Audio" or "audi" rejected at validation
    
    audio_data: Optional[str] = Field(
        None,
        description="Base64-encoded audio (MP3 format)"
    )
    # Why Optional? Only present when type="audio"
    # Why base64? JSON can't hold binary data
    # Why MP3? Universal compatibility
    
    llm_text: Optional[str] = Field(
        None,
        description="LLM's text response (for display/debugging)"
    )
    # Why include? Even though we send audio, text is useful:
    # - Client might want to display transcript
    # - Debugging (see what LLM actually said)
    # - Accessibility (screen readers)
    
    error_message: Optional[str] = Field(
        None,
        description="Error details if type='error'"
    )
    # Why Optional? Only present when type="error"
    # Contains human-readable error description
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this message was created (UTC)"
    )
    # Why default_factory? Generates timestamp automatically
    # Why UTC? Timezone-independent (best practice)
    # Why included? Helps with:
    # - Debugging (when did this happen?)
    # - Client-side message ordering
    # - Latency calculation (client can compare with send time)
    
    class Config:
        """Pydantic model configuration."""
        
        # Examples for API documentation
        json_schema_extra = {
            "examples": [
                {
                    "type": "audio",
                    "audio_data": "SUQzBAAAAAAAI1RTU0UAAAA...",
                    "llm_text": "Quantum computing uses quantum bits...",
                    "timestamp": "2025-11-30T19:00:00.123456"
                },
                {
                    "type": "error",
                    "error_message": "OpenAI API rate limit exceeded",
                    "timestamp": "2025-11-30T19:00:00.123456"
                }
            ]
        }
