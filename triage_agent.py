from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# 1. THE STATE
class AgentState(TypedDict):
    task_description: str
    current_action: str
    error_message: Optional[str]
    recovery_plan: Optional[str]
    attempt_count: int


# Connect to your Local Llama 3.1 8B via Ollama
local_llm = Ollama(model="llama3.1:8b")


# 2. THE EXECUTOR NODE
def execute_task(state: AgentState):
    print(f"\n[Executor] Attempting action: {state['current_action']}")

    # Simulating a failure for testing purposes
    if "sudo" not in state['current_action'] and state['attempt_count'] == 0:
        print("[Executor] SYSTEM ERROR: Permission Denied.")
        return {
            "error_message": "AuthError: Missing sudo privileges",
            "attempt_count": state["attempt_count"] + 1
        }
        
    print("[Executor] Action Successful!")
    return {"error_message": None}

# 3. THE TRIAGE NODE (Powered by Llama 3.1)
def triage_error(state: AgentState):
    print(f"\n[Triage] Analyzing error with Llama 3.1: {state['error_message']}")


    #Prompting the local LLM to act as the Triage Module
    prompt_template = PromptTemplate(
        template = """You are a Triage AI for an Operating System Agent.
        The agent attempted: {action}
        And received this error: {error}
        
        Provide a fixed bash command to resolve this issue. Output ONLY the exact fixed command, no markdown.""",
        input_variables = ["action", "error"]
    )

    prompt = prompt_template.format(action = state['current_action'], error = state['error_message'])

    #Call your local hardware model
    fixed_action = local_llm.invoke(prompt).strip()
    print(f"[Triage] Llama 3.1 Suggested Fix: {fixed_action}")

    return {
        "current_action": fixed_action,
        "recovery_plan": "fix_and_retry",
        "error_message": None
    }


# 4. CONDITIONAL ROUTER
def route_after_execution(state: AgentState):
    if state.get("error_message"):
        return "triage"
    return "end"


# --- BUILDING THE GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("executor", execute_task)
workflow.add_node("triage", triage_error)
workflow.set_entry_point("executor")

workflow.add_conditional_edges(
    "executor",
    route_after_execution,
    {
        "triage": "triage",
        "end": END
    }
)
workflow.add_edge("triage", "executor")
agent_rx_app = workflow.compile()

# --- RUNNING THE TEST ---
if __name__ == "__main__":
    initial_memory = {
        "task_description": "Create a new user.",
        "current_action": "add_user 'guest' ",
        "error_message": None,
        "attempt_count": 0
    }

    final_state = agent_rx_app.invoke(initial_memory)