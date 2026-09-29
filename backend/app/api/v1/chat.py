from fastapi import APIRouter, HTTPException, Depends, Request
from app.core.db import db
from app.agents.state import AgentRequest, AgentResponse
from app.agents.orchestrator import AgentOrchestrator
from app.core.ratelimit import RedisRateLimiter

router = APIRouter()
rate_limiter = RedisRateLimiter()

async def rate_limit_dependency(request: Request):
    await rate_limiter.check_rate_limit(request, limit=10, window=60)

@router.post("/chat", response_model=AgentResponse, dependencies=[Depends(rate_limit_dependency)])
async def chat_endpoint(request: AgentRequest):
    if not db.pool:
        raise HTTPException(status_code=500, detail="Database connection pool is not initialized.")
    
    orchestrator = AgentOrchestrator(db.pool)
    response = await orchestrator.run(request)
    return response