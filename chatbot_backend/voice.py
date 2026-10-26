import os
import io
import json
from functools import lru_cache
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uvicorn
import anyio


from all_models.openrouter_llm import openrouter_llm as client
from service.agent import stream_agent


router = APIRouter()

config = {
    "configurable": {
        "thread_id": "user_123"
    }
}


@lru_cache(maxsize=1)
def get_elevenlabs() -> ElevenLabs:
    return ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

def speech_to_text(audio_data: bytes)->str:
    audio_file = io.BytesIO(audio_data)
    audio_file.name = "speech.webm"
    transcription = client.audio.transcriptions.create(
        model="google/chirp-3",
        file=audio_file
    )
    return transcription.text

def text_to_speech(text: str) -> bytes:
    try:
        response = get_elevenlabs().text_to_speech.convert(
        voice_id="Na15FlRRkMEDtEW4nVVP",
        text=text,
        model_id="eleven_flash_v2_5",
        output_format="mp3_22050_32",
        voice_settings=VoiceSettings(
            stability=0.3, 
            similarity_boost=1.0, 
            style=0.0, 
            use_speaker_boost=True, 
            speed=1.2
        )
    )

        audio_bytes = b"".join(chunk for chunk in response if chunk)
        return audio_bytes
        
    except Exception as e:
        error_msg = f"Detailed error when calling the ElevenLabs API: {e}"
        return error_msg.encode('utf-8')


@router.websocket("/ws/voice")
async def voice_ws(websocket: WebSocket, thread_id: Optional[str]="1"): 
    await websocket.accept()
    audio_buffer = io.BytesIO()
    try:
        while True:
            message =await  websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if message.get("bytes"):
                audio_buffer.write(message["bytes"])
                continue

            if not message.get("text"):
                continue

            try:
                command = json.loads(message["text"])
            except json.JSONDecodeError:
                continue
            if command.get("action") != "STOP_RECORDING":
                continue

            audio_data = audio_buffer.getvalue()
            audio_buffer = io.BytesIO()
            if not audio_data:
                continue

            # STT
            user_text = await anyio.to_thread.run_sync(speech_to_text, audio_data)
            await websocket.send_json({"type": "transcription", "text": user_text})

            # Agent
            agen_reply = ""
            async for chunk in stream_agent(user_text, thread_id):
                agen_reply += chunk
            if not agen_reply:
                agen_reply = "No response from the AI."

            # TTS
            audio_bytes = await anyio.to_thread.run_sync(text_to_speech, agen_reply)

            await websocket.send_json({
                "type": "agent_response",
                "text": agen_reply,
                "has_audio": len(audio_bytes) > 0
            })
            if audio_bytes:
                await websocket.send_bytes(audio_bytes)
    except WebSocketDisconnect:
        audio_buffer.close()