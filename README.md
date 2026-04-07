# AgentX StudyFlow 🚀

AgentX StudyFlow is a **Multi-Agent Study Productivity Assistant** designed to help students learn complex concepts, manage study tasks, and efficiently create structured study plans. 

Unlike traditional tools that handle only one aspect of studying, AgentX StudyFlow integrates learning, task management, and scheduling into a single intelligent workflow powered by multiple specialized AI agents.

---

## 🧩 System Architecture

The core of the system relies on an Agentic framework built using **LangGraph** and **Google Gemini**, exposed via a high-performance **FastAPI** web server. The architecture consists of one primary routing agent and three specialized sub-agents.

### The Agents
1. **🤖 Primary Agent (Coordinator):**
   Acts as the brain of the system. It uses a lightweight Gemini LLM to analyze the user's intent and intelligently routes the request to the most appropriate sub-agent.
  
2. **📚 Study Agent:**
   Designed to explain concepts precisely and clearly to students. Equipped with LangChain Web Tools (**Wikipedia, DuckDuckGo Search, and ArXiv**), it dynamically browses the web for the latest general knowledge and academic research before generating an explanation.

3. **✅ Task Agent:**
   Acts as a task manager. It connects securely to **Google Cloud Firestore** to read, write, and update the user's study tasks, homework, and assignments in real time.

4. **📅 Scheduler Agent:**
   Acts as a personal planner. It retrieves pending tasks from Firestore and generates a structured, realistic time-blocked study schedule based on the user's workload.

---

## 🛠️ Technology Stack

- **Orchestration:** LangGraph & LangChain 
- **LLM Engine:** Google Gemini (Vertex AI / GenAI SDK)
- **Database:** Google Cloud Firestore (Native Mode)
- **Backend API:** FastAPI (Python) & Uvicorn
- **Containerization:** Docker (Ready for Google Cloud Run)

---

## ⚙️ Setup & Installation

Follow these steps to run the multi-agent system locally:

### 1. Prerequisites
- Python 3.9+
- A Google Cloud Platform (GCP) Account with an active **Firestore DataBase**.
- A Google AI Studio or Vertex AI **Gemini API Key**.

### 2. Environment Variables
Create a `.env` file in the root directory and add the following keys. Ensure your GCP Service Account JSON key is downloaded and placed in the project root.

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials.json
PROJECT_ID=your-gcp-project-id
```

### 3. Installation
Create a virtual environment and install the required dependencies:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Running the Server
Start the FastAPI server utilizing `uvicorn`. (We bind it to port 8080 just in case 8000 is occupied):
```bash
uvicorn app.main:app --port 8080 --reload
```

---

## 🌐 API Usage

Once the server is running on `http://127.0.0.1:8080`, it serves a beautiful chat interface directly!

1. Navigate to **http://localhost:8080/** in your browser to interact with the Student Interface.
2. Alternatively, navigate to **http://localhost:8080/docs** to test the API directly via Swagger UI.
3. Submit a JSON payload to test the agents:

**Example Request:**
```json
{
  "user_id": "student-123",
  "message": "Can you explain what Action Potential is in biology?"
}
```

**Example Response:**
```json
{
  "agent_used": "Study Agent",
  "response": "An action potential is a rapid sequence of changes in the voltage across a cell membrane...",
  "data": null
}
```
