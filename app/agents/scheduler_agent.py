from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent
from app.config import config
from app.tools.firestore_tools import get_pending_tasks

def get_scheduler_agent_executor():
    llm = ChatVertexAI(model_name="gemini-2.5-flash", project=config.PROJECT_ID)
    tools = [get_pending_tasks]
    agent_executor = create_react_agent(llm, tools)
    return agent_executor

def run_scheduler_agent(user_input: str, user_id: str) -> str:
    executor = get_scheduler_agent_executor()
    sys_prompt = "You are the Scheduler Agent. Your goal is to create structured, time-blocked study plans for students. Retrieve their pending tasks using the tool. Given those tasks and any time constraints mentioned by the user, generate a realistic study schedule. Format the output elegantly as a Markdown schedule."
    context_input = f"User ID: {user_id}\nRequest: {user_input}"
    response = executor.invoke({"messages": [("system", sys_prompt), ("user", context_input)]})
    msg_content = response["messages"][-1].content
    if isinstance(msg_content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in msg_content)
    return str(msg_content)
