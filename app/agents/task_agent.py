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
    sys_prompt = "You are the Task Agent. Your job is to help the user manage their tasks, homework, and assignments. Extract the relevant information (user_id is provided in the input, task title, description, due date) and call the necessary tools to read or write database content. Confirm the action to the user once the tool finishes executing. CRITICAL: When the user asks to view or list their tasks, you MUST format the resulting tasks elegantly as a Markdown table with columns like Task, Description, and Due Date."
    context_input = f"User ID: {user_id}\nRequest: {user_input}"
    response = executor.invoke({"messages": [("system", sys_prompt), ("user", context_input)]})
    msg_content = response["messages"][-1].content
    if isinstance(msg_content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in msg_content)
    return str(msg_content)
