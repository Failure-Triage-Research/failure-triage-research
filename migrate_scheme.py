import os
import json
import shutil

TASKS_DIR = "tasks/"
BACKUP_DIR = "tasks_backup/"

def execute_migration():
    print("===================================================")
    print("🛠️  AGENT-RX SCHEMA MIGRATION UTILITY")
    print("===================================================")

    if not os.path.exists(TASKS_DIR):
        print(f"[!] '{TASKS_DIR}' not found. Aborting.")
        return

    # 1. Create a safe backup before touching anything
    if not os.path.exists(BACKUP_DIR):
        shutil.copytree(TASKS_DIR, BACKUP_DIR)
        print(f"[*] Created safe backup of all files in '{BACKUP_DIR}'")
    else:
        print(f"[*] Backup directory '{BACKUP_DIR}' already exists. Skipping backup creation.")

    task_files = [f for f in os.listdir(TASKS_DIR) if f.endswith('.json')]
    migrated_count = 0
    skipped_count = 0

    for filename in task_files:
        filepath = os.path.join(TASKS_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's already using the new schema
            if "evaluation_loop" in data:
                skipped_count += 1
                continue

            # --- MAPPING LOGIC (Old Flat Schema -> New Nested Schema) ---
            new_schema = {
                "task_metadata": {
                    "task_id": data.get("task_id", filename.replace('.json', '')),
                    "domain": data.get("domain", "Unknown"),
                    "failure_category": data.get("failure_type", "Unknown"),
                    # Defaulting target recovery based on your project rules
                    "target_recovery": "escalate_to_human" if data.get("failure_type") in ["ambiguous_task", "irreversible"] else "fix_and_retry"
                },
                "environment_setup": {
                    "filesystem_state": "Standard environment setup. (Requires manual review)",
                    "available_tools": ["execute_bash"]
                },
                "evaluation_loop": {
                    "condition": data.get("task_description", ""),
                    "injected_failure_state": {
                        "tool": "execute_bash",
                        "payload": data.get("current_action", ""),
                        "observation": data.get("error_message", "")
                    },
                    "success_criteria": "Agent correctly resolves the failure. (Requires manual review)"
                }
            }

            # Overwrite the file with the new formatted schema
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(new_schema, f, indent=2)
            
            migrated_count += 1
            print(f"  [+] Migrated: {filename}")

        except Exception as e:
            print(f"  [X] Failed to migrate {filename}: {e}")

    print("===================================================")
    print(f"✅ MIGRATION COMPLETE: {migrated_count} files updated | {skipped_count} files already correct.")
    print("===================================================")

if __name__ == "__main__":
    execute_migration()