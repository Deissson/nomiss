import React, { useState, useEffect, useRef } from "react";
import { API_URL } from "../config";

const CHAT_HISTORY_KEY = "nomiss_chat_history_v2";

interface Message {
    role: 'user' | 'ai';
    content: string;
    fileAttached?: boolean;
}

const ChatWidget: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [uploadedFile, setUploadedFile] = useState<{ base64: string; type: string } | null>(null);
    const historyRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const saved = localStorage.getItem(CHAT_HISTORY_KEY);
        if (saved) setMessages(JSON.parse(saved));
    }, []);

    useEffect(() => {
        localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages));
        if (historyRef.current) {
            historyRef.current.scrollTop = historyRef.current.scrollHeight;
        }
    }, [messages]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const base64 = (event.target?.result as string).split(",")[1];
            setUploadedFile({ base64, type: file.type });
        };
        reader.readAsDataURL(file);
    };

    const handleSend = async () => {
        if (!input.trim() && !uploadedFile) return;

        const userMsg: Message = {
            role: 'user',
            content: input,
            fileAttached: !!uploadedFile
        };

        setMessages(prev => [...prev, userMsg]);
        const currentInput = input;
        const currentFile = uploadedFile;

        setInput('');
        setUploadedFile(null);
        setIsTyping(true);

        try {
            const res = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: currentInput,
                    file_base64: currentFile?.base64,
                    file_type: currentFile?.type,
                }),
            });
            const data = await res.json();
            setMessages(prev => [...prev, { role: 'ai', content: data.reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'ai', content: "Connection Error" }]);
        } finally {
            setIsTyping(false);
        }
    };

    const clearChat = () => {
        if (window.confirm("Clear chat history?")) {
            setMessages([]);
            localStorage.removeItem(CHAT_HISTORY_KEY);
        }
    };

    return (
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl flex flex-col h-[500px] border border-blue-100 dark:border-gray-800 overflow-hidden">
            <div className="p-4 bg-blue-600 text-white flex justify-between items-center">
                <div>
                    <h3 className="font-bold">AI Tutor</h3>
                    <p className="text-[10px] opacity-80">Connected to your missed classes</p>
                </div>
                <button onClick={clearChat} className="text-xs bg-blue-500 hover:bg-blue-400 px-2 py-1 rounded transition-colors">Clear</button>
            </div>

            <div ref={historyRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <span className={`text-xs mb-1 font-bold ${msg.role === 'user' ? 'text-gray-600 dark:text-gray-400 mr-1' : 'text-blue-400 ml-1'}`}>
                            {msg.role === 'user' ? 'You' : 'AI Tutor'}
                        </span>
                        <div className={`p-4 rounded-2xl max-w-[85%] text-sm shadow-md whitespace-pre-wrap ${
                            msg.role === 'user'
                                ? 'bg-blue-600 text-white rounded-tr-sm'
                                : 'bg-blue-50 dark:bg-gray-800 border border-blue-200 dark:border-gray-700 text-gray-900 dark:text-gray-200 rounded-tl-sm'
                        }`}>
                            {msg.content}
                            {msg.fileAttached && <div className="mt-1 text-[10px] opacity-70">📎 File Attached</div>}
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="flex items-center gap-2 text-gray-400 text-xs italic ml-2">
                        <div className="flex gap-1">
                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                        </div>
                        Tutor is thinking...
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-gray-100 dark:border-gray-800">
                <div className="flex gap-2">
                    <label className={`cursor-pointer text-xs font-bold px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 transition-colors ${uploadedFile ? 'text-green-500' : 'text-gray-500'}`}>
                        {uploadedFile ? 'Attached' : 'Attach'}
                        <input type="file" className="hidden" onChange={handleFileChange} accept="image/*,application/pdf" />
                    </label>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about missed material..."
                        className="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg px-4 text-sm focus:ring-1 focus:ring-blue-500 outline-none"
                    />
                    <button
                        onClick={handleSend}
                        disabled={isTyping}
                        className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatWidget;
