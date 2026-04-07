from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    agent_used: str
    response: str
    data: Optional[Dict[str, Any]] = None

class Task(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    description: Optional[str] = ""
    status: str = "pending" # pending, completed
    due_date: Optional[str] = None
