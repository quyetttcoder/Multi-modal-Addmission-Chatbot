"use client";
import React, { useRef, useState } from "react";
import { FaPlus } from "react-icons/fa6";
import { IoIosSend } from "react-icons/io";
import VoiceChat from "@/app/components/VoiceRecognite";

interface DialogProps {
    onSend: (message: string, files: File[]) => void;
    onNewVoiceMessage: (role: "user" | "assistant", text: string) => void; 
}

export default function Dialog({ onSend, onNewVoiceMessage }: DialogProps) {
    const [input, setInput] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [files, setFiles] = useState<{ file: File; preview: string }[]>([]);

    const handleChooseFile = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = Array.from(e.target.files || []);

        for (const file of selected) {
            if (!file.type.startsWith("image/")) {
                alert("Only image uploads are allowed.");
                e.target.value = "";
                return;
            }
        }

        const mapped = selected.map((file) => ({
            file,
            preview: URL.createObjectURL(file),
        }));

        setFiles((prev) => [...prev, ...mapped]);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const target = e.target;
        setInput(target.value);

        
        target.style.height = "0px";
        target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
    };

    const removeFile = (index: number) => {
        setFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const handleSend = () => {
        
        if (!input.trim() && files.length === 0) return;

        onSend(input, files.map(item => item.file));

        setInput("");
        setFiles([]);
        if (textareaRef.current) {
            textareaRef.current.style.height = "0px";
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="
          rounded-2xl md:rounded-3xl
          border border-gray-200
          bg-gray-50
          px-3 py-3 md:px-4 md:py-4
          shadow-lg
          dark:border-white/10
          dark:bg-[#2f2f2f]
          dark:shadow-2xl
          w-full
        ">
            {/* Preview image display area when a file is selected. */}
            <div className="flex flex-row gap-1 w-full">
                <div className="overflow-x-auto w-full no-scrollbar">
                    <div className="flex w-max gap-2 mb-2 md:mb-3">
                        {files.map((item, index) => (
                            <div
                                key={index}
                                className="relative w-16 h-16 sm:w-20 sm:h-20 shrink-0 rounded-xl border overflow-hidden bg-gray-100 dark:bg-neutral-800"
                            >
                                <button
                                    type="button"
                                    onClick={() => removeFile(index)}
                                    className="absolute top-1 right-1 w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-gray-200/80 text-gray-700 hover:bg-black/60 hover:text-white transition flex items-center justify-center text-xs z-10"
                                >
                                    ✕
                                </button>
                                <img
                                    src={item.preview}
                                    
                                    className="object-cover"
                                    alt="Preview"
                                    
                                />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            <textarea
                name="chat_input"
                id="chat"
                ref={textareaRef}
                value={input}
                onKeyDown={handleKeyDown}
                onChange={handleInputChange}
                rows={1}
                placeholder="Type your question here..."
                className="
                    block
                    mb-2 md:mb-3
                    w-full
                    px-1 md:px-2
                    resize-none
                    overflow-y-auto
                    bg-transparent
                    text-base md:text-lg
                    dark:text-white
                    placeholder:text-gray-400
                    focus:outline-none
                    not-dark:caret-black
                    min-h-7
                    max-h-40 md:max-h-50
                "
            />

            <div className="flex items-center justify-between pt-1">
                <div className="flex items-center">
                    <button
                        type="button"
                        onClick={handleChooseFile}
                        className="flex h-9 w-9 md:h-10 md:w-10 items-center justify-center rounded-full hover:bg-gray-200 dark:hover:bg-[#404040] transition hover:cursor-pointer"
                    >
                        <FaPlus className="text-xs md:text-sm text-black dark:text-white" />
                    </button>

                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        accept="image/*"
                        multiple
                        onChange={handleFileChange}
                    />
                </div>
                
                <div className="flex items-center gap-2 md:gap-3">
                    <div className="scale-90 md:scale-100 origin-right">
                        <VoiceChat onNewVoiceMessage={onNewVoiceMessage} />
                    </div>

                    <button 
                        onClick={handleSend}
                        className="flex h-8 w-8 md:h-9 md:w-9 items-center justify-center rounded-full bg-white border border-gray-200 dark:border-none hover:cursor-pointer shadow-sm active:scale-95 transition"
                    >
                        <IoIosSend className="text-black text-lg md:text-xl"/>
                    </button>
                </div>
            </div>
        </div>
    );
}