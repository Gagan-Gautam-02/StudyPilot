const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// ─── Conversational Quick Replies (no API call needed) ───────────────────────
const QUICK_REPLIES = [
    {
        pattern: /^(hi|hey|hello|sup|yo|hiya|howdy)[\s!?.]*$/i,
        reply: "👋 Hey there! I'm **AgentX**, your AI study companion.\n\nHere's what I can do for you:\n- 📚 **Explain** any concept or topic\n- ✅ **Add or view tasks** and assignments\n- 📅 **Generate a study schedule** based on your workload\n\nWhat would you like to do today?"
    },
    {
        pattern: /^(how are you|how r u|how do you do|what's up|whats up)[\s!?.]*$/i,
        reply: "I'm running at full power and ready to help you study smarter! 🚀\n\nTell me — do you need help understanding a topic, managing tasks, or planning your week?"
    },
    {
        pattern: /^(thanks|thank you|thx|ty|cheers)[\s!?.]*$/i,
        reply: "You're very welcome! 😊 Always here when you need me. Good luck with your studies!"
    },
    {
        pattern: /^(bye|goodbye|see you|cya|later)[\s!?.]*$/i,
        reply: "Goodbye! 👋 Come back anytime you need help studying. You've got this! 💪"
    },
    {
        pattern: /^(help|what can you do|what do you do|capabilities)[\s!?.]*$/i,
        reply: "Here's everything I can help you with:\n\n**📚 Study Mode**\nAsk me to explain any concept — physics, history, coding, you name it. I use Wikipedia, ArXiv, and DuckDuckGo to give accurate, cited answers.\n\n**✅ Task Manager**\nSay things like:\n- *\"Add task: finish math homework, due Friday\"*\n- *\"Show my pending tasks\"*\n- *\"Mark task [id] as complete\"*\n\n**📅 Study Scheduler**\nSay *\"Make a study plan for this week\"* and I'll generate a time-blocked schedule based on your real pending tasks.\n\n**📊 Stats**\nCheck the **My Stats** tab on the left to see your completion rate and performance!"
    }
];

function appendMessage(sender, content, agentName = null) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
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

    // Check quick replies first (instant, no API call)
    for (const qr of QUICK_REPLIES) {
        if (qr.pattern.test(message)) {
            showLoading();
            await new Promise(r => setTimeout(r, 500)); // brief thinking delay
            hideLoading();
            appendMessage('ai', qr.reply, 'AgentX');
            sendBtn.disabled = false;
            userInput.focus();
            return;
        }
    }

    showLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${window.AUTH_TOKEN}`
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        hideLoading();
        
        if (response.ok) {
            appendMessage('ai', data.response, data.agent_used);
        } else {
            appendMessage('ai', `❌ Error: ${data.detail || 'Something went wrong.'}`);
        }
    } catch (error) {
        hideLoading();
        appendMessage('ai', `❌ Connection Error: ${error.message}`);
    }

    sendBtn.disabled = false;
    userInput.focus();
}

// ─── Sidebar & View Switching ─────────────────────────────────────────────────
const menuStudyFlow = document.getElementById('menu-study-flow');
const menuMyTasks   = document.getElementById('menu-my-tasks');
const menuSchedule  = document.getElementById('menu-schedule');
const menuStats     = document.getElementById('menu-stats');

const viewStudyFlow = document.getElementById('view-study-flow');
const viewMyTasks   = document.getElementById('view-my-tasks');
const viewSchedule  = document.getElementById('view-schedule');
const viewStats     = document.getElementById('view-stats');
const workspaceTitle    = document.getElementById('workspace-title');
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
            if (typeof marked !== 'undefined') parsedContent = marked.parse(data.response);
            container.innerHTML = parsedContent;
        } else {
            container.innerHTML = `<div class="dashboard-placeholder" style="color:#ef4444;">Error: ${data.detail || 'Failed to load.'}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="dashboard-placeholder" style="color:#ef4444;">Connection Error: ${error.message}</div>`;
    }
}

// ─── Stats Fetching ───────────────────────────────────────────────────────────
async function fetchStats() {
    try {
        const response = await fetch('/api/stats', {
            headers: { 'Authorization': `Bearer ${window.AUTH_TOKEN}` }
        });
        const d = await response.json();

        document.getElementById('val-total').textContent     = d.total;
        document.getElementById('val-completed').textContent = d.completed;
        document.getElementById('val-pending').textContent   = d.pending;
        document.getElementById('val-ontime').textContent    = d.on_time;
        document.getElementById('val-overdue').textContent   = d.overdue;
        document.getElementById('val-rate').textContent      = d.completion_rate + '%';

        // Animate progress bar
        const fill = document.getElementById('progress-fill');
        fill.style.width = '0%';
        setTimeout(() => { fill.style.width = d.completion_rate + '%'; }, 100);

        // Color-code stat cards
        document.getElementById('stat-completed').style.borderColor = '#22c55e';
        document.getElementById('stat-pending').style.borderColor   = '#f59e0b';
        document.getElementById('stat-ontime').style.borderColor    = '#06b6d4';
        document.getElementById('stat-overdue').style.borderColor   = '#ef4444';

    } catch (err) {
        document.getElementById('stats-grid').innerHTML =
            `<div class="dashboard-placeholder" style="color:#ef4444;">Failed to load stats: ${err.message}</div>`;
    }
}

// ─── Menu Listeners ───────────────────────────────────────────────────────────
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

menuStats.addEventListener('click', () => {
    setActiveMenu(menuStats);
    switchView(viewStats, "My Stats", "Track your academic performance");
    fetchStats();
});

// ─── Send Button ──────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
