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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- HNSW Index for rapid vector retrieval
CREATE INDEX IF NOT EXISTS course_docs_embedding_hnsw_idx 
ON course_documents USING hnsw (embedding vector_cosine_ops);

-- English Full-Text Search Index
CREATE INDEX IF NOT EXISTS course_docs_content_fts_en_idx 
ON course_documents USING gin(to_tsvector('english', content));

-- German Full-Text Search Index
CREATE INDEX IF NOT EXISTS course_docs_content_fts_de_idx 
ON course_documents USING gin(to_tsvector('german', content));