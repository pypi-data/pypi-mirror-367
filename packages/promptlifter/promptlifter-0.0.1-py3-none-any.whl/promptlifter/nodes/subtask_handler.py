import asyncio
import logging
from typing import Any, Dict

from .compose_contextual_prompt import compose_prompt
from .run_pinecone_search import run_pinecone_search
from .run_subtask_llm import run_llm
from .run_tavily_search import run_tavily_search

# Set up logging
logger = logging.getLogger(__name__)


async def process_subtask(task: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single subtask with parallel search and LLM generation."""
    try:
        logger.info(f"Processing subtask: {task[:50]}...")

        # Run searches in parallel with timeout
        tavily_task = run_tavily_search(task)
        pinecone_task = asyncio.wait_for(
            run_pinecone_search(task), timeout=30.0  # Now async  # 30 second timeout
        )

        # Wait for both searches to complete
        tavily_data, pinecone_data = await asyncio.gather(
            tavily_task, pinecone_task, return_exceptions=True
        )

        # Handle exceptions from parallel tasks
        if isinstance(tavily_data, Exception):
            logger.error(f"Tavily search exception: {str(tavily_data)}")
            tavily_data = f"[Tavily search error: {str(tavily_data)}]"
        if isinstance(pinecone_data, Exception):
            logger.error(f"Pinecone search exception: {str(pinecone_data)}")
            pinecone_data = f"[Pinecone search error: {str(pinecone_data)}]"

        # Log search results
        logger.info("Tavily result: {}...".format(str(tavily_data)[:100]))
        logger.info("Pinecone result: {}...".format(str(pinecone_data)[:100]))

        # Check if both searches failed
        both_failed = str(tavily_data).startswith("[Error:") and str(
            pinecone_data
        ).startswith("[Error:")

        if both_failed:
            logger.warning(
                "Both search services failed - proceeding with limited context"
            )

        # Compose contextual prompt
        prompt = compose_prompt(task, str(tavily_data), str(pinecone_data))

        # Run LLM processing with timeout
        logger.info("Running LLM processing...")
        result = await asyncio.wait_for(
            run_llm(task, prompt), timeout=60.0  # 60 second timeout for LLM
        )

        return {
            "task": task,
            "result": result,
            "tavily_data": tavily_data,
            "pinecone_data": pinecone_data,
        }

    except asyncio.TimeoutError:
        logger.error(f"Request timed out for task: {task}")
        return {
            "task": task,
            "result": "[Error: Request timed out]",
            "tavily_data": "",
            "pinecone_data": "",
        }
    except Exception as e:
        logger.error(f"Error processing subtask '{task}': {str(e)}")
        return {
            "task": task,
            "result": f"[Error processing subtask: {str(e)}]",
            "tavily_data": "",
            "pinecone_data": "",
        }


async def handle_subtasks(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle all subtasks in parallel."""
    tasks = state["subtasks"]
    logger.info(f"Processing {len(tasks)} subtasks in parallel")

    # Process all subtasks in parallel
    results = await asyncio.gather(
        *[process_subtask(task, state) for task in tasks], return_exceptions=True
    )

    # Handle any exceptions from subtask processing
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Subtask {i} failed with exception: {str(result)}")
            processed_results.append(
                {
                    "task": tasks[i] if i < len(tasks) else "Unknown",
                    "result": f"[Error: {str(result)}]",
                    "tavily_data": "",
                    "pinecone_data": "",
                }
            )
        else:
            # Ensure result is a dict
            if isinstance(result, dict):
                processed_results.append(result)
            else:
                logger.error(f"Unexpected result type: {type(result)}")
                processed_results.append(
                    {
                        "task": tasks[i] if i < len(tasks) else "Unknown",
                        "result": f"[Error: Unexpected result type: {type(result)}]",
                        "tavily_data": "",
                        "pinecone_data": "",
                    }
                )

    # Log summary
    successful_tasks = sum(
        1 for r in processed_results if not r["result"].startswith("[Error:")
    )
    logger.info(
        f"Completed {len(processed_results)} subtasks: {successful_tasks} successful"
    )

    return {**state, "subtask_results": processed_results}
