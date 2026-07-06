"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Send,
  Bot,
  User,
  Zap,
  Brain,
  Cpu,
  RefreshCw,
  ChevronDown,
  Sparkles,
} from "lucide-react"
import { agentApi } from "@/lib/api"
import type { ChatMessage, AgentQueryResult } from "@/types"
import { EXAMPLE_QUESTIONS } from "@/lib/constants"

let messageIdCounter = 0
const newId = () => `msg_${++messageIdCounter}`

function TypingIndicator() {
  return (
    <div className="flex items-end gap-3">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shrink-0">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="chat-bubble-ai flex items-center gap-1 py-3">
        {[0, 0.15, 0.3].map((delay, i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-violet-400"
            style={{ animation: `bounce 1.2s ${delay}s infinite` }}
          />
        ))}
      </div>
    </div>
  )
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user"
  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={`flex items-end gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
        isUser
          ? "bg-gradient-to-br from-cyan-500 to-blue-600"
          : "bg-gradient-to-br from-violet-500 to-indigo-600"
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>

      {/* Bubble */}
      <div className={`flex flex-col gap-1 ${isUser ? "items-end" : "items-start"}`}>
        <div className={isUser ? "chat-bubble-user" : "chat-bubble-ai"}>
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
        </div>

        {/* Meta */}
        {!isUser && (msg.intent || msg.execution_time_ms || msg.gpu_accelerated) && (
          <div className="flex items-center gap-2 px-1">
            {msg.intent && (
              <span className="badge-brand text-xs flex items-center gap-1">
                <Brain className="w-2.5 h-2.5" />
                {msg.intent.replace("_", " ")}
              </span>
            )}
            {msg.execution_time_ms && (
              <span className="text-xs text-gray-500">{msg.execution_time_ms.toFixed(0)}ms</span>
            )}
            {msg.gpu_accelerated && (
              <span className="badge-success text-xs flex items-center gap-1">
                <Cpu className="w-2.5 h-2.5" />
                GPU
              </span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: newId(),
      role: "assistant",
      content: "👋 Hi! I'm your FinSense AI assistant. Ask me about your spending, budget analysis, or any financial question.\n\nI use your actual transaction data for personalized answers!",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>()
  const [streamingContent, setStreamingContent] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [showScrollBtn, setShowScrollBtn] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  useEffect(() => {
    if (!isStreaming) scrollToBottom()
  }, [messages, isStreaming])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const onScroll = () => {
      const distFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight
      setShowScrollBtn(distFromBottom > 200)
    }
    container.addEventListener("scroll", onScroll)
    return () => container.removeEventListener("scroll", onScroll)
  }, [])

  const sendMessage = async (text?: string) => {
    const question = (text || input).trim()
    if (!question || loading) return

    setInput("")
    setLoading(true)

    const userMsg: ChatMessage = {
      id: newId(),
      role: "user",
      content: question,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])

    try {
      setIsStreaming(true)
      setStreamingContent("")
      let fullContent = ""
      let meta: Partial<AgentQueryResult> = {}

      await agentApi.queryStream(
        { question, conversation_id: conversationId, stream: true },
        (token) => {
          fullContent += token
          setStreamingContent(fullContent)
        },
        (doneMeta) => {
          meta = doneMeta
          if (doneMeta.conversation_id) setConversationId(doneMeta.conversation_id)
        },
        (err) => {
          fullContent = `❌ Error: ${err}`
          setStreamingContent(fullContent)
        }
      )

      const aiMsg: ChatMessage = {
        id: newId(),
        role: "assistant",
        content: fullContent || "No response generated.",
        timestamp: new Date(),
        intent: meta.intent,
        execution_time_ms: meta.execution_time_ms,
        gpu_accelerated: meta.gpu_accelerated,
        sources: meta.sources,
      }
      setMessages((prev) => [...prev, aiMsg])

    } catch (err) {
      setMessages((prev) => [...prev, {
        id: newId(),
        role: "assistant",
        content: "❌ Something went wrong. Please try again.",
        timestamp: new Date(),
      }])
    } finally {
      setIsStreaming(false)
      setStreamingContent("")
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const clearChat = () => {
    setMessages([{
      id: newId(),
      role: "assistant",
      content: "Chat cleared. How can I help you?",
      timestamp: new Date(),
    }])
    setConversationId(undefined)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full" style={{ maxHeight: "calc(100vh - 0px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center animate-pulse-glow">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-display font-bold text-white">AI Financial Advisor</h1>
            <p className="text-xs text-gray-500">Powered by LangGraph + Gemini + CUDA</p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-white/5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Clear
        </button>
      </div>

      {/* Messages */}
      <div ref={containerRef} className="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-5">
        <AnimatePresence>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
        </AnimatePresence>

        {/* Streaming bubble */}
        {isStreaming && (
          <div className="flex items-end gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="chat-bubble-ai max-w-[75%]">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {streamingContent}
                <span className="inline-block w-2 h-4 bg-violet-400 ml-0.5 animate-pulse rounded-sm" />
              </p>
            </div>
          </div>
        )}

        {loading && !isStreaming && <TypingIndicator />}

        {/* Example questions (when no user messages) */}
        {messages.length === 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-2"
          >
            <p className="text-xs text-gray-500 text-center">Try asking:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {EXAMPLE_QUESTIONS.slice(0, 4).map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-xs px-3 py-2 rounded-xl border border-white/10 text-gray-300 hover:text-white hover:border-violet-500/40 hover:bg-violet-500/10 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Scroll to bottom */}
      <AnimatePresence>
        {showScrollBtn && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={scrollToBottom}
            className="absolute bottom-24 right-6 p-2 rounded-full border border-white/10 bg-black/50 backdrop-blur-sm text-gray-400 hover:text-white transition-colors"
          >
            <ChevronDown className="w-4 h-4" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="px-4 md:px-6 py-4 border-t border-white/5 shrink-0">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your finances… (Enter to send, Shift+Enter for newline)"
              disabled={loading}
              rows={1}
              className="w-full resize-none px-4 py-3 pr-12 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none transition-all duration-200 disabled:opacity-50"
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                minHeight: "48px",
                maxHeight: "120px",
              }}
              onFocus={(e) => e.target.style.borderColor = "rgba(99,102,241,0.5)"}
              onBlur={(e) => e.target.style.borderColor = "rgba(255,255,255,0.1)"}
              onInput={(e) => {
                const t = e.target as HTMLTextAreaElement
                t.style.height = "auto"
                t.style.height = Math.min(t.scrollHeight, 120) + "px"
              }}
            />
          </div>
          <motion.button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="btn-brand p-3 aspect-square flex-shrink-0"
            whileTap={{ scale: 0.95 }}
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </motion.button>
        </div>
        <p className="text-xs text-gray-600 mt-2 text-center">
          <Zap className="w-2.5 h-2.5 inline mr-1" />
          LangGraph agents · Hybrid RAG · GPU-accelerated
        </p>
      </div>

      <style jsx>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  )
}
