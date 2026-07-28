# Autonomous Task Planner Agent

An interactive, premium-designed web application dashboard that showcases an **Autonomous Task Planner Agent** using Agentic AI (LLM + Tools), LangChain, and Streamlit. The agent takes a high-level goal, breaks it down into subtasks (planning), and executes them step-by-step using custom tools (web search, calculator, scraping, and file operations), all while displaying live execution progress.

## 🚀 Key Features

1. **Autonomous Planning**: The agent uses an LLM-driven planning tool to automatically break down any high-level objective into an organized checklist of subtasks before executing them.
2. **Dynamic Dashboard UI**: A premium dark-blue design with live-updating task checklists (Pending, Running, Completed, Failed badges) and full agent reasoning logs.
3. **Broad Tool Integration**:
   - 🔍 **Web Search**: DuckDuckGo search integration for real-time information retrieval.
   - 🌐 **Web Scraper**: Web page extraction using BeautifulSoup to read contents.
   - 🧮 **Calculator**: Safe execution of math expressions.
   - 📁 **File Read/Write**: Saves results, reports, or markdown summaries directly into the workspace.
4. **Workspace File Viewer**: Read and verify generated files directly inside the application.
5. **Multiple Model Providers**: Support for both **OpenAI** (GPT-4o, GPT-4o-mini) and **Google Gemini** (Gemini 2.5 Flash, Gemini 2.5 Pro).

---

## 🛠️ Project Structure

- `app.py`: The entry point Streamlit application displaying the visual dashboard, checklists, logs, and workspace file viewer.
- `agent.py`: LangChain tool-calling agent loop, LLM setup, and a custom callback handler to stream execution logs live to the UI.
- `tools.py`: Declarations of custom tools (DuckDuckGo search, beautifulsoup scraping, calculator, file I/O).
- `planner.py`: State manager for the agent's plan (goals, tasks, logs) and the planner tools (`initialize_plan`, `update_plan_status`).
- `requirements.txt`: Python package requirements.

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.8+ (your environment has Python 3.13.0)

### 1. Set Workspace & Install Dependencies
Navigate to the project directory and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
Start the Streamlit application:
```bash
streamlit run app.py
```

### 3. Provide API Key
Input your API key in the sidebar of the web app (or set it in your environment as `OPENAI_API_KEY` or `GEMINI_API_KEY`).

---

## 💡 Quick Start Scenarios to Try

- **Stock Analysis**: *"Find the current stock price of Apple (AAPL). Then, calculate its P/E ratio assuming its EPS is 6.58. Write a markdown report called apple_pe_report.md containing all these calculations and details."*
- **Latest News Summary**: *"Search for the latest news about Google Gemini 2.5 Flash model release. Summarize the key updates and features, and write them to a text file named gemini_news_summary.txt."*
- **Geometry Calculator**: *"Calculate the hypotenuse of a right-angled triangle with sides 24.5 and 18.2. Also calculate its area. Save the output results to geometry_results.txt."*
