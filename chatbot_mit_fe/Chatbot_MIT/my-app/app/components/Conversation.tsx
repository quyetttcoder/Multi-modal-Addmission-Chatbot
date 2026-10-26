import React, { useState } from "react";
import { TypeAnimation } from "react-type-animation";

import PreviewImage from "./PreviewImage";

export interface Message {
  role: "user" | "assistant";
  content: string;
  images?: string[];
  timestamp?: string | Date;
  isLoading?: boolean;
}

export interface ConversationProps {
  messages: Message[];
}

export default function Conversation({
  messages,
}: ConversationProps) {
  const [previewImage, setPreviewImage] = useState<string | null>(
    null
  );

  const handleChatLength = (message: string) => {
    return message.split(" ").map((word, index) => {
      if (word.length > 20) {
        return (
          <React.Fragment key={index}>
            <span className="break-all">{word}</span>{" "}
          </React.Fragment>
        );
      }

      return (
        <React.Fragment key={index}>
          {word}{" "}
        </React.Fragment>
      );
    });
  };


  const formatTime = (time?: string | Date) => {
    if (!time) return "";
    const date = new Date(time);
    
    if (isNaN(date.getTime())) return "";

    return date.toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  };

  return (
    <>
      <div
        className={`mx-auto flex h-full w-full max-w-4xl flex-col gap-3 overflow-y-auto p-3 md:p-4 ${
          messages?.length
            ? ""
            : "items-center justify-center"
        }`}
      >
        {messages?.length ? (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex w-full ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`flex max-w-[85%] flex-col md:max-w-[75%] ${
                  message.role === "user" ? "items-end" : "items-start"
                }`}
              >
                {/* Attached image display section */}
                <div
                  className={`mb-2 flex max-w-full flex-wrap gap-2 ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {message.images?.map((item, imgIndex) => (
                    <div
                      key={imgIndex}
                      className="h-16 w-16 shrink-0 cursor-pointer overflow-hidden rounded-xl border bg-gray-100 dark:bg-neutral-800 sm:h-20 sm:w-20 md:h-24 md:w-24"
                    >
                      <img
                        src={item}
                        alt=""
                        className="h-full w-full object-cover"
                        onClick={() => setPreviewImage(item)}
                      />
                    </div>
                  ))}
                </div>

                {/* Container for message content or the 'Thinking' loading animation. */}
                <div
                  className={`max-w-full w-fit rounded-2xl px-3 py-2.5 md:py-3 ${
                    message.role === "user"
                      ? "rounded-tr-none bg-red-700 text-white"
                      : "rounded-tl-none bg-gray-200 text-black"
                  }`}
                >
                  {message.isLoading ? (
                    <div className="flex items-center gap-2 text-sm text-gray-600 md:text-base">
                      <svg
                        className="h-5 w-5 animate-spin text-red-700"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      <span>Thinking...</span>
                    </div>
                  ) : (
                    <span className="block max-w-full whitespace-pre-wrap wrap-break-words text-sm md:text-base">
                      {handleChatLength(message.content)}
                    </span>
                  )}
                </div>

                {message.timestamp && !message.isLoading && (
                  <span className="mt-1 text-[10px] text-gray-500 dark:text-gray-400 px-1">
                    {formatTime(message.timestamp)}
                  </span>
                )}
              </div>
            </div>
          ))
        ) : (
          <h1 className="flex max-w-full flex-col px-4 text-center text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
            <span className="text-[#870e03] dark:text-[#e7a320]">
              Hello!
            </span>

            <br />

            <span className="mt-2 block text-xl font-medium sm:text-2xl md:text-3xl">
              <TypeAnimation
                sequence={[
                  "How can I help you today?",
                  2000,
                  "For more information, please contact: 0981.767.568",
                  5000,
                  "For more information, please contact: https://mit.vn/zalo",
                  5000,
                  "For more information, please contact: tuyensinh@mit.vn",
                  5000,
                  "For more information, please contact: https://tuyensinh.mit.vn",
                  5000,
                ]}
                speed={{
                  type: "keyStrokeDelayInMs",
                  value: 25,
                }}
                repeat={Infinity}
              />
            </span>
          </h1>
        )}
      </div>

      {previewImage && (
        <PreviewImage
          image={previewImage}
          onClose={() => setPreviewImage(null)}
        />
      )}
    </>
  );
}