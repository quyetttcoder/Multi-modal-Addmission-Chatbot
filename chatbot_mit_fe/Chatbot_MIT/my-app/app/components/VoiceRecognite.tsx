'use client';

import { useEffect, useRef, useState } from 'react';
import { FaMicrophoneLines, FaStop } from "react-icons/fa6";

const VOICE_WS_URL =
  process.env.NEXT_PUBLIC_VOICE_WS_URL ?? 'ws://localhost:3001/ws/voice';

interface VoiceChatProps {
  onNewVoiceMessage: (role: "user" | "assistant", text: string) => void;
  threadId?: string;
}

export default function VoiceChat({ onNewVoiceMessage, threadId = "1" }: VoiceChatProps) {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Luôn giữ callback mới nhất mà không buộc phải kết nối lại WebSocket
  const onMessageRef = useRef(onNewVoiceMessage);
  useEffect(() => {
    onMessageRef.current = onNewVoiceMessage;
  }, [onNewVoiceMessage]);

  useEffect(() => {
    const ws = new WebSocket(`${VOICE_WS_URL}?thread_id=${encodeURIComponent(threadId)}`);
    ws.binaryType = "blob";
    wsRef.current = ws;

    ws.onopen = () => console.log("Voice WebSocket connected:", VOICE_WS_URL);

    ws.onmessage = (event) => {
      if (typeof event.data === "string") {
        try {
          const response = JSON.parse(event.data);
          if (response.type === "transcription") {
            onMessageRef.current("user", response.text);
          } else if (response.type === "agent_response") {
            onMessageRef.current("assistant", response.text);
          }
        } catch (e) {
          console.error("Failed to parse JSON from WebSocket message:", e);
        }
      } else if (event.data instanceof Blob) {
        const audioUrl = URL.createObjectURL(event.data);
        const audio = new Audio(audioUrl);
        audio.onended = () => URL.revokeObjectURL(audioUrl);
        audio.play().catch((err) => console.error("Unable to autoplay audio:", err));
      }
    };

    ws.onclose = (e) => console.log("Voice WebSocket closed:", e.code, e.reason);
    ws.onerror = (err) => console.error("Voice WebSocket error:", err);

    return () => ws.close();
  }, [threadId]); // chỉ kết nối lại khi đổi thread, không phụ thuộc callback

  const startVoiceChat = async () => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      console.error("Voice WebSocket is not connected.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(event.data);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);
      setIsRecording(true);
    } catch (err) {
      console.error("Unable to access microphone:", err);
    }
  };

  const stopVoiceChat = () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder) return;

    // onstop chạy SAU chunk dữ liệu cuối cùng -> gửi STOP lúc này mới đủ audio
    recorder.onstop = () => {
      recorder.stream.getTracks().forEach((t) => t.stop()); // tắt mic
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "STOP_RECORDING" }));
      }
    };

    recorder.stop();
    setIsRecording(false);
  };

  return (
    <button
      onClick={isRecording ? stopVoiceChat : startVoiceChat}
      className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-gray-200 dark:hover:bg-[#404040] transition hover:cursor-pointer"
    >
      {isRecording ? (
        <div className="flex items-center justify-center w-8 h-8 rounded-full border border-black dark:border-white">
          <FaStop className="text-black dark:text-white text-xs" />
        </div>
      ) : (
        <FaMicrophoneLines className="text-black dark:text-white" />
      )}
    </button>
  );
}