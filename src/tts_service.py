"""
TTS Service - OpenAI Text-to-Speech

This module is responsible for:
Given input text, call OpenAI's TTS API and return audio bytes.
"""

import httpx
from src.config import settings

async def get_tts_audio( llm_response_text: str ) -> bytes:
    """
    Convert the text to speech audio using OpenAI TTS
    TTS Endpoint URL = https://platform.openai.com/docs/api-reference/audio/createSpeech

    Args:
        text: The text to convert to speech.

    Returns:
        Raw audio bytes (e.g. MP3), suitable for sending over WebSocket.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx status.
        httpx.RequestError: For network-related errors.
    """

    # Build the endpoint URL using config
    url = f"{settings.openai_base_url}/audio/speech"

    # Build the headers and add OpenAI API KEY
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    # Build the Payload as per the OpenAI Spec
    payload = {
        "model": settings.tts_model,
        "voice": settings.tts_voice,
        "input": llm_response_text,
        "response_format": settings.tts_response_format,
    }

    # Call the OpenAI Audio Endpoint with async
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:

        # Call with the params and get the response
        response = await client.post(url, headers=headers, json=payload)

        response.raise_for_status()

        # For TTS, the audio is returned as binary content
        return response.content