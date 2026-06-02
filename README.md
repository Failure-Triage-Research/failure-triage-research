# Failure-Aware Self-Triage in LLM Agents (Agent-Rx)

This repository contains the codebase and benchmark suite for the research project **"Failure-Aware Self-Triage in LLM Agents (Agent-Rx)"**, focused on building and evaluating agents that can diagnose their own tool execution failures and select optimal recovery strategies.

Research conducted by **Rohit & Bhawika** at **Sister Nivedita University, Kolkata**.
Targeting submission to the **NeurIPS / ICML 2027 Workshop**.

---

## 🎯 Research Overview

### Primary Research Question
> *"Can an AI agent learn to recognise what kind of mistake it just made, and use that to decide the smartest next move—stop, retry, self-fix, or ask for help?"*

### Sub-Questions
1. **SQ1 (Agent Memory):** Do AI agents become better when they remember what went wrong in past tasks?
2. **SQ2 (Local vs. Cloud Models):** Can a small local model (LLaMA 3.1 8B) act as effectively as GPT-4o-mini as an agent when equipped with a dedicated triage and recovery module?

---

## 🏗️ System Architecture

This project compares two agent paradigms implemented using **LangGraph**:

1. **Baseline Agent (`baseline_agent.py`):** Operates on a standard ReAct (Reasoning + Acting) loop. If a tool fails, it increments a dumb retry counter and retries blindly up to 3 times before failing the task.
2. **Triage Agent (`triage_agent.py` + `failure_triage.py`):** Integrates an active **Triage Node**. When a tool fails, it invokes LLaMA 3.1 8B with a chain-of-thought prompt to classify the failure type and select a corresponding recovery strategy.

```
[plan] ──> [execute] ──> [TRIAGE] ──> [decide]
                            │
              (classifies failure & selects
                optimal recovery action)
```

---

## 🔍 Taxonomy & Recovery Strategies

The triage module classifies failures into **6 Failure Types** and selects from **5 Recovery Strategies**:

### 1. The 6 Failure Types
| # | Type ID | Description | Example |
|---|---|---|---|
| 1 | `tool_unavailable` | External API is down or service is unreachable. | DuckDuckGo returns `503 Service Unavailable`. |
| 2 | `malformed_input` | Request formatted incorrectly (bad JSON, wrong types). | API expects `{"q": "..."}` but agent sends plain text. |
| 3 | `execution_error` | Tool crashes mid-run or hits a timeout/OOM. | Python code execution node hits 30s timeout on an infinite loop. |
| 4 | `logic_error` | Tool runs successfully, but the output is wrong/irrelevant. | Agent searches for the wrong year's price data. |
| 5 | `irreversible` | Action succeeds but cannot be undone (data deleted, purchase made). | Agent deletes a file it was asked to overwrite. |
| 6 | `ambiguous_task` | Task description is unclear or underspecified. | "Find the best result" (by what metric?). |

### 2. The 5 Recovery Strategies
* **`retry_same_step`**: Wait 2 seconds. Retry with identical inputs (for transient network/service errors).
* **`fix_and_retry`**: Ask the LLM to revise the tool input or parameters, then retry.
* **`backtrack_and_replan`**: Pop the last $N$ steps from the agent state, return to the planning node, and select a new path.
* **`escalate_to_human`**: Pause execution, log `NEEDS_HUMAN`, and flag the task success as `False`.
* **`abort_task`**: Mark the task complete and set success to `False` immediately (preventing damage from repeated failures).

---

## 📊 Benchmark & Dataset

The system is evaluated against **AgentFailBench**, a custom benchmark consisting of **150 human-annotated task JSON files** divided across 6 categories (25 tasks each):
* `web_search` (`web_001` - `web_025`)
* `file_operations` (`file_001` - `file_025`)
* `calculation` (`calc_001` - `calc_025`)
* `code_execution` (`code_001` - `code_025`)
* `api_calls` (`api_001` - `api_025`)
* `multi_step` (`multi_001` - `multi_025`)

---

## ⚙️ Development & Execution Environment

* **Development:** MacBook Pro (M3 Max, 128GB Unified Memory)
* **Execution & Inference:** Windows 11 PC (Ryzen 9 7950X, NVIDIA RTX 4090 Ti 64GB) via WSL2 Ubuntu
* **Local Inference Engine:** Ollama running LLaMA 3.1 8B (`llama3.1:8b`)
* **Libraries:** Python 3.11, LangGraph, LangChain, PyTorch, CUDA
