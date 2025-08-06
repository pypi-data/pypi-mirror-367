from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from .nodes.gather_and_compile import gather_and_compile
from .nodes.split_input import split_input
from .nodes.subtask_handler import handle_subtasks


class GraphState(TypedDict):
    input: str
    subtasks: List[str]
    original_query: str
    subtask_results: List[Dict[str, Any]]
    final_output: str
    subtask_count: int
    error: Optional[str]  # Add error field for handling validation failures


def build_graph() -> Any:
    """Build the LangGraph workflow."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("split_input", split_input)  # type: ignore
    workflow.add_node("subtask_handler", handle_subtasks)  # type: ignore
    workflow.add_node("gather_and_compile", gather_and_compile)  # type: ignore

    # Set entry point
    workflow.set_entry_point("split_input")

    # Add edges
    workflow.add_edge("split_input", "subtask_handler")
    workflow.add_edge("subtask_handler", "gather_and_compile")
    workflow.add_edge("gather_and_compile", END)

    return workflow.compile()
