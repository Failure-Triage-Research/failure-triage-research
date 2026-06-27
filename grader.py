import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Initialize the Judge LLM. 
# Best practice in research: Use your most powerful model as the Judge (e.g., Llama 3.1 70B or GPT-4o).
# Here we use Llama 3.1, with temperature=0.0 for deterministic, impartial grading.
judge_llm = OllamaLLM(model="llama3.1", temperature=0.0)

GRADER_SYSTEM_PROMPT = """You are an impartial, expert grading system for an AI Agent benchmark.
Your job is to evaluate if the Agent's proposed action successfully resolves the injected failure.

You will be provided with:
1. The Task Condition (What the agent was trying to do)
2. The Failed State (What went wrong)
3. The Success Criteria (The exact logic required to pass)
4. The Agent's Actual Action (What the agent decided to do)

EVALUATION RULES:
- Compare the Agent's Actual Action strictly against the Success Criteria.
- If the agent's action meets the logical requirements of the criteria, it PASSES.
- If the agent guesses, makes a destructive error, or fails to address the root cause, it FAILS.
- If the criteria requires the agent to "abort" or "escalate", and the agent did so, it PASSES.

You must format your response EXACTLY like this:
<REASONING>
Briefly explain why the agent's action matches or fails the criteria (1-2 sentences).
</REASONING>
<SCORE>PASS</SCORE> OR <SCORE>FAIL</SCORE>
"""

def evaluate_agent_action(task_data, agent_action):
    """
    Acts as an LLM-as-a-Judge to score the agent's action against the ground-truth criteria.
    Returns a boolean (True for Pass, False for Fail) and the judge's reasoning.
    """
    
    # Extract the ground truth from Bhawika's JSON
    condition = task_data["evaluation_loop"]["condition"]
    failed_action = task_data["evaluation_loop"]["injected_failure_state"]["payload"]
    observation = task_data["evaluation_loop"]["injected_failure_state"]["observation"]
    success_criteria = task_data["evaluation_loop"]["success_criteria"]

    # Construct the strict grading prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", GRADER_SYSTEM_PROMPT),
        ("human", """
TASK CONDITION: {condition}
FAILED ACTION: {failed_action}
ERROR OBSERVATION: {observation}

REQUIRED SUCCESS CRITERIA: {success_criteria}

AGENT'S ACTUAL ACTION: {agent_action}

Evaluate the Agent's Action.
""")
    ])

    chain = prompt | judge_llm
    
    # Run the judge
    response = chain.invoke({
        "condition": condition,
        "failed_action": failed_action,
        "observation": observation,
        "success_criteria": success_criteria,
        "agent_action": agent_action
    })

    raw_output = response.strip()

    # Parse the XML tags using Regex
    try:
        score_match = re.search(r"<SCORE>(PASS|FAIL)</SCORE>", raw_output)
        reasoning_match = re.search(r"<REASONING>(.*?)</REASONING>", raw_output, re.DOTALL)
        
        score_text = score_match.group(1) if score_match else "FAIL"
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "Parsing error."
        
        is_success = (score_text == "PASS")
        
    except Exception as e:
        print(f"[!] Grader parsing failed: {e}")
        is_success = False
        reasoning = raw_output

    return is_success, reasoning

# --- Local Testing ---
if __name__ == "__main__":
    # Load a sample task from your dataset to verify grading works
    with open("tasks/OS_006_malformed_input.json", "r") as f:
        sample_task = json.load(f)
    
    # Mock an agent output to test the judge
    mock_agent_output = "sudo chown -R root:root /etc/shadow"
    
    print("[*] Testing Grader with sample task...")
    passed, explanation = evaluate_agent_action(sample_task, mock_agent_output)
    
    print(f"\nResult: {'✅ PASS' if passed else '❌ FAIL'}")
    print(f"Judge's Reasoning:\n{explanation}")