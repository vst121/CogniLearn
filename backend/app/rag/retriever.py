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
        
        # Parent span wrapping the entire hybrid retrieval operation
        with tracer.start_as_current_span("BilingualHybridRetriever.hybrid_search") as span:
            # Set high-level query metadata as attributes
            span.set_attribute("rag.query_text", query_text)
            span.set_attribute("rag.course_code", course_code)
            span.set_attribute("rag.language", language)
            span.set_attribute("rag.top_k", top_k)
            span.set_attribute("rag.rrf_k", rrf_k)

            fts_config = "german" if language.lower() == "de" else "english"

            async with self.db_pool.acquire() as conn:
                # 1. Dense Vector Similarity Search Span
                with tracer.start_as_current_span("vector_search") as vec_span:
                    vec_span.set_attribute("rag.candidate_limit", top_k * 2)
                    
                    vector_query = """
                        SELECT id, course_code, language, chapter, section, content,
                               1 - (embedding <=> $1::vector) AS vector_score
                        FROM course_documents
                        WHERE course_code = $2 AND language = $3
                        ORDER BY embedding <=> $1::vector
                        LIMIT $4;
                    """
                    vector_results = await conn.fetch(
                        vector_query, str(query_embedding), course_code, language, top_k * 2
                    )
                    vec_span.set_attribute("rag.vector_results_count", len(vector_results))

                # 2. Sparse Full-Text Keyword Search Span
                with tracer.start_as_current_span("fts_search") as fts_span:
                    fts_span.set_attribute("rag.fts_config", fts_config)
                    fts_span.set_attribute("rag.candidate_limit", top_k * 2)

                    fts_query = f"""
                        SELECT id, course_code, language, chapter, section, content,
                               ts_rank_cd(to_tsvector('{fts_config}', content), plainto_tsquery('{fts_config}', $1)) AS fts_score
                        FROM course_documents
                        WHERE course_code = $2 AND language = $3 
                          AND to_tsvector('{fts_config}', content) @@ plainto_tsquery('{fts_config}', $1)
                        ORDER BY fts_score DESC
                        LIMIT $4;
                    """
                    fts_results = await conn.fetch(
                        fts_query, query_text, course_code, language, top_k * 2
                    )
                    fts_span.set_attribute("rag.fts_results_count", len(fts_results))

            # 3. Reciprocal Rank Fusion (RRF) Re-ranking Span
            with tracer.start_as_current_span("rrf_fusion") as rrf_span:
                scores: Dict[str, float] = {}
                doc_map: Dict[str, Dict[str, Any]] = {}

                for rank, doc in enumerate(vector_results):
                    doc_id = str(doc["id"])
                    doc_map[doc_id] = dict(doc)
                    scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))

                for rank, doc in enumerate(fts_results):
                    doc_id = str(doc["id"])
                    if doc_id not in doc_map:
                        doc_map[doc_id] = dict(doc)
                    scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))

                reranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
                
                results = []
                for doc_id in reranked_ids:
                    item = doc_map[doc_id]
                    item["rrf_score"] = scores[doc_id]
                    results.append(item)

                rrf_span.set_attribute("rag.total_unique_candidates", len(doc_map))
                rrf_span.set_attribute("rag.returned_results_count", len(results))

            span.set_attribute("rag.final_results_count", len(results))
            return results