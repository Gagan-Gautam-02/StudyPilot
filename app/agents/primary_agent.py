from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from app.config import config
from app.agents.study_agent import run_study_agent
from app.agents.task_agent import run_task_agent
from app.agents.scheduler_agent import run_scheduler_agent

def determine_intent(user_input: str) -> str:
    """Uses a lightweight LLM call to classify the intent."""
    llm = ChatVertexAI(model_name="gemini-2.5-flash", project=config.PROJECT_ID)
    
    prompt = PromptTemplate.from_template(
        "You are a router. Analyze the user's prompt and classify the intent into ONE of the following categories: 'STUDY', 'TASK', 'SCHEDULER', or 'UNKNOWN'.\n\n"
        "Categories:\n"
        "- STUDY: The user wants an explanation of a concept, help understanding a topic, or general knowledge.\n"
        "- TASK: The user wants to add, view, or manage a task/homework/assignment in their list.\n"
        "- SCHEDULER: The user wants to create a study plan or generate a schedule based on their tasks.\n"
        "- UNKNOWN: Anything else.\n\n"
        "User Prompt: {input}\n"
        "Category:"
    )
    
    chain = prompt | llm
    intent = chain.invoke({"input": user_input}).content.strip()
    return intent

def run_primary_coordinator(user_input: str, user_id: str) -> tuple[str, str]:
    """Routes the request and returns the agent used and the response."""
    intent = determine_intent(user_input).upper()
    
    if "STUDY" in intent:
        response = run_study_agent(user_input)
        return "Study Agent", response
    elif "TASK" in intent:
        response = run_task_agent(user_input, user_id)
        return "Task Agent", response
    elif "SCHEDULER" in intent:
        response = run_scheduler_agent(user_input, user_id)
        return "Scheduler Agent", response
    else:
        # Fallback to study agent for general conversation or ask for clarification
        return "Primary Agent", "I'm sorry, I'm not sure how to help with that. Are you trying to learn a concept, manage tasks, or create a study schedule?"
