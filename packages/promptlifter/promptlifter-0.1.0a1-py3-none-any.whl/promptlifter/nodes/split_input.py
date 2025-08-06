import re
from typing import Any, Dict

from .llm_service import llm_service


def validate_and_sanitize_input(query: str) -> str:
    """Validate and sanitize user input."""
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", query.strip())

    # Limit length to prevent abuse
    if len(sanitized) > 1000:
        raise ValueError("Query too long (max 1000 characters)")

    if len(sanitized) < 3:
        raise ValueError("Query too short (min 3 characters)")

    return sanitized


async def split_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """Split the user query into research subtasks using custom LLM."""
    try:
        query = state["input"]

        # Validate and sanitize input
        query = validate_and_sanitize_input(query)

        messages = [
            {
                "role": "system",
                "content": (
                    "Break this query into 3-5 research subtasks. Each subtask should "
                    "be a specific, focused research question that contributes to "
                    "answering the main query. Return only the subtasks, one per line, "
                    "starting with '- '."
                ),
            },
            {"role": "user", "content": query},
        ]

        response = await llm_service.generate(messages, max_tokens=500)

        subtasks_text = response.strip()
        subtasks = [s.strip("- ") for s in subtasks_text.split("\n") if s.strip()]

        return {
            **state,
            "subtasks": subtasks,
            "original_query": query,
            "subtask_results": [],
            "final_output": "",
            "subtask_count": 0,
        }
    except Exception as e:
        return {
            **state,
            "error": f"Input validation failed: {str(e)}",
            "subtasks": [],
            "subtask_results": [],
            "final_output": "",
            "subtask_count": 0,
        }
