from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent
from app.config import config
from app.tools.web_tools import get_web_tools

def get_study_agent_executor():
    llm = ChatVertexAI(model_name="gemini-2.5-flash", project=config.PROJECT_ID)
    tools = get_web_tools()
    agent_executor = create_react_agent(llm, tools)
    return agent_executor

def run_study_agent(user_input: str) -> str:
    executor = get_study_agent_executor()
    sys_prompt = "You are the Study Agent, a helpful tutor. Explain concepts clearly and simply to students. You have access to Wikipedia, DuckDuckGo, and ArXiv to find accurate information. Use these tools if you don't know the answer or need up-to-date context. If providing academic answers, cite your tool's sources."
    response = executor.invoke({"messages": [("system", sys_prompt), ("user", user_input)]})
    msg_content = response["messages"][-1].content
    if isinstance(msg_content, list):
        return "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in msg_content)
    return str(msg_content)
