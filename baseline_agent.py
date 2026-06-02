from typing import TypedDict, List, Optional, Dict

class ToolResult(TypedDict):
    tool_name: str
    input: str
    output: Optional[str]
    error : Optional[str]
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