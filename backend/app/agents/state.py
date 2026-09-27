from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Citation(BaseModel):
    chapter: str
    section: str
    content_snippet: str
    relevance_score: float

class AgentRequest(BaseModel):
    query: str
    course_code: str
    language: Literal["en", "de"] = "en"
    mode: Literal["citation", "socratic"] = "citation"
    chat_history: Optional[List[dict]] = []

class AgentResponse(BaseModel):
    answer: str
    language: str
    mode: str
    citations: List[Citation] = []
    follow_up_question: Optional[str] = None
