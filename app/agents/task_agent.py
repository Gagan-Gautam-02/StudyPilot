def get_task_agent_executor():
    from langchain_google_vertexai import ChatVertexAI
    from langgraph.prebuilt import create_react_agent
    from app.config import config
    from app.tools.firestore_tools import add_task, get_pending_tasks, complete_task
    llm = ChatVertexAI(model_name="gemini-2.5-flash", project=config.PROJECT_ID)
    tools = [add_task, get_pending_tasks, complete_task]
    agent_executor = create_react_agent(llm, tools)
    return agent_executor

def run_task_agent(user_input: str, user_id: str) -> str:
    executor = get_task_agent_executor()
    sys_prompt = "You are the Task Agent. Your job is to help the user manage their tasks, homework, and assignments. The user_id is provided in the input context — always pass it to every tool call. When adding a task, extract the title, description, and due date. When the user says they finished or completed a task, call complete_task with their user_id and the task name EXACTLY as they mentioned it (do NOT make up an ID). When listing tasks, format the result elegantly as a Markdown table with columns: Task, Description, Due Date. Confirm every action clearly to the user."
    context_input = f"User ID: {user_id}\nRequest: {user_input}"
    response = executor.invoke({"messages": [("system", sys_prompt), ("user", context_input)]})
    msg_content = response["messages"][-1].content
    if isinstance(msg_content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in msg_content)
    return str(msg_content)
