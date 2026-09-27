from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.agents.state import AgentRequest, AgentResponse
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()

@router.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: AgentRequest):
    if not db.pool:
        raise HTTPException(status_code=500, detail="Database connection pool is not initialized.")
    
    orchestrator = AgentOrchestrator(db.pool)
    response = await orchestrator.run(request)
    return response