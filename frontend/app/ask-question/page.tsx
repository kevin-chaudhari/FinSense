"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { FiSend, FiUser } from "react-icons/fi";

type Message = {
  role: "user" | "bot";
  content: string;
};

export default function AskQuestion() {
  const [sessionActive, setSessionActive] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Optionally: Check if already logged in
  useEffect(() => {
    fetch("http://127.0.0.1:5000/current_user", {
      method: "GET",
      credentials: "include",
    })
      .then((res) => res.ok && setSessionActive(true))
      .catch(() => setSessionActive(false));
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) {
      toast.warning("Please enter a message");
      return;
    }

    const newMessage: Message = { role: "user", content: inputMessage.trim() };
    setMessages((prev) => [...prev, newMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/agentic_query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ question: inputMessage.trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages((prev) => [
          ...prev,
          { role: "bot", content: data.response || "Sorry, I couldn't generate a response." },
        ]);
      } else {
        toast.error(data.error || "Something went wrong");
      }
    } catch {
      toast.error("Server error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUserIdSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const userIdInput = form.elements.namedItem("userId") as HTMLInputElement;
    const inputVal = userIdInput.value.trim();

    if (!inputVal) return;

    try {
      const loginResponse = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ user_id: inputVal }),
      });

      const result = await loginResponse.json();

      if (!loginResponse.ok) {
        toast.error(result.error || "Login failed");
        return;
      }

      setSessionActive(true);
      setMessages([{ role: "bot", content: "Hello! How can I assist you today?" }]);
    } catch (err) {
      toast.error("Login request failed");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <motion.h1
        className="text-4xl font-bold mb-8 text-center text-indigo-800 dark:text-indigo-200"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        Ask a Question
      </motion.h1>

      {!sessionActive ? (
        <motion.form
          onSubmit={handleUserIdSubmit}
          className="card p-8 bg-white dark:bg-gray-800 shadow-lg rounded-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-6">
            <label htmlFor="userId" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              <FiUser className="inline-block mr-2" />
              Enter User ID
            </label>
            <input
              id="userId"
              name="userId"
              type="text"
              required
              className="input w-full mt-2"
              placeholder="e.g., user_123"
            />
          </div>
          <button
            type="submit"
            className="btn bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Start Chat
          </button>
        </motion.form>
      ) : (
        <motion.div
          className="card p-6 bg-white dark:bg-gray-800 shadow-lg rounded-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div
            ref={chatContainerRef}
            className="h-96 overflow-y-auto mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-md space-y-3"
          >
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`w-fit max-w-xs px-4 py-2 rounded-lg shadow ${
                    msg.role === "user"
                      ? "ml-auto bg-indigo-600 text-white"
                      : "mr-auto bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-200"
                  }`}
                >
                  {msg.content}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              className="input flex-grow"
              placeholder="Type your message here..."
              disabled={isLoading}
            />
            <motion.button
              type="submit"
              disabled={isLoading}
              className="btn bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FiSend />
              {isLoading ? "Sending..." : "Send"}
            </motion.button>
          </form>
        </motion.div>
      )}

      <ToastContainer position="bottom-right" autoClose={3000} />
    </div>
  );
}
