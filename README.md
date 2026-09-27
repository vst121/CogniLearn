# CogniLearn AI

<p align="center">
  <img src="frontend/public/public/CogniLearn.jpg" alt="CogniLearn AI Synapse Book Mark" width="96" height="96" />
</p>

**CogniLearn AI** is a production-grade, bilingual (EN/DE) artificial intelligence learning platform[cite: 1]. Built with a clean, decoupled architecture[cite: 1], it pairs a **FastAPI** backend powering a **Bilingual Hybrid RAG Engine** and **Socratic Multi-Agent Orchestrator** with a **Next.js 15** frontend web workspace[cite: 1].

---

## Key Features

- **Bilingual Hybrid Retrieval (Vector + BM25):** Powered by PostgreSQL 17 with `pgvector` HNSW indexes for dense search, coupled with language-specific GIN Full-Text Search (FTS for English and German) combined via Reciprocal Rank Fusion (RRF)[cite: 1].
- **Socratic Multi-Agent Engine:**
  - **Q&A Citation Agent:** Provides direct, context-grounded answers accompanied by exact textbook chapter and section citations[cite: 1].
  - **Socratic Tutor Agent:** Employs interactive pedagogical techniques to guide students toward answers without giving away solutions directly[cite: 1].
- **Modern Next.js 15 Workspace:** High-performance user interface leveraging React Server Actions (`useActionState`), TypeScript, and Tailwind CSS[cite: 1].
- **Containerized Local Stack:** Standardized infrastructure setup running PostgreSQL 17 (`pgvector`), Redis, and Jaeger via Docker Compose[cite: 1].

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
