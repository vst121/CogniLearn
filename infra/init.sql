CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS course_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(50) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    chapter VARCHAR(100) NOT NULL,
    section VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    fts_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', content)
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- 1. GIN Index for Sparse Full-Text Keyword Search (FTS)
CREATE INDEX IF NOT EXISTS idx_course_docs_fts 
ON course_documents USING GIN (fts_vector);

-- 2. HNSW Index for Dense Vector Similarity Search
CREATE INDEX IF NOT EXISTS idx_course_docs_embedding 
ON course_documents USING hnsw (embedding vector_cosine_ops);

-- 3. Composite B-Tree Index for Metadata Filtering
CREATE INDEX IF NOT EXISTS idx_course_docs_metadata 
ON course_documents (course_code, language);