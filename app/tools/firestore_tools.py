from langchain_core.tools import tool
from google.cloud.firestore_v1.base_query import FieldFilter
from app.database import get_db
import uuid

@tool
def add_task(user_id: str, title: str, description: str = "", due_date: str = "") -> str:
    """Adds a new task to the user's task list in Firestore. Use this when the user wants to add a task, homework, or assignment to their backlog."""
    db = get_db()
    if not db:
        return "Error: Database is not connected."
    
    task_id = str(uuid.uuid4())
    task_data = {
        "id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "status": "pending",
        "due_date": due_date
    }
    
    db.collection("tasks").document(task_id).set(task_data)
    return f"Successfully added task: {title} (ID: {task_id})"

@tool
def get_pending_tasks(user_id: str) -> str:
    """Retrieves all pending tasks for a specific user from Firestore. Use this to view the user's tasks."""
    db = get_db()
    if not db:
        return "Error: Database is not connected."
    
    tasks_ref = db.collection("tasks").where(filter=FieldFilter("user_id", "==", user_id)).where(filter=FieldFilter("status", "==", "pending")).stream()
    
    tasks = []
    for doc in tasks_ref:
        tasks.append(doc.to_dict())
        
    if not tasks:
        return "No pending tasks found."
        
    result = "Pending tasks:\n"
    for t in tasks:
        result += f"- {t.get('title')} (Due: {t.get('due_date', 'None')})\n"
    return result

@tool
def complete_task(task_id: str) -> str:
    """Marks a specific task as completed in Firestore."""
    from datetime import datetime, timezone
    db = get_db()
    if not db:
        return "Error: Database is not connected."
    
    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()
    
    if doc.exists:
        doc_ref.update({
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
        return f"Task {task_id} marked as completed."
    return f"Task {task_id} not found."
