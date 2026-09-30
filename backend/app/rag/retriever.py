import json
import asyncpg
from typing import List, Dict, Any
from opentelemetry import trace

# Initialize tracer for retriever module
tracer = trace.get_tracer(__name__)


class BilingualHybridRetriever:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def hybrid_search(
        self, 
        query_text: str, 
        query_embedding: List[float], 
        course_code: str,
        language: str = "en",
        top_k: int = 5, 
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        
        # Parent span wrapping the full retrieval operation
        with tracer.start_as_current_span("BilingualHybridRetriever.hybrid_search") as span:
            span.set_attribute("rag.query_text", query_text)
            span.set_attribute("rag.course_code", course_code)
            span.set_attribute("rag.language", language)
            span.set_attribute("rag.top_k", top_k)
            span.set_attribute("rag.rrf_k", rrf_k)

            # 1. Fix SQL Injection Risk: Whitelist language configuration
            lang_config_map = {
                "de": "german",
                "en": "english"
            }
            fts_config = lang_config_map.get(language.lower(), "english")
            span.set_attribute("rag.fts_config", fts_config)

            # 2. Fix Vector Format: Explicit JSON vector serialization for pgvector
            embedding_str = json.dumps(query_embedding)
            candidate_limit = top_k * 2

            # 3 & 5. Optimized Single CTE Query (Uses stored fts_vector index & eliminates multi-roundtrips)
            combined_query = """
            WITH vector_search AS (
                SELECT 
                    id, course_code, language, chapter, section, content,
                    ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) AS rank
                FROM course_documents
                WHERE course_code = $2 AND language = $3
                ORDER BY embedding <=> $1::vector
                LIMIT $5
            ),
            fts_search AS (
                SELECT 
                    id, course_code, language, chapter, section, content,
                    ROW_NUMBER() OVER (
                        ORDER BY ts_rank_cd(fts_vector, plainto_tsquery($4, $6)) DESC
                    ) AS rank
                FROM course_documents
                WHERE course_code = $2 
                  AND language = $3 
                  AND fts_vector @@ plainto_tsquery($4, $6)
                LIMIT $5
            )
            SELECT 
                COALESCE(v.id, f.id) AS id,
                COALESCE(v.course_code, f.course_code) AS course_code,
                COALESCE(v.language, f.language) AS language,
                COALESCE(v.chapter, f.chapter) AS chapter,
                COALESCE(v.section, f.section) AS section,
                COALESCE(v.content, f.content) AS content,
                (COALESCE(1.0 / ($7 + v.rank), 0.0) + COALESCE(1.0 / ($7 + f.rank), 0.0)) AS rrf_score
            FROM vector_search v
            FULL OUTER JOIN fts_search f ON v.id = f.id
            ORDER BY rrf_score DESC
            LIMIT $8;
            """

            # Trace single CTE database execution span
            with tracer.start_as_current_span("db_cte_hybrid_search") as db_span:
                db_span.set_attribute("db.candidate_limit", candidate_limit)
                
                async with self.db_pool.acquire() as conn:
                    records = await conn.fetch(
                        combined_query,
                        embedding_str,     # $1
                        course_code,       # $2
                        language,          # $3
                        fts_config,        # $4
                        candidate_limit,   # $5
                        query_text,        # $6
                        rrf_k,             # $7
                        top_k              # $8
                    )
                db_span.set_attribute("db.fetched_records_count", len(records))

            results = [dict(record) for record in records]
            span.set_attribute("rag.final_results_count", len(results))

            return results