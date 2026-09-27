import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
import asyncpg

from app.rag.retriever import BilingualHybridRetriever
from app.agents.state import AgentRequest, AgentResponse, Citation

# System prompts for dynamic language response
SYSTEM_PROMPTS = {
    "citation": {
        "en": (
            "You are CogniLearn's Q&A Citation Agent. Answer the student's question accurately using ONLY "
            "the provided course context documents. Include explicit citations to chapters and sections. "
            "If the answer is not in the context, politely state that it isn't covered in the material."
        ),
        "de": (
            "Du bist der CogniLearn Q&A-Zitier-Agent. Beantworte die Frage des Studenten präzise und AUSSCHLIESSLICH "
            "auf Basis der bereitgestellten Kursdokumente. Füge explizite Zitate zu Kapiteln und Abschnitten hinzu. "
            "Wenn die Antwort nicht im Kontext enthalten ist, weise höflich darauf hin."
        )
    },
    "socratic": {
        "en": (
            "You are CogniLearn's Socratic Tutor. Do NOT give the direct answer away immediately. "
            "Use the provided course context to guide the student towards understanding. Ask a probing follow-up "
            "question that helps them break down the concept step-by-step."
        ),
        "de": (
            "Du bist der Sokratische Tutor von CogniLearn. Verrate die direkte Antwort NICHT sofort. "
            "Nutze den bereitgestellten Kurskontext, um den Studenten schrittweise zur Lösung zu führen. "
            "Stelle eine gezielte Nachfrage, die dem Studenten hilft, das Konzept selbst zu erschließen."
        )
    }
}

class AgentOrchestrator:
    def __init__(self, db_pool: asyncpg.Pool):
        self.retriever = BilingualHybridRetriever(db_pool)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

    async def run(self, request: AgentRequest) -> AgentResponse:
        # 1. Mock or Real Embedding Generation
        # In production, replace with client.embeddings.create(...)
        mock_embedding = [0.01] * 1536 

        # 2. Retrieve relevant docs via Hybrid Search (Vector + BM25)
        context_docs = await self.retriever.hybrid_search(
            query_text=request.query,
            query_embedding=mock_embedding,
            course_code=request.course_code,
            language=request.language,
            top_k=3
        )

        # 3. Format citations and context block
        citations = []
        context_text_blocks = []
        for doc in context_docs:
            citations.append(Citation(
                chapter=doc["chapter"],
                section=doc["section"],
                content_snippet=doc["content"][:150] + "...",
                relevance_score=round(doc["rrf_score"], 4)
            ))
            context_text_blocks.append(
                f"[{doc['chapter']} - {doc['section']}]\n{doc['content']}"
            )

        formatted_context = "\n\n".join(context_text_blocks)
        
        # 4. Select prompt based on mode and language
        system_prompt = SYSTEM_PROMPTS[request.mode][request.language]
        
        user_message = f"Course Context:\n{formatted_context}\n\nStudent Query: {request.query}"

        # 5. Fallback response if OpenAI key is not configured locally yet
        if not os.getenv("OPENAI_API_KEY"):
            return AgentResponse(
                answer=f"[{request.language.upper()} - {request.mode.upper()}] Context retrieved successfully. Configure OPENAI_API_KEY to generate LLM completions.",
                language=request.language,
                mode=request.mode,
                citations=citations
            )

        # 6. Call OpenAI Completion
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        completion = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3 if request.mode == "citation" else 0.7
        )

        llm_answer = completion.choices[0].message.content

        return AgentResponse(
            answer=llm_answer,
            language=request.language,
            mode=request.mode,
            citations=citations
        )