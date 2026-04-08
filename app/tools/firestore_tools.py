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
def complete_task(user_id: str, task_title: str) -> str:
    """Marks a task as completed by its name/title. Use this when the user says they finished or completed a specific task. Search by the task title, not an ID."""
    from datetime import datetime, timezone
    db = get_db()
    if not db:
        return "Error: Database is not connected."

    # Search for pending tasks matching this user + title (case-insensitive partial match)
    tasks_ref = db.collection("tasks") \
        .where(filter=FieldFilter("user_id", "==", user_id)) \
        .where(filter=FieldFilter("status", "==", "pending")) \
        .stream()

    matched = []
    for doc in tasks_ref:
        t = doc.to_dict()
        if task_title.lower() in t.get("title", "").lower():
            matched.append((doc.id, t.get("title")))

    if not matched:
        return f"No pending task found with the name '{task_title}'. Please check the task name and try again."

    if len(matched) > 1:
        names = ", ".join(f'"{m[1]}"' for m in matched)
        return f"Multiple tasks match '{task_title}': {names}. Please be more specific."

    doc_id, title = matched[0]
    db.collection("tasks").document(doc_id).update({
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat()
    })
    return f"✅ Task '{title}' has been marked as completed!"
