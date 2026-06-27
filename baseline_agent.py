from typing import TypedDict, List, Optional, Dict
from langgraph.graph import StateGraph, END

class ToolResult(TypedDict):
    tool_name: str
    input: str
    output: Optional[str]
    error: Optional[str]
    success: bool
    timestamp: float


class AgentState(TypedDict):
    task_id: str
    task_description: str
    agent_type: str
    steps_taken: List[str]
    tool_calls: List[ToolResult]
    failures: List[ToolResult]
    retry_counts: Dict[str, int]
    is_complete: bool
    task_success: bool


# Define your agent's core logic/node
def baseline_step(state: AgentState):
    print("      [Baseline] Attempting baseline execution...")
    
    # Safely get steps_taken or default to empty list, and append new step
    updated_steps = state.get("steps_taken", []) or []
    updated_steps = updated_steps + ["Attempted baseline execution"]
    
    return {
        "steps_taken": updated_steps,
        "is_complete": True,
        "task_success": True
    }


# Build the simple StateGraph using AgentState
workflow = StateGraph(AgentState)

# Add the node
workflow.add_node("baseline_step", baseline_step)

# Set entry and finish point to the single node
workflow.set_entry_point("baseline_step")
workflow.set_finish_point("baseline_step")

# Compile the workflow into baseline_app
baseline_app = workflow.compile()

# Also alias to app for compatibility with current imports in data_bridge.py
app = baseline_app