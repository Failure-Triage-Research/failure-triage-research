from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# 1. THE STATE SCHEMA (TypedDict)
class AgentState(TypedDict):
    task_description: str
    current_action: str
    error_message: Optional[str]
    task_success: bool
    triage_loops: int
    recovery_strategy: str
    max_retries: int


# Connect to local Ollama Llama 3.1 8B
local_llm = OllamaLLM(model="llama3.1")


# 2. THE EXECUTOR NODE
def executor(state: AgentState):
    print(f"\n[Executor] Attempting action: {state['current_action']}")
    
    action = state.get("current_action", "")
    loops = state.get("triage_loops", 0)
    
    # Simulating permission failure on the first attempt if sudo is not present
    if "sudo" not in action and loops == 0:
        print("[Executor] SYSTEM ERROR: Permission Denied.")
        return {
            "error_message": "AuthError: Missing sudo privileges",
            "task_success": False
        }
        
    print("[Executor] Action Successful!")
    return {
        "error_message": None,
        "task_success": True
    }


# 3. THE TRIAGE NODE
def triage(state: AgentState):
    print(f"\n[Triage] Analyzing error: {state['error_message']}")

    # Prompting the local LLM to act as the Triage Module
    prompt_template = PromptTemplate(
        template="""You are a Triage AI for an Operating System Agent.
The agent attempted: {action}
And received this error: {error}

Provide a fixed bash command to resolve this issue (e.g. by adding sudo or fixing parameters).
Output ONLY the exact fixed command, no markdown, no explanation, no backticks.""",
        input_variables=["action", "error"]
    )

    prompt = prompt_template.format(action=state['current_action'], error=state['error_message'])

    try:
        fixed_action = local_llm.invoke(prompt).strip()
    except Exception as e:
        print(f"[Triage] LLM invocation failed: {e}. Falling back to prepending sudo.")
        fixed_action = f"sudo {state['current_action']}"

    print(f"[Triage] Suggested Fix: {fixed_action}")

    # Set recovery strategy dynamically
    recovery_strategy = "sudo_fallback" if "sudo" in fixed_action else "generic_fix"

    return {
        "current_action": fixed_action,
        "recovery_strategy": recovery_strategy,
        "triage_loops": state.get("triage_loops", 0) + 1,
        "error_message": None
    }


# 4. CONDITIONAL ROUTERS
def route_after_execution(state: AgentState):
    if state.get("task_success", False):
        return "end"
    return "triage"


def should_continue(state: AgentState):
    if state.get("triage_loops", 0) < state.get("max_retries", 3):
        return "executor"
    return "end"


# --- BUILDING THE GRAPH ---
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("executor", executor)
workflow.add_node("triage", triage)

# Set entry point
workflow.set_entry_point("executor")

# Add edges/routers
workflow.add_conditional_edges(
    "executor",
    route_after_execution,
    {
        "triage": "triage",
        "end": END
    }
)

workflow.add_conditional_edges(
    "triage",
    should_continue,
    {
        "executor": "executor",
        "end": END
    }
)

# Compile graph
agent_rx_app = workflow.compile()

# Compatibility alias for external loggers
app = agent_rx_app


# --- RUNNING THE TEST ---
if __name__ == "__main__":
    initial_state = {
        "task_description": "Create a new user.",
        "current_action": "add_user 'guest'",
        "error_message": None,
        "task_success": False,
        "triage_loops": 0,
        "recovery_strategy": "none",
        "max_retries": 3
    }

    print("[*] Running local agent test...")
    final_state = agent_rx_app.invoke(initial_state)
    print(f"[*] Test complete. Success: {final_state.get('task_success')}, Loops: {final_state.get('triage_loops')}")