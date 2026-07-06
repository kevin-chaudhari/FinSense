"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"
import { transactionsApi } from "@/lib/api"
import type { TransactionSummary } from "@/types"
import { CHART_COLORS, CATEGORY_COLORS } from "@/lib/constants"

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] }
  }),
}

function ChartCard({ title, children, custom }: { title: string; children: React.ReactNode; custom?: number }) {
  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="show"
      custom={custom ?? 0}
      className="premium-card p-6"
    >
      <h3 className="font-display font-semibold text-white mb-5">{title}</h3>
      {children}
    </motion.div>
  )
}

const tooltipStyle = {
  backgroundColor: "rgba(15,15,26,0.95)",
  border: "1px solid rgba(99,102,241,0.2)",
  borderRadius: "12px",
  color: "white",
}

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<TransactionSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    transactionsApi.summary()
      .then(setSummary)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="page-container">
        <div className="mb-8">
          <div className="skeleton h-8 w-40 rounded mb-2" />
          <div className="skeleton h-4 w-56 rounded" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="premium-card p-6">
              <div className="skeleton h-5 w-32 rounded mb-5" />
              <div className="skeleton h-48 rounded" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!summary || summary.transaction_count === 0) {
    return (
      <div className="page-container flex flex-col items-center justify-center min-h-[60vh] text-center">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500/10 to-indigo-500/10 flex items-center justify-center mb-4">
          <span className="text-4xl">📊</span>
        </div>
        <h2 className="font-display text-2xl font-bold text-white mb-2">No data yet</h2>
        <p className="text-gray-400 mb-6">Add transactions to see your financial analytics.</p>
      </div>
    )
  }

  // Prepare chart data
  const categoryData = Object.entries(summary.categories)
    .map(([cat, data]) => ({
      name: cat,
      expenses: data.debit,
      income: data.credit,
      total: data.debit + data.credit,
      fill: CATEGORY_COLORS[cat] || "#94a3b8",
    }))
    .sort((a, b) => b.total - a.total)

  const pieData = categoryData.slice(0, 8).map((d, i) => ({
    name: d.name,
    value: d.total,
    fill: CHART_COLORS[i % CHART_COLORS.length],
  }))

  const monthlyData = Object.entries(summary.monthly_trend)
    .sort()
    .map(([month, data]) => ({
      month: new Date(month + "-01").toLocaleDateString("en-US", { month: "short", year: "2-digit" }),
      income: data.credit,
      expenses: data.debit,
      net: data.credit - data.debit,
    }))

  const radarData = categoryData.slice(0, 6).map((d) => ({
    category: d.name.split(" ")[0],
    value: d.total,
  }))

  return (
    <div className="page-container">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold text-white">Analytics</h1>
        <p className="text-gray-400 text-sm mt-1">
          Visual breakdown of {summary.transaction_count} transactions
        </p>
      </div>

      {/* Summary Row */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="premium-card p-4 text-center">
          <p className="text-emerald-400 font-display text-2xl font-bold">${summary.total_credit.toFixed(0)}</p>
          <p className="text-gray-500 text-xs mt-1">Total Income</p>
        </div>
        <div className="premium-card p-4 text-center">
          <p className="text-red-400 font-display text-2xl font-bold">${summary.total_debit.toFixed(0)}</p>
          <p className="text-gray-500 text-xs mt-1">Total Expenses</p>
        </div>
        <div className={`premium-card p-4 text-center`}>
          <p className={`font-display text-2xl font-bold ${summary.net >= 0 ? "text-violet-400" : "text-amber-400"}`}>
            {summary.net >= 0 ? "+" : ""}${summary.net.toFixed(0)}
          </p>
          <p className="text-gray-500 text-xs mt-1">Net Balance</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <ChartCard title="Spending by Category" custom={0}>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categoryData.slice(0, 8)} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#6b7280" }} tickLine={false} axisLine={false}
                tickFormatter={(v) => v.split(" ")[0]}
              />
              <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} tickLine={false} axisLine={false}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`$${v.toFixed(2)}`]} />
              <Bar dataKey="expenses" name="Expenses" radius={[4, 4, 0, 0]}>
                {categoryData.slice(0, 8).map((entry, i) => (
                  <Cell key={i} fill={entry.fill} fillOpacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Pie / Donut Chart */}
        <ChartCard title="Expense Distribution" custom={1}>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} fillOpacity={0.85} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`$${v.toFixed(2)}`]} />
              <Legend
                formatter={(v) => <span style={{ color: "#9ca3af", fontSize: 11 }}>{v}</span>}
                iconType="circle"
                iconSize={8}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Monthly Trend */}
        {monthlyData.length > 0 && (
          <ChartCard title="Monthly Trend" custom={2}>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#6b7280" }} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} tickLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`$${v.toFixed(2)}`]} />
                <Legend formatter={(v) => <span style={{ color: "#9ca3af", fontSize: 11 }}>{v}</span>} />
                <Line type="monotone" dataKey="income" name="Income" stroke="#10b981" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="expenses" name="Expenses" stroke="#ef4444" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="net" name="Net" stroke="#6366f1" strokeWidth={2} strokeDasharray="4 2" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        )}

        {/* Radar Chart */}
        {radarData.length >= 3 && (
          <ChartCard title="Spending Pattern Radar" custom={3}>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="category" tick={{ fontSize: 11, fill: "#9ca3af" }} />
                <Radar
                  name="Spending"
                  dataKey="value"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`$${v.toFixed(2)}`]} />
              </RadarChart>
            </ResponsiveContainer>
          </ChartCard>
        )}
      </div>
    </div>
  )
}
