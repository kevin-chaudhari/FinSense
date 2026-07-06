/**
 * FinSense AI — TypeScript Type Definitions
 */

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface UserProfile {
  user_id: string
  username: string
  display_name: string | null
  created_at: string
  transaction_count: number
}

// ── Transactions ──────────────────────────────────────────────────────────────

export type TransactionType = "credit" | "debit"

export interface Transaction {
  id: string
  amount: number
  transaction_type: TransactionType
  category: string
  description: string
  date: string
  created_at: string
  user_id: string
}

export interface TransactionCreatePayload {
  amount: number
  transaction_type: TransactionType
  category: string
  description: string
  date: string
}

export interface TransactionSummary {
  total_credit: number
  total_debit: number
  net: number
  transaction_count: number
  categories: Record<string, { credit: number; debit: number; count: number }>
  monthly_trend: Record<string, { credit: number; debit: number }>
}

// ── Agent ─────────────────────────────────────────────────────────────────────

export interface AgentQueryPayload {
  question: string
  conversation_id?: string
  stream?: boolean
}

export interface AgentQueryResult {
  response: string
  intent?: string
  conversation_id?: string
  sources?: string[]
  execution_time_ms?: number
  gpu_accelerated?: boolean
}

// ── Chat ──────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  intent?: string
  sources?: string[]
  execution_time_ms?: number
  gpu_accelerated?: boolean
  streaming?: boolean
}

// ── GPU ───────────────────────────────────────────────────────────────────────

export interface GPUStatus {
  cuda_available: boolean
  device_name?: string
  vram_gb: number
  faiss_gpu: boolean
  mixed_precision: boolean
}
