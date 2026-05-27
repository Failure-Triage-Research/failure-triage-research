---
name: "🧠 New Benchmark Task (JSON)"
about: "Draft a new task to test the agent's failure recovery."
title: "[TASK] <category> - <short description>"
labels: 'task-draft'
assignees: ''
---

## Step 1: Pick the Category & Domain
*Which of the 6 core categories is this testing?*
- [ ] `web_search`
- [ ] `file_operations`
- [ ] `calculation`
- [ ] `code_execution`
- [ ] `api_calls`
- [ ] `multi_step`

**Domain / Topic:** (e.g., Tech, SNU University, Local Kolkata, Gaming)
> 

---

## Step 2: Pick the Trap (Failure Type)
*Select exactly ONE failure type this task is engineered to trigger:*
- [ ] `tool_unavailable` (API down, network timeout)
- [ ] `malformed_input` (Bad JSON, wrong string format)
- [ ] `execution_error` (Code crash, timeout loop)
- [ ] `logic_error` (Agent searches wrong thing, hallucinated tool)
- [ ] `irreversible` (Dangerous action like delete or buy)
- [ ] `ambiguous_task` (Vague instructions, missing context)

---

## Step 3: Design the Scenario
*Briefly describe the trap. How will we force the agent to fail?*
> 

---

## Step 4: The JSON Draft
*Fill in the green values. Do NOT change the pink keys.*

```json
{
  "task_id": "category_000",
  "category": "",
  "description": "",
  "expected_tools": [],
  "success_criteria": "",
  "expected_failure": "",
  "recovery_hint": "",
  "difficulty": "easy",
  "created_by": "",
  "notes": ""
}
