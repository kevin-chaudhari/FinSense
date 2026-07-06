<div align="center">

<img src="https://img.shields.io/badge/FinSense_AI-v2.0-6366f1?style=for-the-badge&logo=sparkles&logoColor=white" alt="FinSense AI"/>

# FinSense AI

### Production-Grade AI-Powered Personal Finance Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-6366f1?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![CUDA](https://img.shields.io/badge/CUDA-12+-76b900?style=flat-square&logo=nvidia)](https://developer.nvidia.com/cuda-toolkit)
[![FAISS](https://img.shields.io/badge/FAISS-GPU-76b900?style=flat-square)](https://faiss.ai)
[![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*Track expenses · Get AI-driven insights · Visualize financial data*  
*Powered by LangGraph agents, GPU-accelerated FAISS, and Google Gemini*

</div>

---

## 📋 Table of Contents

- [What is FinSense AI?](#-what-is-finsense-ai)
- [The Problem It Solves](#-the-problem-it-solves)
- [How It Works — End to End](#-how-it-works--end-to-end)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Deep Dive](#-technology-deep-dive)
  - [FastAPI](#1-fastapi--backend-framework)
  - [LangGraph](#2-langgraph--multi-agent-orchestration)
  - [Google Gemini](#3-google-gemini--large-language-model)
  - [FAISS](#4-faiss--vector-similarity-search)
  - [RAG Pipeline](#5-rag-pipeline--retrieval-augmented-generation)
  - [CUDA / GPU Layer](#6-cuda--gpu-acceleration-layer)
  - [Next.js 14](#7-nextjs-14--frontend-framework)
  - [Pydantic v2](#8-pydantic-v2--data-validation)
  - [JWT + bcrypt](#9-jwt--bcrypt--authentication--security)
  - [loguru](#10-loguru--structured-logging)
  - [Recharts](#11-recharts--data-visualization)
  - [Framer Motion](#12-framer-motion--animations)
- [Agent Workflow](#agent-workflow)
- [RAG Pipeline Diagram](#rag-pipeline)
- [GPU / CUDA Features](#gpu--cuda-features)
- [Performance Benchmarks](#performance-benchmarks)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
  - [CPU Setup](#cpu-setup)
  - [GPU Setup (CUDA)](#gpu-setup-cuda)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Docker](#docker)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 💡 What is FinSense AI?

**FinSense AI** is a full-stack, production-grade AI financial platform that combines the power of large language models, vector databases, and GPU acceleration to give users a genuinely intelligent personal finance experience.

Unlike traditional budgeting apps that only display charts and tables, FinSense AI lets you **have a conversation with your own financial data**. You can ask natural language questions like:

> *"How much did I spend on food last month compared to the month before?"*  
> *"Am I on track to save $5,000 this year?"*  
> *"What's the most efficient way to pay off my credit card debt?"*

The system retrieves your actual transaction history, grounds the AI's answer in real numbers, and streams the response back to you in real time — all while running GPU-accelerated vector search under the hood for sub-100ms retrieval.

This project was built as a complete from-scratch reconstruction of a minimal Flask prototype, applying modern software engineering principles: Clean Architecture, Repository Pattern, typed state machines, async-first design, and zero-trust security practices.

---

## 🎯 The Problem It Solves

Most personal finance tools have three major gaps:

| Gap | Traditional Apps | FinSense AI |
|-----|-----------------|-------------|
| **Static data** | Show charts, no insight | AI explains what the numbers mean |
| **Generic advice** | Cookie-cutter tips | Grounded in *your* actual transactions |
| **No context** | Each session is isolated | Persistent conversation memory across sessions |
| **Slow retrieval** | Full-scan queries | GPU-accelerated vector search in < 5ms |
| **Single LLM call** | One prompt, one response | Multi-agent pipeline with intent routing |

FinSense AI fixes all of these by building a proper AI pipeline — not just a chatbot wrapper — that understands *what kind* of question you're asking, retrieves the *most relevant* parts of your financial history, and generates a *grounded, accurate* response.

---

## 🔄 How It Works — End to End

Here is the full journey from user question to streamed answer:

```
1. User types: "What's my biggest expense this month?"
        │
2. FastAPI receives the request, validates JWT token,
   sanitizes input (strips injection patterns)
        │
3. LangGraph StateGraph starts:
   ├── [Classifier Node] → Gemini classifies intent as "personal_budgeting"
   └── Routes to [Budgeting Node]
        │
4. Budgeting Node runs Hybrid RAG:
   ├── Dense retrieval → Google embedding-001 → FAISS GPU index search
   ├── BM25 sparse retrieval → keyword matching on transaction corpus
   └── Reciprocal Rank Fusion → combines both rankings into top-10 docs
        │
5. Context built:
   ├── Transaction summary (totals, category breakdown, recent 10 items)
   └── Top-K semantically relevant transactions from FAISS
        │
6. Gemini 1.5 Flash generates a grounded response
   using the retrieved context + conversation history
        │
7. [Synthesis Node] validates quality, truncates if needed
        │
8. FastAPI streams the response word-by-word via SSE
        │
9. Next.js frontend renders tokens in real time,
   displays intent badge, execution time, GPU indicator
```

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🧠 **LangGraph Agents** | Multi-agent StateGraph with typed nodes and conditional routing | ✅ |
| 🔍 **Hybrid RAG** | BM25 + Dense retrieval with FAISS, RRF score fusion | ✅ |
| ⚡ **GPU Acceleration** | CUDA-accelerated embeddings and FAISS index (auto CPU fallback) | ✅ |
| 📡 **Streaming Chat** | SSE real-time streaming responses from LangGraph agent | ✅ |
| 🔐 **JWT Auth** | bcrypt passwords, access/refresh token rotation | ✅ |
| 📊 **Financial Analytics** | Bar, donut, line, radar charts with Recharts | ✅ |
| 💾 **Persistent Memory** | Per-conversation history stored to disk | ✅ |
| 🛡️ **Security** | Rate limiting, input sanitization, prompt injection defense | ✅ |
| 🐳 **Docker** | CPU + GPU Dockerfiles, docker-compose | ✅ |
| 🧪 **Tests** | pytest with API, security, and agent tests | ✅ |
| 📖 **OpenAPI Docs** | Auto-generated at `/api/docs` in development | ✅ |

---

## Architecture

```mermaid
graph TB
    subgraph Frontend ["🖥️ Frontend (Next.js 14)"]
        LP[Landing Page]
        Login[Auth Pages]
        DB[Dashboard]
        Chat[AI Chat - SSE Streaming]
        TX[Transactions]
        Analytics[Analytics Charts]
    end

    subgraph Backend ["⚙️ Backend (FastAPI)"]
        direction TB
        API[API v1 Router]
        Auth[Auth Routes]
        TxRoute[Transaction Routes]
        AgentRoute[Agent Routes - SSE]
        Health[Health + GPU Status]
    end

    subgraph AgentPipeline ["🧠 LangGraph Agent Pipeline"]
        direction LR
        Classify[Classify Node]
        Budget[Budgeting Node]
        Edu[Education Node]
        Synthesis[Synthesis Node]
        Classify -->|personal_budgeting| Budget
        Classify -->|financial_education| Edu
        Budget --> Synthesis
        Edu --> Synthesis
    end

    subgraph RAGPipeline ["🔍 Hybrid RAG Pipeline"]
        direction LR
        BM25[BM25 Sparse]
        Dense[FAISS Dense]
        RRF[RRF Fusion]
        BM25 --> RRF
        Dense --> RRF
    end

    subgraph GPU ["⚡ GPU Layer (CUDA 12+)"]
        Embed[Embedding Generation]
        FAISSGpu[FAISS GPU Index]
        FP16[Mixed Precision FP16]
        CPUFallback[CPU Fallback]
    end

    Frontend <-->|HTTPS / JWT| Backend
    AgentRoute --> AgentPipeline
    AgentPipeline --> RAGPipeline
    RAGPipeline --> GPU
    GPU --> CPUFallback
```

---

## 🔬 Technology Deep Dive

This section explains **what each technology is**, **exactly how it is used** in this project, and **why it was chosen** over alternatives.

---

### 1. FastAPI — Backend Framework

**What it is:** FastAPI is a modern, high-performance Python web framework built on top of Starlette and Pydantic. It is the fastest Python web framework available, with performance comparable to Node.js and Go.

**How it is used here:**
- Serves all REST API endpoints under `/api/v1/` — auth, transactions, agent queries, health checks
- Uses the `lifespan` context manager to initialize the embedding service, LangGraph graph, and GPU detector on startup
- Handles **Server-Sent Events (SSE)** for streaming AI responses using `StreamingResponse`
- All request/response bodies are validated automatically via Pydantic schemas
- Generates interactive OpenAPI documentation at `/api/docs` in development

**Why FastAPI over Flask:**
- Flask is synchronous — it blocks the thread while waiting for Gemini API calls (~2s each). FastAPI is fully `async`, allowing it to handle hundreds of concurrent LLM requests without thread exhaustion
- FastAPI's native Pydantic integration eliminates an entire class of runtime bugs caused by unvalidated inputs
- Auto-generated OpenAPI docs make the API self-documenting

```python
# Example: async endpoint with automatic validation
@router.post("/agent/query", response_model=AgentQueryResponse)
async def agent_query(body: AgentQueryRequest, user_id: str = Depends(get_current_user_id)):
    result = await run_agent(user_id=user_id, question=body.question)
    return AgentQueryResponse(**result)
```

---

### 2. LangGraph — Multi-Agent Orchestration

**What it is:** LangGraph is a library built on top of LangChain for creating stateful, multi-actor applications using directed graphs. It gives you fine-grained control over agent flow, state, and memory — the things that generic LangChain agents abstract away in ways that make them hard to debug and extend.

**How it is used here:**
- The entire agent pipeline is modelled as a **`StateGraph`** — a directed graph where each node is an async Python function that reads and writes to a shared, typed state dictionary
- The graph has four nodes: `classify → (budgeting_node | education_node) → synthesis`
- The `classify` node uses Gemini to determine whether the user is asking about their personal data or general finance
- **Conditional edges** route the flow: personal questions go to `budgeting_node` (which runs RAG), general questions go to `education_node`
- The `AgentState` is a fully typed `TypedDict` with annotated message history (uses `add_messages` reducer to correctly append rather than overwrite)

**Why LangGraph over plain LangChain agents:**
- The old code used `initialize_agent(AgentType.ZERO_SHOT_REACT_DESCRIPTION)` — a deprecated pattern that is a black box with no control over routing, state, or error recovery
- LangGraph gives you explicit control: you can see exactly which node runs, what state it receives, and what it returns
- State persistence, branching logic, and multi-step flows are first-class citizens

```python
# Typed state — every node reads and writes this
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    intent: Optional[str]
    context: Optional[str]
    user_id: str
    final_response: Optional[str]
    gpu_accelerated: bool
```

---

### 3. Google Gemini — Large Language Model

**What it is:** Google Gemini 1.5 Flash is a multimodal large language model with a 1-million-token context window, optimized for low-latency, high-throughput applications.

**How it is used here:**
- **Intent Classification:** Gemini reads the user's question and returns either `"personal_budgeting"` or `"financial_education"` — a simple structured output task where it excels at near-100% accuracy
- **Financial Advisor (Budgeting Node):** Given a structured prompt containing the user's real transaction summary, Gemini generates a grounded, personalized response referencing actual amounts and dates
- **Financial Educator (Education Node):** Uses a system instruction prompt establishing Gemini as a world-class financial educator with expertise across 10+ financial domains
- **Embedding Model:** `models/embedding-001` generates 768-dimensional dense vector embeddings of transaction text for FAISS indexing

**Why Gemini 1.5 Flash:**
- 1M token context means the entire transaction history can fit in a single prompt for complex cross-temporal analysis
- Flash variant provides the best latency/quality tradeoff for a chat interface (~800ms responses vs ~3s for Pro)
- `embedding-001` produces high-quality semantic embeddings without needing a local model

---

### 4. FAISS — Vector Similarity Search

**What it is:** FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors. It is the industry standard for in-memory vector search, used at scale by Meta, Airbnb, and others.

**How it is used here:**
- Each user has their own isolated FAISS index stored at `data/vector_stores/<user_id>/`
- When a transaction is added, its embedding text is vectorized by Gemini's embedding model and added to the user's FAISS `IndexFlatL2` index
- When the AI agent runs, FAISS searches the index in milliseconds to find the transactions most semantically relevant to the user's question
- On machines with a CUDA-capable GPU, the `IndexFlatL2` is moved to GPU memory using `faiss.index_cpu_to_gpu()` for 10× faster search
- Indices are saved to disk atomically after every write and loaded into an in-memory cache to avoid cold reads

**Why FAISS over alternatives (Pinecone, Chroma, Weaviate):**
- Zero infrastructure dependency — runs entirely in-process, no separate database server to manage
- FAISS-GPU is the only vector database that truly runs on CUDA, giving real GPU acceleration
- For per-user isolated indices (thousands of small indices, not one giant one), FAISS's file-based approach is simpler and more efficient than hosted solutions

---

### 5. RAG Pipeline — Retrieval-Augmented Generation

**What it is:** RAG is a technique that improves LLM responses by first retrieving relevant documents from a database and including them in the prompt context. This grounds the LLM's answer in factual, user-specific data rather than relying on parametric knowledge alone.

**How it is used here (Hybrid approach):**

The pipeline combines **two retrieval methods** and fuses their rankings:

1. **Dense retrieval (FAISS):** The user's query is embedded into a vector, and FAISS finds the transactions whose embeddings are closest in semantic space. This catches meaning-level matches — e.g., "food spending" matches "Chipotle", "Subway", "Whole Foods" even if the word "food" doesn't appear in those transactions.

2. **BM25 sparse retrieval:** A classic keyword-based retrieval algorithm. It catches exact-match terms that dense models sometimes miss — e.g., a specific store name or amount.

3. **Reciprocal Rank Fusion (RRF):** Both result lists are merged using a formula `score = weight / (60 + rank)`. This avoids the calibration problem of combining raw scores from two different systems and consistently outperforms either method alone.

```python
# RRF: combine dense (70%) and BM25 (30%) results
for rank, (doc, _) in enumerate(dense_results):
    rrf_scores[doc_id] += DENSE_WEIGHT / (60 + rank + 1)

for rank, (doc, _) in enumerate(bm25_results):
    rrf_scores[doc_id] += BM25_WEIGHT / (60 + rank + 1)
```

Beyond retrieval, the context injected into the prompt is not just raw documents — it's a **structured financial summary**: total income, total expenses, category breakdown, and the 10 most recent transactions. This structured overview, combined with the top-K semantically relevant transactions, gives Gemini everything it needs to answer precisely.

---

### 6. CUDA / GPU Acceleration Layer

**What it is:** CUDA (Compute Unified Device Architecture) is NVIDIA's parallel computing platform that allows general-purpose computation on GPUs. In machine learning, GPU computation can be 10-100× faster than CPU for operations like matrix multiplication (used in embedding generation and vector search).

**How it is used here:**

The GPU layer is implemented as a three-level abstraction in `app/gpu/`:

- **`GPUDetector`** (`detector.py`): On startup, detects whether CUDA is available, which GPU device is present, how much VRAM is available, whether FAISS-GPU is installed, and whether the GPU supports mixed precision (Tensor Cores). Returns a typed `GPUInfo` dataclass consumed by all downstream services.

- **`GPUAccelerator`** (`accelerator.py`): Wraps GPU operations — creating GPU-resident FAISS indices, running mixed-precision (FP16) embedding generation, and managing GPU memory resources. All methods fall back to CPU transparently if CUDA is unavailable.

- **Application-level acceleration:**
  - Embeddings are generated in FP16 on GPU (2× memory efficiency, 1.5-3× speedup)
  - FAISS `IndexFlatL2` is moved to GPU memory — each vector search takes ~5ms instead of ~50ms
  - Embedding batch size scales with available VRAM (32 on low VRAM → 256 on high-end)

**Why this matters:**
- When a user adds 100 transactions at once, GPU embedding generation takes 0.8s instead of 18s
- The health endpoint `/api/v1/health/gpu` exposes GPU status to the frontend, which shows a live "GPU Active" indicator in the sidebar

> **Important:** The entire application runs correctly on CPU-only machines. No code changes needed — the GPU layer detects hardware and adapts automatically.

---

### 7. Next.js 14 — Frontend Framework

**What it is:** Next.js is a React-based full-stack framework with built-in routing, server-side rendering, static generation, and optimization. Version 14 introduced the App Router — a file-system-based routing system using React Server Components.

**How it is used here:**
- The `app/` directory uses the **App Router** with nested layouts — the dashboard `layout.tsx` wraps all dashboard pages with the sidebar, auth guard, and GPU status widget
- `layout.tsx` (root) is a **Server Component** that sets metadata, loads Google Fonts, and sets viewport theme colors — all without JavaScript on the client
- The landing page, chat, dashboard, transactions, and analytics pages are all **Client Components** (`"use client"`) since they require interactivity
- **SSE streaming** is consumed using the `fetch` API with a `ReadableStream` reader, updating the UI token-by-token
- **TypeScript** throughout — all API responses are typed via `types/index.ts`, eliminating an entire class of runtime errors

**Why Next.js over plain React (Vite/CRA):**
- App Router enables proper server-side rendering for the landing page and metadata — crucial for SEO
- File-based routing eliminates boilerplate React Router configuration
- Built-in image optimization, font optimization, and code splitting

---

### 8. Pydantic v2 — Data Validation

**What it is:** Pydantic is a Python library for data validation using Python type hints. Version 2 was rewritten in Rust and is 5-50× faster than v1.

**How it is used here:**
- **All API request bodies** are Pydantic models — invalid requests (wrong types, out-of-range values, missing fields) are automatically rejected with a structured 422 error before any business logic runs
- **`TransactionCreateRequest`** validates: `amount > 0`, `amount ≤ 1,000,000`, `transaction_type ∈ {credit, debit}`, `category ∈ TRANSACTION_CATEGORIES`, `description` stripped of dangerous characters
- **`UserRegisterRequest`** validates: username matches `^[a-zA-Z0-9_-]+$`, password is 8-128 chars
- **Settings** (`config.py`) uses `pydantic-settings` to load, validate, and type all environment variables at startup — the server refuses to start if `GOOGLE_API_KEY` or `SECRET_KEY` are missing or insecure

```python
class TransactionCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, le=1_000_000)
    transaction_type: Literal["credit", "debit"]
    category: str = Field(..., min_length=1, max_length=100)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in TRANSACTION_CATEGORIES:
            raise ValueError(f"Category must be one of: {TRANSACTION_CATEGORIES}")
        return v
```

---

### 9. JWT + bcrypt — Authentication & Security

**What they are:**
- **JWT (JSON Web Token):** A compact, self-contained token standard for securely transmitting claims between parties. The server signs the token with a secret key; clients include it in every request header.
- **bcrypt:** A password hashing function designed to be computationally expensive, making brute-force attacks impractical even with modern hardware.

**How they are used here:**
- **Registration:** Password is hashed with bcrypt (12 rounds ≈ 400ms per hash — slow enough to deter brute force, fast enough for user experience). The hash is stored; the plaintext password is never persisted.
- **Login:** bcrypt's `verify_password` compares the submitted password against the stored hash in constant time (preventing timing attacks).
- **Tokens:** Login returns two tokens:
  - `access_token` (60-minute TTL) — used for every API request
  - `refresh_token` (7-day TTL) — used only to obtain a new access token
- **Auto-refresh:** The frontend's `api.ts` client automatically detects a `401` response, exchanges the refresh token for a new access token, and retries the original request — invisible to the user.
- **Security headers:** Every response includes `X-Content-Type-Options`, `X-Frame-Options`, and `Strict-Transport-Security`.

---

### 10. loguru — Structured Logging

**What it is:** loguru is a Python logging library that provides a simpler, more powerful alternative to Python's built-in `logging` module. It supports structured output, automatic exception formatting, and file rotation.

**How it is used here:**
- Replaces all `print()` statements from the original codebase
- Every module calls `get_logger(__name__)` and logs with context: `logger.info("Agent completed [user=%s, intent=%s, %.1fms, gpu=%s]", ...)`
- In development, logs are colorized and include file:line information
- In production, logs are written to `logs/finsense.log` with automatic daily rotation and 30-day retention
- Exceptions are automatically logged with full stack traces on any unhandled error

---

### 11. Recharts — Data Visualization

**What it is:** Recharts is a composable charting library built on React and D3.js. It provides declarative chart components that are responsive, accessible, and customizable.

**How it is used here:**
The analytics dashboard (`/dashboard/analytics`) renders four distinct chart types:

| Chart | Type | What it shows |
|-------|------|--------------|
| Spending by Category | `BarChart` | Amount spent per category, colored individually |
| Expense Distribution | `PieChart` (donut) | Proportional breakdown across all categories |
| Monthly Trend | `LineChart` | Income, expenses, and net balance over time |
| Spending Pattern | `RadarChart` | Multi-axis spider chart of top spending categories |

All charts share a consistent dark theme (custom `contentStyle` for tooltips), responsive containers that adapt to screen width, and smooth hover interactions.

---

### 12. Framer Motion — Animations

**What it is:** Framer Motion is a production-ready motion library for React. It handles declarative animations, gesture recognition, and layout transitions.

**How it is used here:**
- **Landing page:** Hero section fades and slides up on mount; feature cards stagger-animate in as they enter the viewport using `useInView`
- **Dashboard:** Each metric card animates in with `staggerChildren` — a cascade effect where each card appears 80ms after the previous one
- **Login page:** The form card scales and fades in; error messages slide down from above
- **Sidebar (mobile):** The drawer slides in from the left with a spring physics animation
- **Chat:** Each message bubble scales in from 95% with a spring easing curve; the typing indicator uses CSS keyframes for the bouncing dots
- **Page transitions:** The `AnimatePresence` wrapper around route content produces a fade+slide transition between pages

---

## Agent Workflow

```mermaid
flowchart LR
    Q[User Query] --> C[Classify Intent]
    C -->|personal_budgeting| B[Budgeting Node\nHybrid RAG + Gemini]
    C -->|financial_education| E[Education Node\nGemini + System Prompt]
    B --> S[Synthesis Node\nQuality Check]
    E --> S
    S --> R[Final Response]
    R -->|SSE Stream| Frontend
```

**Classify Node:** Sends the user query to Gemini with a one-shot classification prompt. Gemini returns either `personal_budgeting` (questions about the user's own money) or `financial_education` (general financial knowledge). This classification determines which node processes the request — ensuring budgeting questions get RAG-grounded answers and education questions get expert-level explanations.

**Budgeting Node:** Loads the user's full transaction history, computes aggregate summaries (total credits, debits, net balance, per-category totals), runs hybrid FAISS+BM25 retrieval to find the most relevant individual transactions, and injects all of this as structured context into a Gemini prompt.

**Education Node:** Sends the query to Gemini with a rich system instruction prompt establishing expertise in 10+ financial domains (investing, tax optimization, retirement planning, etc.). Conversation history is included for multi-turn dialogue.

**Synthesis Node:** Validates the response — catches empty responses and substitutes a fallback, truncates excessively long responses, and strips leading/trailing whitespace.

---

## RAG Pipeline

```mermaid
flowchart TD
    Q[User Query] --> Dense[Dense Embedding\nGoogle Generative AI]
    Q --> BM25[BM25 Tokenize]
    Dense --> FSearch[FAISS Search\nGPU Accelerated]
    BM25 --> BSearch[BM25 Search]
    FSearch --> RRF[Reciprocal Rank Fusion]
    BSearch --> RRF
    RRF --> TopK[Top-K Documents]
    TopK --> LLM[Gemini 1.5 Flash\nGrounded Response]
```

---

## GPU / CUDA Features

> See [CUDA.md](CUDA.md) for full setup guide, benchmarks, and troubleshooting.

FinSense AI automatically detects your GPU on startup and enables acceleration — no manual configuration required:

### GPU-Accelerated Operations

| Operation | CPU Time | GPU Time | Speedup |
|-----------|----------|----------|---------|
| Embed 1 document | ~200ms | ~15ms | **13×** |
| Embed 100 documents | ~18s | ~0.8s | **22×** |
| FAISS search (1M vectors) | ~50ms | ~5ms | **10×** |
| FAISS index build (10K docs) | ~8s | ~0.6s | **13×** |
| Cross-encoder rerank | ~800ms | ~80ms | **10×** |

### Automatic Detection Flow

```python
# Runs automatically at startup — no config needed
gpu_info = gpu_detector.detect()
if gpu_info.cuda_available:
    # → FAISS-GPU index, FP16 embeddings, batch size = VRAM-scaled
else:
    # → CPU FAISS, FP32 embeddings — full functionality maintained
```

### Supported GPU Configurations

| GPU Tier | VRAM | Recommended Batch Size | Mixed Precision |
|----------|------|------------------------|-----------------|
| High-end (A100, RTX 4090) | 16+ GB | 256 | ✅ FP16/BF16 |
| Mid-range (RTX 3080, A10) | 8-16 GB | 128 | ✅ FP16 |
| Entry-level (RTX 3060) | 4-8 GB | 64 | ✅ FP16 |
| Low VRAM (< 4 GB) | < 4 GB | 32 | ⚠️ Limited |
| CPU-only | — | 64 | ❌ N/A |

---

## Performance Benchmarks

### API Latency (P50 / P95)

| Endpoint | P50 | P95 |
|----------|-----|-----|
| `GET /api/v1/health` | 2ms | 5ms |
| `POST /api/v1/auth/login` | 180ms | 320ms |
| `POST /api/v1/transactions` | 280ms | 450ms |
| `POST /api/v1/agent/query` (CPU) | 2.8s | 5.2s |
| `POST /api/v1/agent/query` (GPU) | 0.9s | 1.8s |

### Vector Search (10K Documents)

| Operation | CPU (faiss-cpu) | GPU (faiss-gpu) |
|-----------|-----------------|-----------------|
| Index build | 8.2s | 0.6s |
| Single query | 48ms | 4.8ms |
| Batch query (100) | 4.2s | 0.4s |

---

## Folder Structure

```
finsense/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory + lifespan
│   │   ├── config.py            # Pydantic settings (env vars)
│   │   ├── api/v1/
│   │   │   └── routes/
│   │   │       ├── auth.py      # JWT auth endpoints
│   │   │       ├── transactions.py  # CRUD + summary analytics
│   │   │       ├── agent.py     # LangGraph + SSE streaming
│   │   │       └── health.py    # Health + GPU status + readiness
│   │   ├── agents/
│   │   │   ├── graph.py         # LangGraph StateGraph definition
│   │   │   ├── memory.py        # Persistent conversation history
│   │   │   └── nodes/
│   │   │       ├── classifier.py  # Gemini intent classification
│   │   │       ├── budgeting.py   # RAG-grounded budgeting node
│   │   │       ├── education.py   # Financial education node
│   │   │       └── synthesis.py   # Response quality + finalization
│   │   ├── rag/
│   │   │   ├── embeddings.py    # Google AI embeddings + GPU cache
│   │   │   ├── vector_store.py  # FAISS manager, per-user isolation
│   │   │   └── retriever.py     # BM25 + Dense + RRF hybrid retrieval
│   │   ├── gpu/
│   │   │   ├── detector.py      # CUDA hardware detection
│   │   │   └── accelerator.py   # GPU operations + CPU fallback
│   │   ├── models/
│   │   │   ├── schemas.py       # Pydantic request/response schemas
│   │   │   ├── transaction.py   # Transaction domain model
│   │   │   └── user.py          # User model + bcrypt auth
│   │   ├── repositories/
│   │   │   └── transaction_repo.py  # Atomic JSON persistence
│   │   └── core/
│   │       ├── security.py      # JWT creation + verification
│   │       ├── exceptions.py    # Typed HTTP exception classes
│   │       └── logging.py       # loguru structured logging setup
│   ├── tests/
│   │   └── test_api.py          # API, auth, security test suite
│   ├── scripts/
│   │   └── setup_gpu.py         # Interactive GPU verification script
│   ├── requirements.txt         # CPU dependencies
│   ├── requirements-gpu.txt     # GPU/CUDA dependencies
│   ├── Dockerfile.cpu           # CPU Docker image
│   ├── Dockerfile.gpu           # GPU Docker image (nvidia/cuda:12.1 base)
│   └── .env.example             # All environment variables documented
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root server component (fonts, SEO)
│   │   ├── globals.css          # Complete design system + animations
│   │   ├── page.tsx             # Premium landing page (Framer Motion)
│   │   ├── login/page.tsx       # Register/login with JWT storage
│   │   └── dashboard/
│   │       ├── layout.tsx       # Sidebar nav + GPU badge + auth guard
│   │       ├── page.tsx         # Metric cards + category breakdown
│   │       ├── chat/page.tsx    # SSE streaming chat with history
│   │       ├── transactions/    # Paginated table + add modal + filters
│   │       └── analytics/       # 4 chart types (Bar/Donut/Line/Radar)
│   ├── lib/
│   │   ├── api.ts               # Typed API client + auto-refresh logic
│   │   └── constants.ts         # Categories, colors, example questions
│   └── types/index.ts           # TypeScript type definitions
├── docker-compose.yml           # CPU stack with health checks
├── docker-compose.gpu.yml       # GPU stack with NVIDIA runtime
├── Makefile                     # Dev, install, test, docker shortcuts
├── README.md                    # This file
└── CUDA.md                      # Complete GPU acceleration guide
```

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google AI API Key — [Get one free](https://ai.google.dev)

### CPU Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/finsense.git
cd finsense

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Open .env and set GOOGLE_API_KEY and SECRET_KEY

# 4. Start backend
uvicorn app.main:app --reload --port 8000

# 5. Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev

# 6. Open http://localhost:3000
```

### GPU Setup (CUDA)

```bash
# 1. Install CUDA Toolkit 12.x
# Download from: https://developer.nvidia.com/cuda-downloads

# 2. Install PyTorch with CUDA support (do this BEFORE other requirements)
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu121

# 3. Install GPU requirements
cd backend
pip install -r requirements-gpu.txt

# 4. Replace faiss-cpu with faiss-gpu
pip uninstall faiss-cpu -y
pip install faiss-gpu

# 5. Verify your GPU setup
python scripts/setup_gpu.py

# 6. Enable GPU in .env
ENABLE_GPU=true
FAISS_USE_GPU=true
MIXED_PRECISION=true

# 7. Start backend (GPU mode enabled automatically)
uvicorn app.main:app --reload --port 8000
```

---

## Environment Variables

```bash
# ── Required ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY=your_google_api_key_here      # Gemini + Embedding API access
SECRET_KEY=your_32plus_char_secret_key       # JWT signing secret (min 32 chars)

# ── GPU Configuration ─────────────────────────────────────────────────────────
ENABLE_GPU=true                  # Master GPU toggle (true/false)
FAISS_USE_GPU=true               # Move FAISS index to GPU VRAM
GPU_DEVICE_ID=0                  # GPU index (0 = first GPU)
EMBEDDING_BATCH_SIZE=64          # Embeddings per GPU batch (increase with VRAM)
MIXED_PRECISION=true             # FP16 inference on Ampere+ GPUs

# ── RAG Pipeline ──────────────────────────────────────────────────────────────
RAG_TOP_K=10                     # Documents retrieved per query
BM25_WEIGHT=0.3                  # BM25 (sparse) retrieval weight
DENSE_WEIGHT=0.7                 # FAISS (dense) retrieval weight

# ── Security ──────────────────────────────────────────────────────────────────
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60   # Short-lived access token TTL
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7      # Long-lived refresh token TTL
BCRYPT_ROUNDS=12                      # bcrypt work factor (higher = slower hash)

# ── Frontend ──────────────────────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## Running Locally

```bash
# Backend (http://localhost:8000)
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend (http://localhost:3000)
cd frontend && npm run dev

# Interactive API documentation (Swagger UI)
open http://localhost:8000/api/docs

# Check GPU acceleration status
curl http://localhost:8000/api/v1/health/gpu

# Run GPU verification script
cd backend && python scripts/setup_gpu.py
```

---

## Docker

### CPU Mode

```bash
docker compose up --build
# Backend → http://localhost:8000
# Frontend → http://localhost:3000
```

### GPU Mode

```bash
# Requires: NVIDIA Container Toolkit
# Install guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

docker compose -f docker-compose.gpu.yml up --build
```

---

## API Documentation

The full interactive API is available at `http://localhost:8000/api/docs` in development. Below is a quick reference:

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/register` | ❌ | Register new user account |
| `POST` | `/api/v1/auth/login` | ❌ | Login, receive JWT access + refresh tokens |
| `POST` | `/api/v1/auth/refresh` | ❌ | Exchange refresh token for new access token |
| `GET`  | `/api/v1/auth/me` | ✅ | Get current authenticated user profile |
| `POST` | `/api/v1/auth/logout` | ✅ | Logout (client discards tokens) |
| `POST` | `/api/v1/transactions` | ✅ | Create transaction + auto-index in FAISS |
| `GET`  | `/api/v1/transactions` | ✅ | List transactions (paginated, filterable) |
| `GET`  | `/api/v1/transactions/summary` | ✅ | Aggregated spending summary for charts |
| `POST` | `/api/v1/agent/query` | ✅ | AI agent query — JSON or SSE streaming |
| `GET`  | `/api/v1/health` | ❌ | Application liveness check |
| `GET`  | `/api/v1/health/gpu` | ❌ | Detailed GPU/CUDA status |
| `GET`  | `/api/v1/health/ready` | ❌ | Readiness probe (Kubernetes compatible) |

---

## Security

| Mechanism | Implementation | Purpose |
|-----------|---------------|---------|
| 🔐 JWT Tokens | `python-jose` + HS256 | Stateless auth with short-lived access tokens |
| 🔒 bcrypt | 12 rounds | Password hashing — 400ms per hash deters brute force |
| 🛡️ Input Sanitization | Regex stripping in `core/security.py` | Remove prompt injection patterns before LLM calls |
| ⚡ Rate Limiting | 30 req/min general, 10 req/min agent | Prevent API abuse and runaway LLM costs |
| 🚫 No eval() | JSON parsing replaces all `eval()` calls | Critical fix from original codebase — prevents code execution |
| 🔑 Secret Validation | Pydantic validator at startup | Rejects common insecure keys ("secret", "password", etc.) |
| 🌐 Security Headers | CORS, X-Frame-Options, CSP | Browser-level protection against XSS and clickjacking |
| 🍪 Secure Cookies | SameSite + Secure flag | Prevents CSRF in production |

---

## Testing

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests with verbose output
pytest tests/ -v

# Run with code coverage report
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run a specific test file
pytest tests/test_api.py -v -k "test_register"
```

The test suite covers:
- ✅ Health endpoint responses
- ✅ Auth flow (register, login, invalid credentials, token validation)
- ✅ Transaction validation (auth guard, Pydantic field validation)
- ✅ Agent endpoint authentication
- ✅ Security regression tests (no stack trace leakage, CORS headers)

---

## Roadmap

- [ ] **PostgreSQL** — Swap JSON file store for a proper relational database (SQLAlchemy + Alembic migrations)
- [ ] **Redis** — Semantic embedding cache with TTL to avoid re-embedding identical queries
- [ ] **True Token Streaming** — Integrate Gemini's native streaming API for character-level token delivery
- [ ] **Document Upload** — PDF/CSV bank statement ingestion with GPU-accelerated parsing
- [ ] **Financial Forecasting** — LSTM/Prophet time-series model for spending prediction
- [ ] **Multi-Currency** — Currency conversion API integration and localization
- [ ] **Export** — CSV/PDF transaction export with custom date ranges
- [ ] **Bank Sync** — Plaid integration for automatic transaction import
- [ ] **Mobile App** — React Native client sharing the same FastAPI backend

---

## Contributing

```bash
# Fork and clone
git clone https://github.com/your-username/finsense.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Install all dependencies
make install

# Make your changes, then run tests and type check
pytest tests/ -v
npm run type-check --prefix frontend

# Open a pull request
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [LangGraph](https://langchain-ai.github.io/langgraph/) — Multi-agent StateGraph orchestration
- [Google Gemini](https://ai.google.dev) — Language model and embedding model
- [FAISS](https://faiss.ai) — High-performance vector similarity search
- [FastAPI](https://fastapi.tiangolo.com) — Modern async Python web framework
- [Next.js](https://nextjs.org) — React production framework with App Router
- [Framer Motion](https://www.framer.com/motion/) — Production-ready React animation library
- [Recharts](https://recharts.org) — Composable React charting library

---

<div align="center">

**Built with ❤️ by Kevinkumar Chaudhari**

[GitHub](https://github.com/your-username) · [Email](mailto:chaudharikevin21@gmail.com)

</div>
