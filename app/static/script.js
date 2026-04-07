const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Authentication dynamically injected from app.html

function appendMessage(sender, content, agentName = null) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
    // Parse markdown if it's the AI
    let parsedContent = content;
    if (sender === 'ai' && typeof marked !== 'undefined') {
        parsedContent = marked.parse(content);
    }

    const badgeHTML = agentName ? `<span class="agent-badge">${agentName}</span>` : '';
    
    msgDiv.innerHTML = `
        <div class="message-bubble">
            ${badgeHTML}
            ${parsedContent}
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'ai');
    loadingDiv.id = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="message-bubble loading-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideLoading() {
    const el = document.getElementById('loading-indicator');
    if (el) el.remove();
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage('user', message);
    userInput.value = '';
    sendBtn.disabled = true;

    showLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${window.AUTH_TOKEN}`
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            appendMessage('ai', data.response, data.agent_used);
        } else {
            appendMessage('ai', `Error: ${data.detail || 'Something went wrong.'}`);
        }
    } catch (error) {
        hideLoading();
        appendMessage('ai', `Connection Error: ${error.message}`);
    }

    sendBtn.disabled = false;
    userInput.focus();
}

// Handle Sidebar Clicks
const menuStudyFlow = document.getElementById('menu-study-flow');
const menuMyTasks = document.getElementById('menu-my-tasks');
const menuSchedule = document.getElementById('menu-schedule');

// View Containers
const viewStudyFlow = document.getElementById('view-study-flow');
const viewMyTasks = document.getElementById('view-my-tasks');
const viewSchedule = document.getElementById('view-schedule');
const workspaceTitle = document.getElementById('workspace-title');
const workspaceSubtitle = document.getElementById('workspace-subtitle');

function setActiveMenu(element) {
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
}

function switchView(viewElement, title, subtitle) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    viewElement.classList.remove('hidden');
    workspaceTitle.innerText = title;
    workspaceSubtitle.innerText = subtitle;
}

async function fetchDashboardData(prompt, containerId, loadingText) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<div class="dashboard-placeholder">${loadingText}</div>`;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${window.AUTH_TOKEN}`
            },
            body: JSON.stringify({ message: prompt })
        });
        const data = await response.json();
        
        if (response.ok) {
            let parsedContent = data.response;
            if (typeof marked !== 'undefined') {
                parsedContent = marked.parse(data.response);
            }
            container.innerHTML = parsedContent;
        } else {
            container.innerHTML = `<div class="dashboard-placeholder" style="color: #ef4444;">Error: ${data.detail || 'Failed to load.'}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="dashboard-placeholder" style="color: #ef4444;">Connection Error: ${error.message}</div>`;
    }
}

menuStudyFlow.addEventListener('click', () => {
    setActiveMenu(menuStudyFlow);
    switchView(viewStudyFlow, "Study Assistant", "Powered by LangGraph & Vertex AI");
});

menuMyTasks.addEventListener('click', () => {
    setActiveMenu(menuMyTasks);
    switchView(viewMyTasks, "My Tasks", "Your pending assignments and goals");
    fetchDashboardData("What are my current pending tasks? Please firmly list them in a Markdown table.", "tasks-content", "Pulling your pending tasks securely from Firestore...");
});

menuSchedule.addEventListener('click', () => {
    setActiveMenu(menuSchedule);
    switchView(viewSchedule, "Study Schedule", "Optimized time-blocked plan");
    fetchDashboardData("Please generate a realistic study schedule for me based on my current tasks.", "schedule-content", "Generating your optimized study schedule via Vertex AI...");
});


sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
