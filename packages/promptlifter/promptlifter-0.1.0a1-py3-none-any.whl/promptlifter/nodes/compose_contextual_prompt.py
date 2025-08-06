def compose_prompt(task: str, tavily_data: str, pinecone_data: str) -> str:
    """Compose a contextual prompt combining search results."""

    # Build the prompt with available data
    prompt_parts = [f"Research Task: {task}\n\n"]

    # Add web search results if available
    if (
        tavily_data
        and not tavily_data.startswith("[Error:")
        and not tavily_data.startswith("[Info:")
    ):
        prompt_parts.append("Web Search Results:")
        prompt_parts.append(tavily_data)
        prompt_parts.append("\n")

    # Add knowledge base results if available
    if (
        pinecone_data
        and not pinecone_data.startswith("[Error:")
        and not pinecone_data.startswith("[Info:")
    ):
        prompt_parts.append("Knowledge Base Results:")
        prompt_parts.append(pinecone_data)
        prompt_parts.append("\n")

    # Add instruction
    prompt_parts.append(
        "Based on the above information, provide a comprehensive and "
        "well-structured answer to the research task. "
        "Include relevant details, cite sources when possible, and "
        "organize your response clearly."
    )

    return "\n".join(prompt_parts)
