import os
import streamlit as st
from planner import AgentPlanner
from agent import execute_agent_task

# 1. Page Configuration
st.set_page_config(
    page_title="Autonomous Task Planner Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Premium Design Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .title-container {
        padding: 20px 0px;
        margin-bottom: 20px;
    }
    
    .title-text {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 5px;
        letter-spacing: -0.02em;
    }
    
    .subtitle-text {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 0px;
    }
    
    /* Custom Card */
    .task-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .task-card:hover {
        border-color: rgba(96, 165, 250, 0.3);
        transform: translateY(-2px);
    }
    
    /* Log Messages */
    .log-card {
        padding: 14px;
        margin-bottom: 10px;
        border-radius: 8px;
        font-size: 0.95em;
        line-height: 1.5;
        border: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    .log-thought {
        background: rgba(59, 130, 246, 0.06);
        border-left: 4px solid #3b82f6;
        color: #f1f5f9;
    }
    
    .log-tool_call {
        background: rgba(168, 85, 247, 0.06);
        border-left: 4px solid #a855f7;
        font-family: 'JetBrains Mono', monospace;
        color: #e9d5ff;
        font-size: 0.9em;
    }
    
    .log-tool_response {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #64748b;
        color: #cbd5e1;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88em;
        padding: 10px;
        overflow-x: auto;
    }
    
    .log-system {
        background: rgba(16, 185, 129, 0.06);
        border-left: 4px solid #10b981;
        color: #a7f3d0;
    }
    
    .log-error {
        background: rgba(239, 68, 68, 0.08);
        border-left: 4px solid #ef4444;
        color: #fca5a5;
    }
    
    /* Status Badges */
    .status-badge {
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    
    .status-pending { background: #334155; color: #94a3b8; }
    .status-progress { background: #1e3a8a; color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .status-completed { background: #064e3b; color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .status-failed { background: #7f1d1d; color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    
    .timestamp {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #64748b;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Session State Initialization
if "planner" not in st.session_state:
    st.session_state.planner = AgentPlanner()
if "goal_input" not in st.session_state:
    st.session_state.goal_input = ""
if "final_result" not in st.session_state:
    st.session_state.final_result = None

# Sidebar Configuration
st.sidebar.markdown("### 🛠️ Configuration")

# LLM Provider Selection
provider = st.sidebar.selectbox(
    "Select LLM Provider",
    ["OpenAI", "Google Gemini"],
    index=0
)

# Model Selection and default keys
if provider == "OpenAI":
    model_options = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    default_key = os.environ.get("OPENAI_API_KEY", "")
    key_label = "OpenAI API Key"
    key_help = "Enter your sk-... key. You can also set OPENAI_API_KEY environment variable."
else:
    model_options = ["gemini-2.5-pro", "gemini-1.5-flash", "gemini-2.5-flash"]
    default_key = os.environ.get("GEMINI_API_KEY", "")
    key_label = "Gemini API Key"
    key_help = "Enter your Gemini API key. You can also set GEMINI_API_KEY environment variable."

selected_model = st.sidebar.selectbox("Model", model_options, index=1 if provider == "OpenAI" else 2) # gpt-4o-mini / gemini-2.5-flash default

# API Key Input
api_key = st.sidebar.text_input(
    key_label,
    value=default_key,
    type="password",
    help=key_help
)

# Hyperparameters
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# Preset Examples Helper
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick-Start Scenarios")

presets = {
    "Stock Analysis": (
        "Find the current stock price of Apple (AAPL). Then, calculate its P/E ratio "
        "assuming its EPS is 6.58. Write a markdown report called apple_pe_report.md "
        "containing all these calculations and details."
    ),
    "Gemini Latest News": (
        "Search for the latest news about Google Gemini 2.5 Flash model release. "
        "Summarize the key updates and features, and write them to a text file "
        "named gemini_news_summary.txt."
    ),
    "Geometry Calculator": (
        "Calculate the hypotenuse of a right-angled triangle with sides 24.5 and 18.2. "
        "Also calculate its area. Save the output results to geometry_results.txt."
    )
}

for name, goal_text in presets.items():
    if st.sidebar.button(name, use_container_width=True):
        st.session_state.goal_input = goal_text
        st.session_state.final_result = None
        st.session_state.planner = AgentPlanner()
        # Rerun to populate the text area
        st.rerun()

# 4. Main Page Render
st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">Autonomous Task Planner Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">An Agentic AI that breaks down goals, plans actions, and executes tools autonomously.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Workspace status
st.markdown(f"**📂 Current Workspace:** `{os.getcwd()}`")

# Goal Form
with st.form("goal_form"):
    goal = st.text_area(
        "Define the Goal / Task for the Agent:",
        value=st.session_state.goal_input,
        placeholder="Type a goal here, or select a scenario from the sidebar...",
        height=100
    )
    
    col1, col2 = st.columns([1, 6])
    with col1:
        submit = st.form_submit_button("⚡ Run Agent", use_container_width=True)
    with col2:
        clear = st.form_submit_button("🗑️ Reset", use_container_width=False)

if clear:
    st.session_state.goal_input = ""
    st.session_state.final_result = None
    st.session_state.planner = AgentPlanner()
    st.rerun()

# 5. Execution UI Setup
col_left, col_right = st.columns([2, 3])

with col_left:
    plan_placeholder = st.empty()

with col_right:
    log_placeholder = st.empty()

def update_st_ui():
    """Triggers redrawing of the plan checklist and live execution logs."""
    planner = st.session_state.planner
    
    # RENDER CHECKLIST
    with plan_placeholder.container():
        st.markdown("### 📋 Task Plan Checklist")
        if not planner.tasks:
            st.info("The agent hasn't generated a plan yet. Run a goal to see the plan here.")
        else:
            for t in planner.tasks:
                status = t["status"]
                desc = t["description"]
                res = t["result"]
                
                status_badges = {
                    "pending": '<span class="status-badge status-pending">⏳ Pending</span>',
                    "in_progress": '<span class="status-badge status-progress">🌀 Running</span>',
                    "completed": '<span class="status-badge status-completed">✅ Completed</span>',
                    "failed": '<span class="status-badge status-failed">❌ Failed</span>'
                }
                badge = status_badges.get(status, f'<span class="status-badge">{status}</span>')
                
                result_html = f'<div style="font-size:0.85em; margin-top:6px; color:#94a3b8; border-top:1px solid rgba(255,255,255,0.06); padding-top:4px;">↳ <b>Result:</b> {res}</div>' if res else ""
                
                st.markdown(f"""
                <div class="task-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                        <span style="font-weight: 500; font-size: 0.95rem;">Subtask {t['id']}: {desc}</span>
                        {badge}
                    </div>
                    {result_html}
                </div>
                """, unsafe_allow_html=True)
                
    # RENDER LOGS
    with log_placeholder.container():
        st.markdown("### 🌀 Live Execution Logs")
        if not planner.logs:
            st.info("Logs will appear here once the agent starts execution.")
        else:
            # We can reverse logs to show newest at the top, or keep standard order.
            # Let's keep standard order for sequential reading, but put them in a scrolling container or standard blocks.
            for log in planner.logs:
                ts = log["timestamp"]
                log_type = log["type"]
                msg = log["message"]
                
                if log_type == "system":
                    st.markdown(f'<div class="log-card log-system"><span class="timestamp">[{ts}]</span> ⚙️ {msg}</div>', unsafe_allow_html=True)
                elif log_type == "thought":
                    st.markdown(f'<div class="log-card log-thought"><span class="timestamp">[{ts}]</span> 🤔 <b>Reasoning:</b><br>{msg}</div>', unsafe_allow_html=True)
                elif log_type == "tool_call":
                    st.markdown(f'<div class="log-card log-tool_call"><span class="timestamp">[{ts}]</span> 🛠️ {msg}</div>', unsafe_allow_html=True)
                elif log_type == "tool_response":
                    with st.expander(f"📥 View Tool Output (click to toggle)", expanded=False):
                        st.code(msg)
                elif log_type == "error":
                    st.markdown(f'<div class="log-card log-error"><span class="timestamp">[{ts}]</span> ❌ <b>Error:</b> {msg}</div>', unsafe_allow_html=True)

# Initial UI state render
update_st_ui()

# 6. Run Execution
if submit:
    if not api_key.strip():
        st.error(f"Please provide an API Key for {provider} in the sidebar.")
    elif not goal.strip():
        st.warning("Please enter a goal for the agent.")
    else:
        st.session_state.final_result = None
        st.session_state.planner = AgentPlanner()
        
        with st.spinner("Agent initializing and starting task execution..."):
            try:
                # Execute agent
                final_out = execute_agent_task(
                    provider=provider,
                    model_name=selected_model,
                    api_key=api_key,
                    temperature=temperature,
                    goal=goal,
                    planner=st.session_state.planner,
                    ui_callback=update_st_ui
                )
                st.session_state.final_result = final_out
            except Exception as e:
                st.session_state.planner.add_log("error", f"Fatal application error: {str(e)}")
                update_st_ui()
        st.success("Agent run complete!")

# 7. Final Result and Workspace Files
if st.session_state.final_result:
    st.markdown("---")
    st.markdown("### 🏁 Final Agent Response")
    st.info(st.session_state.final_result)

# File Viewer Section
st.markdown("---")
st.markdown("### 📂 Generated Workspace Files")

def get_workspace_files():
    excluded = ["app.py", "agent.py", "tools.py", "planner.py", "requirements.txt"]
    files = []
    if os.path.exists("."):
        for f in os.listdir("."):
            if os.path.isfile(f) and f not in excluded and not f.startswith("."):
                files.append(f)
    return sorted(files)

workspace_files = get_workspace_files()

if not workspace_files:
    st.info("No generated files found in the workspace directory yet.")
else:
    file_col, view_col = st.columns([1, 3])
    with file_col:
        selected_file = st.selectbox("Select file to view:", workspace_files)
    with view_col:
        if selected_file:
            try:
                with open(selected_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Highlight based on extension
                ext = os.path.splitext(selected_file)[1].lower()
                st.markdown(f"**📄 {selected_file}**")
                if ext == ".md":
                    st.markdown(content)
                else:
                    st.code(content, language="markdown" if ext in [".txt", ".csv"] else ext[1:])
            except Exception as e:
                st.error(f"Error reading file {selected_file}: {str(e)}")
