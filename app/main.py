from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.models.schemas import ChatRequest, ChatResponse
from app.agents.primary_agent import run_primary_coordinator

app = FastAPI(title="AgentX StudyFlow", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        agent_name, agent_response = run_primary_coordinator(request.message, request.user_id)
        return ChatResponse(
            agent_used=agent_name,
            response=agent_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for the frontend UI (must be at the bottom to avoid shadowing API routes)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
