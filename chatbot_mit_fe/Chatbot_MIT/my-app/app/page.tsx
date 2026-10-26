"use client";

import { useState, useCallback } from "react";

import Conversation, { Message } from "./components/Conversation";
import Dialog from "./components/Dialog";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);

  const addVoiceMessage = useCallback(
    (role: "user" | "assistant", text: string) => {
      const currentTime = new Date();

      setMessages((prev) => {
        if (role === "user") {
          return [
            ...prev,
            { role: "user", content: text, timestamp: currentTime },
            { role: "assistant", content: "", timestamp: currentTime },
          ];
        }

        const copy = [...prev];

        if (copy.length > 0 && copy[copy.length - 1].role === "assistant") {
          copy[copy.length - 1] = {
            ...copy[copy.length - 1],
            content: text,
            timestamp: currentTime,
          };
          return copy;
        }

        return [
          ...prev,
          { role: "assistant", content: text, timestamp: currentTime },
        ];
      });
    },
    []
  );

  const handleSend = async (
    text: string,
    files: File[]
  ) => {
    const imageUrls = files.map((file) =>
      URL.createObjectURL(file)
    );
    const userTime = new Date();
    const loadingTime = new Date();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
        images: imageUrls,
        timestamp: userTime,
      },
      {
        role: "assistant",
        content: "",
        timestamp: loadingTime,
        isLoading: true,
      },
    ]);

    const formData = new FormData();
    formData.append("message", text);

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const res = await fetch("http://localhost:3001/chat", {
        method: "POST",
        body: formData,
      });
      
      const reader = res.body?.getReader();
      if (!reader) {
        throw new Error("Response body is null.");
      }
      

      const decoder = new TextDecoder("utf-8");
      let accumulatedContent = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value, { stream: true });
        
        accumulatedContent += chunkText;
        const assistantTime = new Date();

        setMessages((prev) => {
          const copy = [...prev];
          if (copy.length > 0 && copy[copy.length - 1].role === "assistant") {
            copy[copy.length - 1] = {
              role: "assistant",
              content: accumulatedContent,
              timestamp: assistantTime,
              isLoading: false,
            };
          }
          return copy;
        });
      }
    } catch (error) {
      console.error("Error when chat:", error);
      const errorTime = new Date();

      setMessages((prev) => {
        const copy = [...prev];
        if (copy.length > 0 && copy[copy.length - 1].role === "assistant") {
          copy[copy.length - 1] = {
            role: "assistant",
            content: "Error when connecting to server. Please try again.",
            timestamp: errorTime,
            isLoading: false,
          };
        }
        return copy;
      });
    }
  };

  return (
    <div className="flex h-screen flex-col">
      <Conversation messages={messages} />

      <div className="border-t border-white/10">
        <div className="mx-auto flex max-w-4xl items-center gap-2 p-4">
          <div className="flex-1">
            <Dialog
              onSend={handleSend}
              onNewVoiceMessage={addVoiceMessage}
            />
          </div>
        </div>
      </div>
    </div>
  );
}