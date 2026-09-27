# System Architecture Document
## CogniLearn — Microservices & Agentic RAG Platform

---

## 1. System Topology Overview

CogniLearn employs a cloud-native microservices architecture designed for async AI workflows, low-latency retrieval, and real-time streaming capabilities.

```
+-----------------------------------------------------------------------+
|                       Client Layer (Next.js 15)                       |
|           - React Server Components & i18n (English / German)         |
|           - WebRTC Player & SSE Streaming UI                          |
+-----------------------------------+-----------------------------------+
                                    |
                                    | HTTP / WebSockets / SSE
                                    v
+-----------------------------------+-----------------------------------+
|                  API Gateway & Security Layer (.NET 10)              |
|           - Authentication & Rate Limiting                            |
|           - Language Router & Request Sanitization                    |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------+-----------------------------------+
|               AI Core Service Engine (Python 3.12 FastAPI)            |
|                                                                       |
|   +--------------------------+     +-------------------------------+  |
|   |   Security Middleware    |     |   Personalization Pipeline    |  |
|   |  - PII Masking           |     |  - Student Context Builder    |  |
|   |  - Guardrails            |     |  - Progress Signals           |  |
|   +------------+-------------+     +---------------+---------------+  |
|                |                                   |                  |
|                +-----------------+-----------------+                  |
|                                  |                                    |
|                                  v                                    |
|   +------------------------------+-------------------------------+    |
|   |                  Multi-Agent Runtime Engine                  |    |
|   |  - Q&A Citation Agent        - Socratic Dialogue Agent       |    |
|   |  - System Prompts (EN / DE)  - Multi-Turn State Machine      |    |
|   +------------------------------+-------------------------------+    |
|                                  |                                    |
+----------------------------------+------------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+--------+--------------------------+     +------------------+-----------+
|    Bilingual Hybrid Search RAG    |     |  Data & Session Storage      |
|  - pgvector Cosine Search         |     |  - PostgreSQL 16 (HNSW)      |
|  - BM25 Full-Text Search (EN/DE)  |     |  - Redis 7 (State & Cache)   |
|  - Reciprocal Rank Fusion (RRF)   |     |  - Jaeger / OpenTelemetry    |
+-----------------------------------+     +------------------------------+
```

---

## 2. Core Technical Components

### 2.1 Bilingual Hybrid Retrieval (RAG)
To guarantee high precision across technical German and English academic terminology, retrieval combines dense vector embeddings with sparse text search:

1. **Dense Retrieval:** OpenAI `text-embedding-3-small` (1536 dimensions) stored in PostgreSQL using `pgvector` with HNSW indexing.
2. **Sparse Retrieval:** PostgreSQL full-text search dictionaries (`to_tsvector('english', content)` and `to_tsvector('german', content)`).
3. **Re-Ranking Algorithm:** Reciprocal Rank Fusion (RRF) merges top-$K$ candidates from both streams using:
   $$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
   Where $M$ represents the set of retrieval methods (Vector, BM25), $k = 60$, and $r_m(d)$ is document $d$'s rank in method $m$.

### 2.2 Stateful Multi-Agent Orchestration
The AI core implements a stateful agent router:
* **Intent Classifier:** Determines if the student request requires direct citation lookup (`QA_MODE`) or conceptual guidance (`SOCRATIC_MODE`).
* **Q&A Citation Agent:** Focuses on extracting exact textbook references and generating verified answers.
* **Socratic Tutor Agent:** Uses step-back prompting and cognitive scaffolding to guide reasoning without giving away solutions directly.

### 2.3 Storage Layer Schema
* **PostgreSQL 16:** Stores document chunks, embeddings, course metadata, and evaluation telemetry.
* **Redis 7:** Manages active dialogue sessions, user context tokens, rate-limiting counters, and semantic query caching.

---

## 3. Data Flow & Sequence Diagram

```
Student (Client)            FastAPI AI Core               PostgreSQL (pgvector)          LLM / Agent Engine
       |                           |                               |                           |
       |--- 1. Query (Text/Lang) -->|                               |                           |
       |                           |--- 2. Anonymize PII --------->|                           |
       |                           |--- 3. Generate Embedding ---->|                           |
       |                           |--- 4. Hybrid Search (EN/DE) ->|                           |
       |                           |<-- 5. Top Chunks + Metadata --|                           |
       |                           |                                                           |
       |                           |--- 6. Construct Prompt (Context + Student Signals) ------>|
       |                           |<-- 7. Stream LLM Tokens (SSE) ----------------------------|
       |<-- 8. Stream Response ----|                                                           |
```

---

## 4. Production Security & Compliance
1. **PII Masking:** PII is stripped using regex and NER models before sending payload data to public LLM endpoints.
2. **OWASP LLM Guardrails:** Input validation blocks indirect prompt injections and system prompt extraction attacks.
3. **Data Residency:** All database storage and primary microservices run within EU sovereign cloud regions (Azure West Europe / AWS Frankfurt) to ensure GDPR compliance.