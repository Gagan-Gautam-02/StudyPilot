from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth

from app.models.schemas import ChatRequest, ChatResponse
from app.agents.primary_agent import run_primary_coordinator
from app.config import config

app = FastAPI(title="AgentX StudyFlow", version="1.0.0")

# Initialize Firebase Admin securely using the same service account
if not firebase_admin._apps:
    cred = credentials.Certificate(config.GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(cred)

security = HTTPBearer()

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(authorization.credentials)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Authentication Token")

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
def chat_endpoint(request: ChatRequest, user_id: str = Depends(verify_token)):
    try:
        agent_name, agent_response = run_primary_coordinator(request.message, user_id)
        return ChatResponse(
            agent_used=agent_name,
            response=agent_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for the frontend UI (must be at the bottom to avoid shadowing API routes)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
