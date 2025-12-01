"""
Configuration - Load from .env file
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # OpenAI
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    request_timeout: int = 30
    
    # LLM
    llm_model: str = "gpt-3.5-turbo"
    llm_max_tokens: int = 150
    llm_temperature: float = 0.7
    # llm_timeout: int = 30  # Max wait time for LLM API response
    llm_system_prompt: str = (
        "You are a helpful AI assistant. "
        "Provide clear, concise, and accurate responses. "
        "Keep answers brief unless asked for details."
    )
    
    # TTS
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"
    tts_response_format: str = "mp3"
    # tts_timeout: int = 15  # Max wait time for TTS conversion
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()
