from .llm_service import llm_service


async def run_llm(task: str, prompt: str) -> str:
    """Run the LLM to generate responses for individual subtasks."""
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Provide comprehensive, "
                    "well-structured answers based on the provided information. "
                    "Be thorough and cite sources when possible."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response = await llm_service.generate(messages, max_tokens=1000)
        return response

    except Exception as e:
        return f"[LLM processing error: {str(e)}]"
