import os
import io
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uvicorn
import anyio


from chatbot_backend.all_models.openrouter_llm import openrouter_llm as openai_client
from chatbot_backend.app.agents.agent import addmission_subgraph
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

app = FastAPI(title="Voice Streaming WebSocket Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {
    "configurable": {
        "thread_id": "user_123"
    }
}

elevant_api_key = os.environ.get("ELEVENLABS_API_KEY")
elevenlabs_client = ElevenLabs(api_key=elevant_api_key)

def text_to_speech_elevenlabs(text: str) -> bytes:
    try:
        response = elevenlabs_client.text_to_speech.convert(
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
        print(f"Detailed error when calling the ElevenLabs API: {e}")
        return b""

async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected.")

    audio_buffer = io.BytesIO()

    try:
        while True:
            message = await websocket.receive()
            
            if message.get("type") == "websocket.disconnect":
                print("Websocket Disconnect.")
                break
            
            if "bytes" in message:
                audio_buffer.write(message["bytes"])
                
            elif "text" in message:
                try:
                    command = json.loads(message["text"])
                    
                    if command.get("action") == "STOP_RECORDING":
                        print("Front-End stopped recording. Processing Whisper...")
                        audio_buffer.seek(0)
                        audio_data = audio_buffer.read()
                        
                        if len(audio_data) > 0:
                            # --- STT ---
                            audio_file = io.BytesIO(audio_data)
                            audio_file.name = "speech.webm"
                            
                            transcription = openai_client.audio.transcriptions.create(
                                model="google/chirp-3", 
                                file=audio_file
                            )
                            user_text = transcription.text
                            
                            await websocket.send_json({
                                "type": "transcription",
                                "text": user_text
                            })

                            # --- LLM AGENT (Autonomous execution via main_graph) ---
                            print("LangGraph Agent is running...")
                            agent_reply = ""
                            
                            try:
                                async for chunk, metadata in addmission_subgraph.astream(
                                    {"messages": [HumanMessage(content=user_text)]},
                                    config=config,
                                    stream_mode="messages"
                                ):
                                    if isinstance(chunk, AIMessage) and chunk.content:
                                        agent_reply += chunk.content
                            except Exception as graph_err:
                                print(f"Graph error: {graph_err}")
                                agent_reply = "Sorry, our internal systems are currently experiencing an issue. Please try again later."
                            
                            if not agent_reply:
                                agent_reply = "No response from the AI"

                            # --- TTS ---
                            agent_audio_bytes = await anyio.to_thread.run_sync(
                                text_to_speech_elevenlabs,
                                agent_reply
                            )

                            # --- SEND BACK ---
                            await websocket.send_json({
                                "type": "agent_response",
                                "text": agent_reply,
                                "has_audio": len(agent_audio_bytes) > 0
                            })
                            
                            if len(agent_audio_bytes) > 0:
                                await websocket.send_bytes(agent_audio_bytes)
                                print("Sent the response and audio data back to the frontend.")
                        
                        audio_buffer = io.BytesIO()
                        
                except json.JSONDecodeError:
                    print("Received invalid text data (not a JSON format).")

    except WebSocketDisconnect:
        print("Client actively disconnected (caught by exception).")
    except Exception as e:
        print(f"Voice System Error: {e}")
    finally:
        audio_buffer.close()
        print("WebSocket Voice Clear.")

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket): 
    await websocket_voice_endpoint(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "chatbot_backend.voice:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )