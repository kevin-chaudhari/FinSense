"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
  CreditCard,
} from "lucide-react"
import Link from "next/link"
import { transactionsApi } from "@/lib/api"
import type { TransactionSummary, Transaction } from "@/types"
import { CATEGORY_COLORS } from "@/lib/constants"

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

function MetricCard({
  label,
  value,
  subtext,
  icon: Icon,
  trend,
  color,
  delay,
}: {
  label: string
  value: string
  subtext?: string
  icon: React.ElementType
  trend?: "up" | "down" | "neutral"
  color: string
  delay?: number
}) {
  return (
    <motion.div
      variants={itemVariants}
      transition={{ delay }}
      className="metric-card"
    >
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl ${color}`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          {trend && trend !== "neutral" && (
            <div className={trend === "up" ? "badge-success" : "badge-danger"}>
              {trend === "up" ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
              {trend === "up" ? "Credit" : "Debit"}
            </div>
          )}
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{label}</p>
        <p className="font-display text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
      </div>
    </motion.div>
  )
}

function SkeletonMetric() {
  return (
    <div className="premium-card p-6">
      <div className="skeleton h-12 w-12 rounded-xl mb-4" />
      <div className="skeleton h-3 w-20 rounded mb-2" />
      <div className="skeleton h-7 w-32 rounded" />
    </div>
  )
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<TransactionSummary | null>(null)
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [summaryData, txData] = await Promise.all([
          transactionsApi.summary(),
          transactionsApi.list({ page: 1, page_size: 5 }),
        ])
        setSummary(summaryData)
        setRecentTransactions(txData.transactions)
      } catch (err) {
        console.error("Dashboard load error:", err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const netPositive = (summary?.net ?? 0) >= 0

  return (
    <div className="page-container">
      <motion.div
        initial="hidden"
        animate="show"
        variants={{ show: { transition: { staggerChildren: 0.08 } } }}
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="mb-8">
          <h1 className="font-display text-3xl font-bold text-white mb-1">Dashboard</h1>
          <p className="text-gray-400 text-sm">Your financial overview at a glance</p>
        </motion.div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => <SkeletonMetric key={i} />)
          ) : (
            <>
              <MetricCard
                label="Total Income"
                value={`$${summary?.total_credit.toFixed(2) ?? "0.00"}`}
                subtext="All credits"
                icon={TrendingUp}
                trend="up"
                color="bg-gradient-to-br from-emerald-500 to-teal-600"
                delay={0}
              />
              <MetricCard
                label="Total Expenses"
                value={`$${summary?.total_debit.toFixed(2) ?? "0.00"}`}
                subtext="All debits"
                icon={TrendingDown}
                trend="down"
                color="bg-gradient-to-br from-red-500 to-rose-600"
                delay={0.05}
              />
              <MetricCard
                label="Net Balance"
                value={`${netPositive ? "+" : ""}$${summary?.net.toFixed(2) ?? "0.00"}`}
                subtext={netPositive ? "Positive balance" : "Deficit"}
                icon={DollarSign}
                trend="neutral"
                color={netPositive ? "bg-gradient-to-br from-violet-500 to-indigo-600" : "bg-gradient-to-br from-orange-500 to-amber-600"}
                delay={0.1}
              />
              <MetricCard
                label="Transactions"
                value={String(summary?.transaction_count ?? 0)}
                subtext="Total recorded"
                icon={Activity}
                trend="neutral"
                color="bg-gradient-to-br from-cyan-500 to-blue-600"
                delay={0.15}
              />
            </>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Category Breakdown */}
          <motion.div variants={itemVariants} className="premium-card p-6 lg:col-span-2">
            <h2 className="section-title text-white mb-5">Spending by Category</h2>
            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="skeleton h-3 w-3 rounded-full" />
                    <div className="skeleton h-3 flex-1 rounded" />
                    <div className="skeleton h-3 w-16 rounded" />
                  </div>
                ))}
              </div>
            ) : !summary || Object.keys(summary.categories).length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <CreditCard className="w-12 h-12 text-gray-600 mb-3" />
                <p className="text-gray-400 text-sm">No transactions yet</p>
                <Link href="/dashboard/transactions" className="btn-brand mt-4 text-xs px-4 py-2">
                  Add Transaction
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {Object.entries(summary.categories)
                  .sort((a, b) => (b[1].debit + b[1].credit) - (a[1].debit + a[1].credit))
                  .slice(0, 8)
                  .map(([cat, data]) => {
                    const total = data.debit + data.credit
                    const maxTotal = Math.max(
                      ...Object.values(summary.categories).map((d) => d.debit + d.credit)
                    )
                    const pct = maxTotal > 0 ? (total / maxTotal) * 100 : 0
                    const color = CATEGORY_COLORS[cat] || "#94a3b8"
                    return (
                      <div key={cat} className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: color }} />
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-baseline mb-1">
                            <span className="text-sm text-gray-300 truncate">{cat}</span>
                            <span className="text-sm font-medium text-white ml-2">${total.toFixed(0)}</span>
                          </div>
                          <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                            <div className="h-full rounded-full transition-all duration-700"
                              style={{ width: `${pct}%`, background: color, opacity: 0.8 }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}
          </motion.div>

          {/* Recent Transactions + Quick Actions */}
          <motion.div variants={itemVariants} className="space-y-4">
            {/* Quick Actions */}
            <div className="premium-card p-5">
              <h2 className="section-title text-white mb-4 text-base">Quick Actions</h2>
              <div className="space-y-2">
                <Link href="/dashboard/chat" className="block">
                  <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer border border-white/5 hover:border-violet-500/30">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">Ask AI</p>
                      <p className="text-xs text-gray-500">Chat with your financial data</p>
                    </div>
                  </div>
                </Link>
                <Link href="/dashboard/transactions" className="block">
                  <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer border border-white/5 hover:border-emerald-500/30">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                      <CreditCard className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">Add Transaction</p>
                      <p className="text-xs text-gray-500">Log income or expense</p>
                    </div>
                  </div>
                </Link>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="premium-card p-5">
              <h2 className="section-title text-white mb-4 text-base">Recent</h2>
              {loading ? (
                <div className="space-y-3">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="flex justify-between">
                      <div className="skeleton h-3 w-24 rounded" />
                      <div className="skeleton h-3 w-12 rounded" />
                    </div>
                  ))}
                </div>
              ) : recentTransactions.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-4">No recent transactions</p>
              ) : (
                <div className="space-y-2.5">
                  {recentTransactions.map((tx) => (
                    <div key={tx.id} className="flex items-center justify-between">
                      <div className="min-w-0">
                        <p className="text-sm text-gray-200 truncate">{tx.description}</p>
                        <p className="text-xs text-gray-500">{tx.category}</p>
                      </div>
                      <span className={`text-sm font-semibold ml-3 ${tx.transaction_type === "credit" ? "text-emerald-400" : "text-red-400"}`}>
                        {tx.transaction_type === "credit" ? "+" : "-"}${tx.amount.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}
