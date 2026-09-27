Here is the downloadable file containing the clean `README.md` for **CogniLearn AI**:

# CogniLearn AI

<p align="center">
  <img src="frontend/public/CogniLearn.jpg" alt="CogniLearn AI Synapse Book Mark" width="700" height="381" />
</p>

**CogniLearn AI** is a production-grade, bilingual (EN/DE) artificial intelligence learning platform. Built with a clean, decoupled architecture, it pairs a **FastAPI** backend powering a **Bilingual Hybrid RAG Engine** and **Socratic Multi-Agent Orchestrator** with a **Next.js 15** frontend web workspace.

---

## Key Features

- **Bilingual Hybrid Retrieval (Vector + BM25):** Powered by PostgreSQL 17 with `pgvector` HNSW indexes for dense search, coupled with language-specific GIN Full-Text Search (FTS for English and German) combined via Reciprocal Rank Fusion (RRF).
- **Socratic Multi-Agent Engine:**
  - **Q&A Citation Agent:** Provides direct, context-grounded answers accompanied by exact textbook chapter and section citations.
  - **Socratic Tutor Agent:** Employs interactive pedagogical techniques to guide students toward answers without giving away solutions directly.
- **Modern Next.js 15 Workspace:** High-performance user interface leveraging React Server Actions (`useActionState`), TypeScript, and Tailwind CSS.
- **Containerized Local Stack:** Standardized infrastructure setup running PostgreSQL 17 (`pgvector`), Redis, and Jaeger via Docker Compose.

---

## System Architecture

```text
               +----------------------------------+
               |        Next.js 15 Frontend       |
               |  React Server Actions / Tailwind |
               +----------------+-----------------+
                                |
                                | HTTP / REST
                                v
               +----------------+-----------------+
               |         FastAPI AI Core          |
               | Python 3.12 / Multi-Agent Engine |
               +--------+----------------+--------+
                        |                |
           Vector / BM25|                | Async Pool
            Search Query|                v
                        |        +---------------+
                        |        | Redis Cache / |
                        |        | Jaeger Traces |
                        v        +---------------+
    +-------------------+-------------------+
    |             PostgreSQL 17             |
    | pgvector (HNSW) + Bilingual FTS (GIN) |
    +---------------------------------------+
```

````

---

## Directory Structure

```text
CogniLearn/
├── backend/                  # FastAPI service (Python 3.12, managed via uv)
│   ├── app/
│   │   ├── agents/           # Citation & Socratic Agent Orchestrator
│   │   ├── api/              # API REST Endpoints (/api/v1/chat)
│   │   ├── core/             # Asyncpg pool & environment configurations
│   │   └── rag/              # Bilingual Hybrid Retriever (RRF Scoring)
│   └── scripts/              # Seed scripts & DB health utilities
├── frontend/                 # Next.js 15 Web Workspace (pnpm)
│   ├── public/               # Static assets & brand mark (favicon.svg)
│   └── src/
│       ├── app/              # App Router & React Server Actions
│       └── components/       # Reusable components (Logo.tsx, UI layout)
└── infra/                    # Local infrastructure files
    ├── docker-compose.yml    # Postgres 17, Redis, and Jaeger containers
    └── init.sql              # Database schema & pgvector / FTS setup

```

---

## Quickstart Guide

### Prerequisites

- [Docker & Docker Compose](https://www.docker.com/?utm_source=gemini)
- [Python 3.12+](https://www.python.org/?utm_source=gemini) & [`uv`](https://github.com/astral-sh/uv?utm_source=gemini)
- [Node.js 20+](https://nodejs.org/?utm_source=gemini) & [`pnpm`](https://pnpm.io/?utm_source=gemini)

---

### 1. Launch Infrastructure Containers

Spin up PostgreSQL 17 with `pgvector`, Redis, and Jaeger:

```bash
docker-compose up -d

```

---

### 2. Configure & Start Backend Core

```bash
cd backend

# Install dependencies and sync virtual environment
uv sync

# Seed PostgreSQL with sample bilingual course materials (DL-101)
uv run python -m scripts.seed_db

# Start the FastAPI development server
uv run uvicorn app.main:app --reload --port 8000

```

- **Interactive API Documentation:** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/health`

---

### 3. Launch Frontend Web App

```bash
cd frontend

# Install Node dependencies
pnpm install

# Start Next.js development server
pnpm dev

```

- **CogniLearn Workspace:** `http://localhost:3000`

---

## Environment Configuration

Create a `.env` file inside the `backend/` directory:

```env
PROJECT_NAME="CogniLearn AI"
VERSION="0.1.0"
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/cognilearn"
OPENAI_API_KEY="your-openai-api-key"

```

```

````
