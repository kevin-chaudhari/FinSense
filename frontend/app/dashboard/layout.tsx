"use client"

import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutDashboard,
  MessageSquare,
  CreditCard,
  BarChart3,
  Cpu,
  LogOut,
  Menu,
  X,
  Sparkles,
  ChevronRight,
} from "lucide-react"
import { authApi, clearTokens, getAccessToken, healthApi } from "@/lib/api"
import type { UserProfile, GPUStatus } from "@/types"

const navItems = [
  { path: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/dashboard/chat", icon: MessageSquare, label: "AI Chat" },
  { path: "/dashboard/transactions", icon: CreditCard, label: "Transactions" },
  { path: "/dashboard/analytics", icon: BarChart3, label: "Analytics" },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [gpuStatus, setGpuStatus] = useState<GPUStatus | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      router.replace("/login")
      return
    }

    authApi.me()
      .then(setUser)
      .catch(() => {
        clearTokens()
        router.replace("/login")
      })

    healthApi.gpu()
      .then(setGpuStatus)
      .catch(() => {})
  }, [router])

  const handleLogout = async () => {
    await authApi.logout()
    router.replace("/login")
  }

  return (
    <div className="flex h-screen overflow-hidden"
      style={{ background: "linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%)" }}
    >
      {/* Sidebar — Desktop */}
      <aside className="hidden md:flex flex-col w-64 shrink-0 border-r border-white/5"
        style={{ background: "rgba(10,10,20,0.8)", backdropFilter: "blur(24px)" }}
      >
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-6 h-16 border-b border-white/5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-display font-bold text-white">FinSense</span>
          <span className="badge-brand text-xs ml-1">AI</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.path || (item.path !== "/dashboard" && pathname.startsWith(item.path))
            return (
              <Link key={item.path} href={item.path}>
                <div className={`sidebar-item ${active ? "active" : ""}`}>
                  <item.icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                  {active && <ChevronRight className="w-3 h-3 ml-auto opacity-50" />}
                </div>
              </Link>
            )
          })}
        </nav>

        {/* GPU Status */}
        {gpuStatus && (
          <div className="px-4 py-3 mx-3 mb-3 rounded-xl"
            style={{ background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.15)" }}
          >
            <div className="flex items-center gap-2 mb-1">
              <Cpu className="w-3 h-3 text-violet-400" />
              <span className="text-xs font-medium text-violet-300">
                {gpuStatus.cuda_available ? "GPU Active" : "CPU Mode"}
              </span>
            </div>
            {gpuStatus.cuda_available && (
              <p className="text-xs text-gray-500 truncate">{gpuStatus.device_name}</p>
            )}
            <div className="flex gap-1 mt-1.5 flex-wrap">
              {gpuStatus.faiss_gpu && <span className="badge-brand text-xs">FAISS-GPU</span>}
              {gpuStatus.mixed_precision && <span className="badge-brand text-xs">FP16</span>}
            </div>
          </div>
        )}

        {/* User */}
        <div className="px-3 py-4 border-t border-white/5">
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl mb-2"
            style={{ background: "rgba(255,255,255,0.04)" }}
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white text-sm font-bold">
              {user?.username?.[0]?.toUpperCase() || "?"}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.display_name || user?.username}</p>
              <p className="text-xs text-gray-500">{user?.transaction_count ?? 0} transactions</p>
            </div>
          </div>
          <button onClick={handleLogout} className="sidebar-item w-full text-red-400 hover:text-red-300 hover:bg-red-500/10">
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 inset-x-0 z-50 flex items-center justify-between px-4 h-14 border-b border-white/5"
        style={{ background: "rgba(10,10,20,0.95)", backdropFilter: "blur(24px)" }}
      >
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-display font-bold text-white text-sm">FinSense</span>
        </div>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-gray-400 hover:text-white">
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, x: -280 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -280 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="md:hidden fixed inset-y-0 left-0 z-40 w-64 border-r border-white/5"
            style={{ background: "rgba(10,10,20,0.97)", backdropFilter: "blur(24px)" }}
          >
            <div className="pt-14">
              <nav className="flex-1 px-3 py-4 space-y-1">
                {navItems.map((item) => {
                  const active = pathname === item.path
                  return (
                    <Link key={item.path} href={item.path} onClick={() => setSidebarOpen(false)}>
                      <div className={`sidebar-item ${active ? "active" : ""}`}>
                        <item.icon className="w-4 h-4" />
                        <span>{item.label}</span>
                      </div>
                    </Link>
                  )
                })}
              </nav>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto md:pt-0 pt-14">
        <AnimatePresence mode="wait">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="min-h-full"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}
