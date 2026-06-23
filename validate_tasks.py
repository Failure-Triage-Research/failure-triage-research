import os
import json

# --- CONFIGURATION ---
TASKS_DIR = "tasks/"

# The exact nested schema required for your NeurIPS/ICML benchmark
REQUIRED_ROOT_KEYS = {"task_metadata", "environment_setup", "evaluation_loop"}
REQUIRED_METADATA_KEYS = {"task_id", "domain", "failure_category", "target_recovery"}
REQUIRED_ENV_KEYS = {"filesystem_state", "available_tools"}
REQUIRED_EVAL_KEYS = {"condition", "injected_failure_state", "success_criteria"}
REQUIRED_INJECTED_KEYS = {"tool", "payload", "observation"}

def execute_validation():
    print("===================================================")
    print("🔍 AGENT-RX TASK VALIDATOR INITIATED")
    print("===================================================")
    
    if not os.path.exists(TASKS_DIR):
        print(f"[!] Directory '{TASKS_DIR}' not found. Aborting.")
        return

    # Find all JSON files in the tasks directory
    task_files = sorted([f for f in os.listdir(TASKS_DIR) if f.endswith('.json')])
    
    if not task_files:
        print("[!] No JSON files found in the 'tasks/' directory.")
        return

    print(f"[*] Found {len(task_files)} task files. Beginning strict schema validation...\n")

    valid_count = 0
    error_count = 0

    for filename in task_files:
        filepath = os.path.join(TASKS_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. Check Root-Level Keys
            if not REQUIRED_ROOT_KEYS.issubset(data.keys()):
                missing = REQUIRED_ROOT_KEYS - data.keys()
                raise ValueError(f"Missing root keys: {missing}")
            
            # 2. Check 'task_metadata' Keys
            if not REQUIRED_METADATA_KEYS.issubset(data["task_metadata"].keys()):
                missing = REQUIRED_METADATA_KEYS - data["task_metadata"].keys()
                raise ValueError(f"Missing in task_metadata: {missing}")

            # 3. Check 'environment_setup' Keys
            if not REQUIRED_ENV_KEYS.issubset(data["environment_setup"].keys()):
                missing = REQUIRED_ENV_KEYS - data["environment_setup"].keys()
                raise ValueError(f"Missing in environment_setup: {missing}")

            # 4. Check 'evaluation_loop' Keys
            if not REQUIRED_EVAL_KEYS.issubset(data["evaluation_loop"].keys()):
                missing = REQUIRED_EVAL_KEYS - data["evaluation_loop"].keys()
                raise ValueError(f"Missing in evaluation_loop: {missing}")

            # 5. Check 'injected_failure_state' Keys
            injected_state = data["evaluation_loop"]["injected_failure_state"]
            if not REQUIRED_INJECTED_KEYS.issubset(injected_state.keys()):
                missing = REQUIRED_INJECTED_KEYS - injected_state.keys()
                raise ValueError(f"Missing in injected_failure_state: {missing}")

            valid_count += 1

        except json.JSONDecodeError as e:
            # Catches syntax errors like missing commas or unescaped quotes
            print(f"  [X] {filename} | SYNTAX ERROR: {e}")
            error_count += 1
        except ValueError as e:
            # Catches structural errors (missing fields from our required sets)
            print(f"  [X] {filename} | SCHEMA ERROR: {e}")
            error_count += 1
        except Exception as e:
            print(f"  [X] {filename} | UNEXPECTED CRASH: {e}")
            error_count += 1

    # --- SUMMARY REPORT ---
    print("\n===================================================")
    print(f"📊 VALIDATION COMPLETE: {valid_count} Valid | {error_count} Errors")
    print("===================================================")
    
    if error_count == 0:
        print("✅ ALL TASKS PASSED! The dataset is structurally flawless.")
    else:
        print("⚠️ PLEASE FIX THE ERRORS ABOVE BEFORE RUNNING THE DATA BRIDGE.")

if __name__ == "__main__":
    execute_validation()