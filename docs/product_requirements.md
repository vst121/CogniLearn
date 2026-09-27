# Product Requirements Document (PRD)
## CogniLearn — Enterprise AI Learning Companion

---

## 1. Executive Summary & Vision
**CogniLearn** is an open-source, enterprise-grade AI learning companion designed to mirror **IU Group's Syntea platform**. The application serves higher education students with real-time, personalized, and curriculum-grounded academic assistance.

By bridging academic course scripts with stateful agentic workflows, CogniLearn transitions traditional static learning into an interactive, multi-turn educational experience.

---

## 2. Core Problem Statement
Distance-learning students often experience:
1. **Academic Isolation:** Lack of immediate conceptual feedback outside formal office hours.
2. **LLM Hallucinations:** Generic commercial LLMs frequently invent inaccurate facts or fail to ground answers in university-approved course material.
3. **Passive Learning:** Standard AI chatbots provide direct answers immediately, reducing critical thinking and long-term retention.
4. **Language Disparity:** Non-native learners require equal feature availability, performance, and accuracy in both **English** and **German**.

---

## 3. Bilingual Strategy & Requirements (EN & DE)

| Dimension | Technical Strategy |
| :--- | :--- |
| **User Interface (i18n)** | Next.js `next-intl` runtime switching supporting `en-US` and `de-DE`. |
| **Hybrid Search** | Multilingual vector embeddings (`text-embedding-3-small`) combined with language-specific PostgreSQL full-text search (`english` and `german` dictionaries). |
| **Agent Prompting** | Dynamic language-aware system prompts enforcing output alignment in English or German while retaining technical terminology. |
| **Cross-Lingual Retrieval** | Ability to query in German and retrieve English source materials (or vice-versa) with localized citation summaries. |

---

## 4. Functional Requirements

### 4.1 Course Q&A Engine (Citation Agent)
* **FR-QA-01:** System must perform hybrid retrieval (Vector + BM25) across digitized course material.
* **FR-QA-02:** All generated factual statements must include explicit source metadata: `[Course Code | Chapter | Section]`.
* **FR-QA-03:** System must enforce strict citation confidence thresholds ($> 0.80$ similarity); questions below threshold must trigger fallback or human-in-the-loop flags.

### 4.2 Socratic Deep Dialogue Engine (Tutoring Agent)
* **FR-SOC-01:** System must identify user learning intent (factual lookup vs. deep concept understanding).
* **FR-SOC-02:** When in Socratic Mode, the agent must *never* reveal direct exercise solutions immediately.
* **FR-SOC-03:** Agent must break down complex topics into step-by-step probing questions to guide student reasoning.

### 4.3 Student Personalization & Context Pipeline
* **FR-PERS-01:** Dynamically ingest student state: active course, target exam date, self-identified weak topics, and previous interaction history.
* **FR-PERS-02:** Inject student context into agent runtime prompts to tailor response complexity and tone.

### 4.4 AI Safety, Quality & Evaluation
* **FR-SAFE-01:** Anonymize PII (names, student IDs, email addresses) before forwarding prompts to cloud model endpoints.
* **FR-SAFE-02:** Filter prompt injection attempts and inappropriate academic integrity breaches (e.g., "write my final exam").
* **FR-EVAL-01:** Continuous automated scoring of responses against offline evaluation benchmarks (Grounding, Citation Precision, Language Alignment) in both English and German.

---

## 5. Non-Functional Requirements
* **Latency:** Time-To-First-Token (TTFT) $< 500\text{ms}$; total RAG response generation $< 2.5\text{s}$.
* **Scalability:** Stateless API layer scalable up to 10+ concurrent replicas behind a load balancer.
* **Observability:** 100% trace coverage of RAG queries, LLM token counts, and retrieval scores via OpenTelemetry.