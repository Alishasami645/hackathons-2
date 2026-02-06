"use client";

import { useState, useRef, useEffect, useCallback } from "react";

type Message = {
  role: "user" | "bot";
  text: string;
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", text: "Hello 👋 How can I help you today?" }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Send message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage: Message = { role: "user", text: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/chat/YOUR_USER_ID/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userMessage.text }),
        }
      );
      const data = await res.json();
      setMessages(prev => [...prev, { role: "bot", text: data.message }]);
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "❌ Server error" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] p-4 bg-gray-50 rounded">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-2 rounded max-w-[70%] ${
              m.role === "user"
                ? "bg-blue-500 text-white ml-auto"
                : "bg-white text-black"
            }`}
          >
            {m.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="flex gap-2 mt-2">
        <input
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 border rounded px-2"
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-3 rounded"
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}
