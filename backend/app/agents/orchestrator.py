from typing import List, Dict, Any
import asyncpg
from openai import AsyncOpenAI
from opentelemetry import trace

from app.rag.retriever import BilingualHybridRetriever
from app.agents.citation_agent import CitationAgent
from app.agents.socratic_agent import SocraticAgent

tracer = trace.get_tracer(__name__)


class AgentOrchestrator:
    def __init__(self, db_pool: asyncpg.Pool, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.retriever = BilingualHybridRetriever(db_pool)
        self.citation_agent = CitationAgent(openai_client)
        self.socratic_agent = SocraticAgent(openai_client)

    async def generate_embedding(self, text: str) -> List[float]:
        with tracer.start_as_current_span("generate_embedding"):
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding

    async def process_query(
        self,
        query: str,
        course_code: str,
        mode: str = "citation",  # "citation" or "socratic"
        language: str = "en"
    ) -> Dict[str, Any]:
        with tracer.start_as_current_span("AgentOrchestrator.process_query") as span:
            span.set_attribute("orchestrator.mode", mode)
            span.set_attribute("orchestrator.course_code", course_code)

            # 1. Generate Query Vector
            query_embedding = await self.generate_embedding(query)

            # 2. Perform Hybrid Retrieval (Vector + BM25 via RRF)
            contexts = await self.retriever.hybrid_search(
                query_text=query,
                query_embedding=query_embedding,
                course_code=course_code,
                language=language,
                top_k=4
            )

            # 3. Route query to chosen agent mode
            if mode.lower() == "socratic":
                return await self.socratic_agent.run(query, contexts)
            else:
                return await self.citation_agent.run(query, contexts)