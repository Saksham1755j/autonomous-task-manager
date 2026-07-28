import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import get_all_tools
from planner import get_planner_tools, set_active_planner, AgentPlanner

def initialize_llm(provider: str, model_name: str, api_key: str, temperature: float):
    """Initialize the appropriate Chat LLM wrapper based on the provider."""
    if provider == "OpenAI":
        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=temperature,
            streaming=True
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            streaming=True
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def execute_agent_task(
    provider: str,
    model_name: str,
    api_key: str,
    temperature: float,
    goal: str,
    planner: AgentPlanner,
    ui_callback=None
):
    """Configures and runs the Custom Agent Loop to execute the user's goal.
    This replaces AgentExecutor to prevent import/compatibility errors in custom environments.
    """
    # Set this planner as the active planner for tools to modify
    set_active_planner(planner)
    planner.set_goal(goal)
    
    # Gather tools
    tools = get_all_tools() + get_planner_tools()
    tool_map = {t.name: t for t in tools}
    
    # Initialize LLM
    try:
        llm = initialize_llm(provider, model_name, api_key, temperature)
        llm_with_tools = llm.bind_tools(tools)
    except Exception as e:
        planner.add_log("error", f"LLM Initialization Failed: {str(e)}")
        if ui_callback:
            ui_callback()
        return f"Initialization error: {str(e)}"
    
    # Set up prompt instruction
    system_instruction = """You are an Autonomous Task Planner Agent. Your mission is to systematically achieve the user's goal.
    
    Follow this strict protocol:
    1. FIRST STEP: You MUST initialize the plan using the `initialize_plan` tool. Provide a list of clear, distinct subtasks (actions) that are required to achieve the overall goal. Do not skip this step!
    2. STEP-BY-STEP EXECUTION: For each subtask:
       a. Mark the subtask as 'in_progress' using the `update_plan_status` tool before executing it.
       b. Use the appropriate tools (web_search, web_scrape, calculator, file_write, file_read) to perform the task.
       c. Mark the subtask as 'completed' (or 'failed') using the `update_plan_status` tool once done. Include a brief summary of the result in the tool call.
    3. Keep files written relative (e.g. 'output_report.md'). Avoid writing files outside of the local directory.
    4. When all tasks are completed, present a final report detailing what was achieved and the list of output files.
    """
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=goal)
    ]
    
    planner.add_log("system", "Starting agent execution loop...")
    if ui_callback:
        ui_callback()
        
    max_iterations = 15
    for iteration in range(max_iterations):
        try:
            # Call LLM
            response = llm_with_tools.invoke(messages)
            
            # Record reasoning/thought if non-empty
            if response.content:
                planner.add_log("thought", response.content)
                if ui_callback:
                    ui_callback()
            
            # Append AIMessage
            messages.append(response)
            
            # Check for tool calls
            tool_calls = getattr(response, "tool_calls", [])
            if not tool_calls:
                # Agent completed work, return response
                planner.add_log("system", "Agent execution successfully completed.")
                if ui_callback:
                    ui_callback()
                return response.content
            
            # Execute tool calls
            for tool_call in tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]
                call_id = tool_call["id"]
                
                planner.add_log("tool_call", f"Calling tool **{name}** with inputs: `{args}`")
                if ui_callback:
                    ui_callback()
                
                # Fetch tool
                tool = tool_map.get(name)
                if not tool:
                    output = f"Error: Tool '{name}' is not recognized."
                    planner.add_log("error", output)
                else:
                    try:
                        # Invoke tool
                        output = tool.invoke(args)
                        planner.add_log("tool_response", f"{output}")
                    except Exception as te:
                        output = f"Error executing tool '{name}': {str(te)}"
                        planner.add_log("error", output)
                
                # Append ToolMessage to scratchpad
                messages.append(ToolMessage(content=str(output), tool_call_id=call_id))
                if ui_callback:
                    ui_callback()
                    
        except Exception as e:
            planner.add_log("error", f"Execution error: {str(e)}")
            if ui_callback:
                ui_callback()
            return f"An error occurred: {str(e)}"
            
    planner.add_log("system", "Max iterations reached. Aborting.")
    if ui_callback:
        ui_callback()
    return "Error: Agent reached maximum iteration limit before completing."
