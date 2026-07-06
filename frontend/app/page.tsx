"use client"

import Link from "next/link"
import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import {
  Brain,
  TrendingUp,
  MessageSquare,
  BarChart3,
  Zap,
  Shield,
  Cpu,
  ArrowRight,
  Sparkles,
  Database,
  GitBranch,
} from "lucide-react"

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.1 },
  },
}
const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] } },
}

const features = [
  {
    icon: Brain,
    title: "LangGraph AI Agents",
    description: "Multi-agent orchestration with typed state, intent classification, and tool-calling.",
    color: "from-violet-500 to-indigo-500",
    badge: "Core AI",
  },
  {
    icon: Database,
    title: "Hybrid RAG Pipeline",
    description: "BM25 + dense retrieval with FAISS vector search and cross-encoder reranking.",
    color: "from-cyan-500 to-blue-500",
    badge: "RAG",
  },
  {
    icon: Cpu,
    title: "CUDA GPU Acceleration",
    description: "GPU-accelerated embeddings, FAISS index build and search with automatic CPU fallback.",
    color: "from-emerald-500 to-teal-500",
    badge: "Performance",
  },
  {
    icon: MessageSquare,
    title: "Streaming AI Chat",
    description: "Real-time SSE streaming responses with persistent conversation memory.",
    color: "from-pink-500 to-rose-500",
    badge: "Chat",
  },
  {
    icon: BarChart3,
    title: "Financial Analytics",
    description: "Interactive charts: spending trends, category breakdown, monthly analysis.",
    color: "from-amber-500 to-orange-500",
    badge: "Analytics",
  },
  {
    icon: Shield,
    title: "Production Security",
    description: "JWT authentication, bcrypt hashing, rate limiting, input sanitization.",
    color: "from-red-500 to-pink-500",
    badge: "Security",
  },
]

const stats = [
  { label: "Agent Nodes", value: "4", suffix: "" },
  { label: "GPU Speedup", value: "22", suffix: "×" },
  { label: "API Routes", value: "12", suffix: "+" },
  { label: "Cache Hit Rate", value: "94", suffix: "%" },
]

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.08, ease: [0.25, 0.46, 0.45, 0.94] }}
      className="group relative premium-card p-6 hover:scale-[1.02] transition-transform duration-300"
    >
      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      <div className="relative">
        <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.color} mb-4`}>
          <feature.icon className="w-5 h-5 text-white" />
        </div>
        <span className="badge-brand absolute top-0 right-0">{feature.badge}</span>
        <h3 className="font-display font-semibold text-gray-900 dark:text-white mb-2">{feature.title}</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{feature.description}</p>
      </div>
    </motion.div>
  )
}

export default function LandingPage() {
  const heroRef = useRef(null)
  const heroInView = useInView(heroRef, { once: true })

  return (
    <div className="min-h-screen overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%)" }}
    >
      {/* Navigation */}
      <nav className="fixed top-0 inset-x-0 z-50 border-b border-white/5"
        style={{ backdropFilter: "blur(24px)", background: "rgba(15,15,26,0.8)" }}
      >
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-white text-lg">FinSense</span>
            <span className="badge-brand text-xs">AI</span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</Link>
            <Link href="#tech" className="text-sm text-gray-400 hover:text-white transition-colors">Technology</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="btn-ghost text-white border-white/10 hover:border-white/20">
              Sign In
            </Link>
            <Link href="/login" className="btn-brand">
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center pt-16">
        {/* Background effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-[120px] animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-indigo-600/20 rounded-full blur-[100px] animate-float" style={{ animationDelay: "1.5s" }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-900/10 rounded-full blur-[150px]" />
          {/* Grid */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:64px_64px]" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={heroInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="relative text-center max-w-4xl mx-auto px-6"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={heroInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-violet-500/30 bg-violet-500/10 text-violet-300 text-sm font-medium mb-8"
          >
            <Zap className="w-3.5 h-3.5" />
            Powered by LangGraph + Gemini + CUDA
          </motion.div>

          <h1 className="font-display text-6xl md:text-7xl lg:text-8xl font-black text-white leading-[1.05] tracking-tight mb-6">
            Your AI{" "}
            <span className="gradient-text animate-gradient-shift">Finance</span>
            {" "}Co-Pilot
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Production-grade AI financial platform with LangGraph multi-agent orchestration,
            GPU-accelerated FAISS retrieval, and real-time streaming insights.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/login" className="btn-brand text-base px-8 py-4">
              Start for Free <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="https://github.com"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-sm font-medium text-gray-300 border border-white/10 hover:border-white/20 hover:text-white transition-all"
            >
              <GitBranch className="w-4 h-4" />
              View on GitHub
            </Link>
          </div>

          {/* Stats row */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate={heroInView ? "show" : "hidden"}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-2xl mx-auto"
          >
            {stats.map((stat) => (
              <motion.div key={stat.label} variants={itemVariants} className="text-center">
                <div className="font-display text-3xl font-black gradient-text">
                  {stat.value}{stat.suffix}
                </div>
                <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* Features */}
      <section id="features" className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
              Built for{" "}
              <span className="gradient-text">Production</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Every architectural decision made for scale, security, and performance.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            style={{ filter: "brightness(1.05)" }}
          >
            {features.map((feature, i) => (
              <FeatureCard key={feature.title} feature={feature} index={i} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-32 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="relative rounded-3xl overflow-hidden p-12"
            style={{ background: "linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.1) 100%)", border: "1px solid rgba(99,102,241,0.2)" }}
          >
            <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.04)_1px,transparent_1px)] bg-[size:32px_32px]" />
            <div className="relative">
              <h2 className="font-display text-4xl font-bold text-white mb-4">
                Start managing smarter
              </h2>
              <p className="text-gray-400 mb-8">
                Join the future of personal finance with AI that actually understands your money.
              </p>
              <Link href="/login" className="btn-brand text-base px-10 py-4 inline-flex">
                Get Started Free <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="w-3 h-3 text-white" />
            </div>
            <span className="text-sm text-gray-500">FinSense AI v2.0</span>
          </div>
          <p className="text-sm text-gray-600">© 2025 Kevinkumar Chaudhari. MIT License.</p>
        </div>
      </footer>
    </div>
  )
}
