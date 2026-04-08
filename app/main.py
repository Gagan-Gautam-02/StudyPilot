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

import os

# Initialize Firebase Admin securely using the same service account
if not firebase_admin._apps:
    try:
        if config.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(config.GOOGLE_APPLICATION_CREDENTIALS):
            cred = credentials.Certificate(config.GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to Google Cloud Native Authentication Environment Variables
            firebase_admin.initialize_app()
        print("Firebase Admin strictly initialized on Boot")
    except Exception as e:
        print(f"CRITICAL WARNING: Firebase Admin failed to initialize on Boot. Authentication features will fail. Error: {e}")

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

@app.get("/api/stats")
def stats_endpoint(user_id: str = Depends(verify_token)):
    """Returns task stats for the authenticated user."""
    try:
        from app.database import get_db
        from google.cloud.firestore_v1.base_query import FieldFilter
        from datetime import datetime, timezone
        db = get_db()
        if not db:
            return {"total": 0, "pending": 0, "completed": 0, "on_time": 0, "overdue": 0}

        all_tasks = list(db.collection("tasks").where(
            filter=FieldFilter("user_id", "==", user_id)
        ).stream())

        total     = len(all_tasks)
        pending   = 0
        completed = 0
        on_time   = 0
        overdue   = 0
        now       = datetime.now(timezone.utc)

        for doc in all_tasks:
            t = doc.to_dict()
            status = t.get("status", "pending")
            if status == "pending":
                pending += 1
            else:
                completed += 1
                due_raw   = t.get("due_date", "")
                done_raw  = t.get("completed_at", "")
                if due_raw and done_raw:
                    try:
                        due_dt  = datetime.fromisoformat(due_raw).replace(tzinfo=timezone.utc)
                        done_dt = datetime.fromisoformat(done_raw)
                        if done_dt.tzinfo is None:
                            done_dt = done_dt.replace(tzinfo=timezone.utc)
                        if done_dt <= due_dt:
                            on_time += 1
                        else:
                            overdue += 1
                    except Exception:
                        pass

        rate = round((completed / total * 100)) if total > 0 else 0
        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "on_time": on_time,
            "overdue": overdue,
            "completion_rate": rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for the frontend UI (must be at the bottom to avoid shadowing API routes)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
