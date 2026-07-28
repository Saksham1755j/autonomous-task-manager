import time
from langchain.tools import tool

class AgentPlanner:
    def __init__(self):
        self.goal = ""
        self.tasks = []
        self.logs = []
        self.files_created = []

    def set_goal(self, goal: str):
        self.goal = goal
        self.tasks = []
        self.logs = []
        self.files_created = []
        self.add_log("system", f"Initialized plan for goal: {goal}")

    def add_log(self, log_type: str, message: str):
        """Types: 'thought', 'tool_call', 'tool_response', 'system', 'error'"""
        self.logs.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "type": log_type,
            "message": message
        })

    def init_tasks(self, task_descriptions: list):
        self.tasks = []
        for i, desc in enumerate(task_descriptions, start=1):
            self.tasks.append({
                "id": i,
                "description": desc,
                "status": "pending",  # pending, in_progress, completed, failed
                "result": ""
            })
        self.add_log("system", f"Created plan with {len(self.tasks)} subtasks.")

    def update_task(self, task_id: int, status: str, result: str = ""):
        for t in self.tasks:
            if t["id"] == task_id:
                t["status"] = status
                if result:
                    t["result"] = result
                self.add_log("system", f"Subtask {task_id} status updated to: {status.upper()}")
                return f"Task {task_id} status updated to {status} successfully."
        return f"Error: Subtask ID {task_id} not found."

# Singleton or active instance helper
_active_planner = None

def set_active_planner(planner: AgentPlanner):
    global _active_planner
    _active_planner = planner

def get_active_planner() -> AgentPlanner:
    global _active_planner
    return _active_planner

@tool
def initialize_plan(subtasks: list[str]) -> str:
    """Initialize the step-by-step task list (plan) for the goal.
    This MUST be the very first tool called by the agent when starting a new goal.
    Provide a list of clear, distinct subtask descriptions required to achieve the overall goal.
    """
    planner = get_active_planner()
    if not planner:
        return "Error: No active planner instance found."
    planner.init_tasks(subtasks)
    return f"Successfully initialized the plan with {len(subtasks)} subtasks."

@tool
def update_plan_status(task_id: int, status: str, result: str = "") -> str:
    """Update the status and progress of a specific subtask in the plan.
    Supported statuses: 'pending', 'in_progress', 'completed', 'failed'.
    Update a task to 'in_progress' before starting work on it, and to 'completed' or 'failed' when finished.
    Optional: Include a brief 'result' string summarizing what was accomplished in this step.
    """
    planner = get_active_planner()
    if not planner:
        return "Error: No active planner instance found."
    
    # Normalize status to lowercase
    status = status.lower().strip()
    if status not in ['pending', 'in_progress', 'completed', 'failed']:
        return f"Error: Invalid status '{status}'. Must be 'pending', 'in_progress', 'completed', or 'failed'."
        
    try:
        task_id_int = int(task_id)
    except ValueError:
        return f"Error: task_id must be an integer, got '{task_id}'."
        
    return planner.update_task(task_id_int, status, result)

def get_planner_tools():
    return [initialize_plan, update_plan_status]
