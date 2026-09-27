import asyncpg
from typing import List, Dict, Any

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
        
        # Determine language dictionary for Postgres text search
        fts_config = "german" if language.lower() == "de" else "english"

        async with self.db_pool.acquire() as conn:
            # 1. Dense Vector Similarity Search
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

            # 2. Sparse Full-Text Keyword Search (BM25 equivalent)
            fts_query = f"""
                SELECT id, course_code, language, chapter, section, content,
                       ts_rank_cd(to_tsvector('{fts_config}', content), plainto_tsquery('{fts_config}', $1)) AS fts_score
                FROM course_documents
                WHERE course_code = $2 AND language = $3 
                  AND to_tsvector('{fts_config}', content) @@ plainto_tsquery('{fts_config}', $1)
                ORDER BY fts_score DESC
                LIMIT $4;
            """
            fts_results = await conn.fetch(fts_query, query_text, course_code, language, top_k * 2)

        # 3. Reciprocal Rank Fusion (RRF) Re-ranking
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

        # Sort documents by top RRF scores
        reranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
        
        results = []
        for doc_id in reranked_ids:
            item = doc_map[doc_id]
            item["rrf_score"] = scores[doc_id]
            results.append(item)

        return results