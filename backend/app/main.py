from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import (
    connect_to_db,
    close_db_connection   
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    yield
    await close_db_connection()

app = FastAPI(
    title="CogniLearn AI Core",
    version="0.1.0",
    description="Backend AI Core for CogniLearn - Hybrid RAG & Socratic Multi-Agent System",
    lifespan=lifespan,
)

# Enable CORS for local Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CogniLearn AI Core",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return {"message": "Welcome to CogniLearn AI Core API"}

