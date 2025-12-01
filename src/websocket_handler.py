"""
WebSocket Handler - Orchestrates LLM - TTS pipeline
"""

import base64
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.models import ClientMessage, ServerMessage
from src.llm_service import get_llm_response
from src.tts_service import get_tts_audio


async def handle_websocket(websocket: WebSocket):
    """
    Handle WebSocket connection - receives message, calls LLM, calls TTS, sends audio.
    
    TODO: Add multi-user support by tracking user_id per connection
    """
    
    # Get client connection info
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else "unknown"
    client_url = f"ws://{client_host}:{client_port}"
    
    print(f"🔗 New connection from {client_url}")
    
    await websocket.accept()
    print(f"✅ Connection accepted: {client_url}")
    
    try:
        while True:
            # Receive and validate
            try:
                data = await websocket.receive_json()
                message = ClientMessage(**data)
            except ValidationError:
                await send_error(websocket, "Invalid message format")
                continue
            except Exception as e:
                # If receive fails, client disconnected or connection broken
                print(f"❌ Receive error from {client_url}: {str(e)[:50]}")
                break  # Exit loop - connection is dead
            
            # Call LLM - TTS pipeline
            try:
                llm_text = await get_llm_response(message.text)
                audio_bytes = await get_tts_audio(llm_text)
                
                # Encode and send
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                response = ServerMessage(
                    type="audio",
                    audio_data=audio_base64,
                    llm_text=llm_text
                )
                
                await websocket.send_json(response.model_dump())
                print(f"✅ Message processed from {client_url}: {len(message.text)} chars → {len(audio_bytes)} bytes")
                
            except Exception as e:
                print(f"❌ Pipeline error from {client_url}: {str(e)[:50]}")
                await send_error(websocket, f"Processing error: {str(e)}")
                continue
    
    except WebSocketDisconnect:
        print(f"🔌 Connection closed: {client_url}")
    except Exception as e:
        print(f"❌ Connection error from {client_url}: {str(e)[:50]}")
    finally:
        try:
            await websocket.close()
            print(f"✅ Cleanup complete for {client_url}")
        except:
            pass  # Already closed


async def send_error(websocket: WebSocket, error_message: str):
    """Send error response to client."""
    try:
        error_response = ServerMessage(
            type="error",
            error_message=error_message
        )
        await websocket.send_json(error_response.model_dump())
    except:
        pass  # Connection might be broken
