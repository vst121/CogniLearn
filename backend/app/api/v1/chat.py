from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.core.ratelimit import RedisRateLimiter
from app.agents.orchestrator import AgentOrchestrator
from app.core.db import db  
from app.core.config import settings

router = APIRouter()
rate_limiter = RedisRateLimiter()


# --- Pydantic Request & Response Models ---

class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1, example="What is Reciprocal Rank Fusion?")
    course_code: str = Field(..., example="DL-101")
    mode: str = Field("citation", example="citation")  # "citation" or "socratic"
    language: str = Field("en", example="en")          # "en" or "de"


class SourceCitation(BaseModel):
    chapter: Optional[str] = None
    section: Optional[str] = None
    rrf_score: Optional[float] = None


class AgentResponse(BaseModel):
    agent: str
    answer: str
    sources: List[SourceCitation] = []


# --- Dependency Factories ---

async def rate_limit_dependency(request: Request):
    await rate_limiter.check_rate_limit(request, limit=50, window=60)


def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)  


# --- API Endpoint ---

@router.post(
    "/chat", 
    response_model=AgentResponse, 
    dependencies=[Depends(rate_limit_dependency)],
    summary="Process user query through Multi-Agent RAG Orchestrator"
)
async def chat_endpoint(
    payload: AgentRequest,
    openai_client: AsyncOpenAI = Depends(get_openai_client)
):
    if not db.pool:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection pool is not initialized."
        )

    try:
        orchestrator = AgentOrchestrator(
            db_pool=db.pool, 
            openai_client=openai_client
        )
        
        response = await orchestrator.process_query(
            query=payload.query,
            course_code=payload.course_code,
            mode=payload.mode,
            language=payload.language
        )
        
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the agent request: {str(e)}"
        )