"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Plus, X, TrendingUp, TrendingDown, Filter } from "lucide-react"
import { transactionsApi } from "@/lib/api"
import type { Transaction, TransactionCreatePayload } from "@/types"
import { TRANSACTION_CATEGORIES, CATEGORY_COLORS } from "@/lib/constants"

function AddTransactionModal({
  onClose,
  onSuccess,
}: {
  onClose: () => void
  onSuccess: (tx: Transaction) => void
}) {
  const [form, setForm] = useState<TransactionCreatePayload>({
    amount: 0,
    transaction_type: "debit",
    category: "Food & Dining",
    description: "",
    date: new Date().toISOString(),
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    try {
      const tx = await transactionsApi.create(form)
      onSuccess(tx)
    } catch (err: any) {
      setError(err.message || "Failed to add transaction")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="relative w-full max-w-md rounded-2xl p-6"
        style={{ background: "rgba(15,15,26,0.98)", border: "1px solid rgba(99,102,241,0.2)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-display font-bold text-white text-lg">Add Transaction</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Amount */}
          <div>
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5 block">Amount ($)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={form.amount || ""}
              onChange={(e) => setForm((f) => ({ ...f, amount: parseFloat(e.target.value) || 0 }))}
              required
              className="w-full px-4 py-3 rounded-xl text-sm text-white focus:outline-none"
              style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
              placeholder="0.00"
            />
          </div>

          {/* Type */}
          <div>
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5 block">Type</label>
            <div className="flex rounded-xl overflow-hidden border border-white/10">
              {(["debit", "credit"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, transaction_type: t }))}
                  className={`flex-1 py-2.5 text-sm font-medium transition-all ${
                    form.transaction_type === t
                      ? t === "debit"
                        ? "bg-gradient-to-r from-red-600 to-rose-600 text-white"
                        : "bg-gradient-to-r from-emerald-600 to-teal-600 text-white"
                      : "text-gray-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {t === "debit" ? "Expense" : "Income"}
                </button>
              ))}
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5 block">Category</label>
            <select
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              className="w-full px-4 py-3 rounded-xl text-sm text-white focus:outline-none"
              style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
            >
              {TRANSACTION_CATEGORIES.map((c) => (
                <option key={c} value={c} style={{ background: "#1a1a2e" }}>{c}</option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5 block">Description</label>
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              required
              className="w-full px-4 py-3 rounded-xl text-sm text-white focus:outline-none"
              style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
              placeholder="e.g., Lunch at Subway"
            />
          </div>

          {/* Date */}
          <div>
            <label className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1.5 block">Date</label>
            <input
              type="datetime-local"
              value={form.date.slice(0, 16)}
              onChange={(e) => setForm((f) => ({ ...f, date: new Date(e.target.value).toISOString() }))}
              className="w-full px-4 py-3 rounded-xl text-sm text-white focus:outline-none"
              style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", colorScheme: "dark" }}
            />
          </div>

          {error && (
            <p className="text-red-400 text-xs px-1">{error}</p>
          )}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-ghost flex-1">Cancel</button>
            <button type="submit" disabled={loading} className="btn-brand flex-1">
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto" />
              ) : "Add Transaction"}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [filterType, setFilterType] = useState<"" | "credit" | "debit">("")

  const pageSize = 20

  const loadTransactions = async (p = 1) => {
    setLoading(true)
    try {
      const data = await transactionsApi.list({
        page: p,
        page_size: pageSize,
        transaction_type: filterType || undefined,
      })
      setTransactions(data.transactions)
      setTotal(data.total)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTransactions(page)
  }, [page, filterType])

  const handleNewTransaction = (tx: Transaction) => {
    setShowModal(false)
    setTransactions((prev) => [tx, ...prev])
    setTotal((t) => t + 1)
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl font-bold text-white">Transactions</h1>
          <p className="text-gray-400 text-sm mt-1">{total} total transactions</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-brand">
          <Plus className="w-4 h-4" /> Add Transaction
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <Filter className="w-4 h-4 text-gray-500" />
        <div className="flex rounded-xl overflow-hidden border border-white/10">
          {(["", "debit", "credit"] as const).map((t) => (
            <button
              key={t}
              onClick={() => { setFilterType(t); setPage(1) }}
              className={`px-4 py-2 text-xs font-medium transition-all ${
                filterType === t
                  ? "bg-gradient-to-r from-violet-600 to-indigo-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {t === "" ? "All" : t === "debit" ? "Expenses" : "Income"}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="premium-card overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="flex justify-between items-center">
                <div className="space-y-1.5">
                  <div className="skeleton h-3 w-40 rounded" />
                  <div className="skeleton h-2.5 w-24 rounded" />
                </div>
                <div className="skeleton h-4 w-16 rounded" />
              </div>
            ))}
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/10 to-indigo-500/10 flex items-center justify-center mb-4">
              <TrendingUp className="w-8 h-8 text-violet-400" />
            </div>
            <p className="text-gray-400 font-medium mb-1">No transactions yet</p>
            <p className="text-gray-600 text-sm mb-4">Add your first transaction to get started</p>
            <button onClick={() => setShowModal(true)} className="btn-brand text-sm px-5 py-2.5">
              <Plus className="w-4 h-4" /> Add Transaction
            </button>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="text-left px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Category</th>
                <th className="text-left px-4 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Date</th>
                <th className="text-right px-6 py-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {transactions.map((tx, i) => {
                const color = CATEGORY_COLORS[tx.category] || "#94a3b8"
                return (
                  <motion.tr
                    key={tx.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="group hover:bg-white/2 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                        <div>
                          <p className="text-sm font-medium text-white">{tx.description}</p>
                          <p className="text-xs text-gray-500 sm:hidden">{tx.category}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 hidden sm:table-cell">
                      <span className="text-xs text-gray-400">{tx.category}</span>
                    </td>
                    <td className="px-4 py-4 hidden md:table-cell">
                      <span className="text-xs text-gray-500">
                        {new Date(tx.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`text-sm font-semibold ${tx.transaction_type === "credit" ? "text-emerald-400" : "text-red-400"}`}>
                        <span className="mr-0.5">{tx.transaction_type === "credit" ? "+" : "-"}</span>
                        ${tx.amount.toFixed(2)}
                      </span>
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-500">
            Page {page} of {totalPages} ({total} results)
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn-ghost px-4 py-2 text-xs disabled:opacity-40"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="btn-ghost px-4 py-2 text-xs disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Add Modal */}
      {showModal && (
        <AddTransactionModal onClose={() => setShowModal(false)} onSuccess={handleNewTransaction} />
      )}
    </div>
  )
}
