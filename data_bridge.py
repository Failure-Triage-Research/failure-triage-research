import os
import json
import csv
import time
from datetime import datetime

# Import your compiled LangGraph applications
# (Adjust these import names based on what you named them in your actual files)
from baseline_agent import app as baseline_app
from triage_agent import app as triage_app

# --- DIRECTORY SETUP ---
TASKS_DIR = "tasks/"
RESULTS_DIR = "results/"
MASTER_LOG_FILE = os.path.join(RESULTS_DIR, f"agent_rx_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

# Ensure directories exist
os.makedirs(TASKS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def initialize_logger():
    """Creates the master CSV file and writes the research header columns."""
    with open(MASTER_LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        # These columns map exactly to your Research sub-questions
        writer.writerow([
            "Task_Id",
            "Domain",
            "Failure_Type",
            "Baseline_Success",
            "Triage_Success",
            "Triage_Loops_Taken",
            "Recovery_Strategy",
            "Baseline_Time_Sec",
            "Triage_Time_Sec",       
        ])
    print(f"[*] Logger Initialized: {MASTER_LOG_FILE}")

def run_agent(app, agent_state, agent_name):
    """Executes a LangGraph app and calculates execution time."""
    print(f"      -> Running {agent_name}...")
    start_time = time.time()

    try: 
        # Inject the state dictionary into the LangGraph engine
        final_state = app.invoke(agent_state)
        success = final_state.get("task_success", False)
        loops = final_state.get("triage_loops", 0)
        strategy = final_state.get("recovery_strategy", "none")
    except Exception as e:
        print(f"    [!] {agent_name} crashed: {e}")
        success = False
        loops = 0
        strategy = "crash"

    execution_time = round(time.time() - start_time, 2)
    return success, loops, strategy, execution_time

def execute_data_bridge():
    """The main automated ingestion loop."""
    print("======================================================================")
    print("Agent-Rx Evaluation Pipeline Initiated")
    print("======================================================================")

    initialize_logger()

    # 1. Scan the directory for Bhawika's JSON Files
    task_files = sorted([f for f in os.listdir(TASKS_DIR) if f.endswith('.json')])
    
    if not task_files:
        print("[!] No JSON tasks found in the 'tasks/' directory. Aborting.")
        return

    print(f"[*] Found {len(task_files)} tasks. Beginning evaluation loop...\n")
    
    # 4 spaces indentation
    with open(MASTER_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # 8 spaces indentation
        for filename in task_files:
            file_path = os.path.join(TASKS_DIR, filename)
            print(f"[*] Processing Task: {filename}")
            
            with open(file_path, 'r') as json_file:
                task_data = json.load(json_file)
    
            # Map JSON data to your LangGraph State Format
            agent_state = {
                "task_description": task_data.get("task_description", ""),
                "current_action": task_data.get("current_action", ""),
                "error_message": task_data.get("error_message", ""),
                "task_success": False,
                "triage_loops": 0,
                "recovery_strategy": "none",
                # The kill-switch guardrail ensures it doesn't loop forever
                "max_retries": 3
            }

            # 3. The Dual Run (Baseline vs Agent-Rx)
            b_success, _, _, b_time = run_agent(baseline_app, agent_state, "Baseline Agent")
            t_success, t_loops, t_strategy, t_time = run_agent(triage_app, agent_state, "Triage Agent")

            triage_action = agent_state.get("current_action") 

            # We pass that action to the grader to get an impartial PASS/FAIL
            from grader import evaluate_agent_action
            passed, reasoning = evaluate_agent_action(task_data, triage_action)

            print(f"    [Judge Grader] Result: {'PASS' if passed else 'FAIL'} | Reason: {reasoning}")

            # 4. Log the Metrics (WRITTEN ONLY ONCE)
            writer.writerow([
                task_data.get("task_id", "unknown"),
                task_data.get("domain", "unknown"),
                task_data.get("failure_type", "unknown"),
                b_success,
                passed,          # Impartial score from the LLM Judge
                t_loops,
                t_strategy,
                b_time,
                t_time
            ])
            
            print(f"        [+] Logged | Baseline: {'PASS' if b_success else 'FAIL'} | Judge Grader: {'PASS' if passed else 'FAIL'} ({t_strategy})\n")

            time.sleep(1)

    print("===============================================================")
    print("Evaluation Pipeline Complete.")
    print(f"[*] Results saved to: {MASTER_LOG_FILE}")
    print("===============================================================")


if __name__ == "__main__":
    execute_data_bridge()