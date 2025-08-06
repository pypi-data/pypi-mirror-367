#!/usr/bin/env python3
"""
PromptLifter - Main application entry point.

A LangGraph-powered context extender that orchestrates OpenAI, Tavily, and
Pinecone to produce structured, expert-level answers from complex queries.
"""

import argparse
import asyncio
import json
import sys
from typing import Any, Dict

from .graph import build_graph
from .logging_config import setup_logging


def validate_configuration() -> None:
    """Validate that all required configuration is present."""
    from .config import (
        ANTHROPIC_API_KEY,
        CUSTOM_LLM_ENDPOINT,
        CUSTOM_LLM_MODEL,
        GOOGLE_API_KEY,
        OPENAI_API_KEY,
        PINECONE_API_KEY,
        PINECONE_INDEX,
        TAVILY_API_KEY,
        validate_config,
    )

    missing_vars = []

    # Validate configuration
    config_errors = validate_config()
    if config_errors:
        print("❌ Configuration validation failed:")
        for error in config_errors:
            print(f"  - {error}")
        sys.exit(1)

    # Check for at least one LLM provider
    llm_providers = [
        ("Custom LLM", CUSTOM_LLM_ENDPOINT and CUSTOM_LLM_MODEL),
        ("OpenAI", OPENAI_API_KEY),
        ("Anthropic", ANTHROPIC_API_KEY),
        ("Google", GOOGLE_API_KEY),
    ]

    available_providers = [name for name, available in llm_providers if available]

    if not available_providers:
        print("❌ No LLM providers configured!")
        print("Please configure at least one of:")
        print("  - Custom LLM (CUSTOM_LLM_ENDPOINT + CUSTOM_LLM_MODEL)")
        print("  - OpenAI (OPENAI_API_KEY)")
        print("  - Anthropic (ANTHROPIC_API_KEY)")
        print("  - Google (GOOGLE_API_KEY)")
        sys.exit(1)

    print(f"✅ LLM providers available: {', '.join(available_providers)}")

    # Check required search/vector services
    if not PINECONE_API_KEY:
        missing_vars.append("PINECONE_API_KEY")
    if not PINECONE_INDEX:
        missing_vars.append("PINECONE_INDEX")
    if not TAVILY_API_KEY:
        missing_vars.append("TAVILY_API_KEY")

    if missing_vars:
        print("⚠️  Missing optional environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("Some features may not work without these.")

        # Special note about Pinecone
        if "PINECONE_API_KEY" in missing_vars or "PINECONE_INDEX" in missing_vars:
            print(
                "\n💡 Note: Pinecone is optional. The system will work without it, "
                "but won't have access to internal knowledge base."
            )
            print(
                "   To enable Pinecone: Set PINECONE_API_KEY and PINECONE_INDEX "
                "in your .env file"
            )


def save_result_to_file(
    result: Dict[str, Any], filename: str = "promptlifter_result.json"
) -> None:
    """Save the workflow result to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Result saved to {filename}")
    except Exception as e:
        print(f"Error saving result to file: {e}")


def print_result_summary(result: Dict[str, Any]) -> None:
    """Print a summary of the workflow result."""
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("\n" + "=" * 60)
    print("📊 PROMPTLIFTER SUMMARY")
    print("=" * 60)

    original_query = result.get("original_query", "Unknown query")
    print(f"🔍 Original Query: {original_query}")

    subtask_count = result.get("subtask_count", 0)
    print(f"📋 Subtasks Processed: {subtask_count}")

    final_output = result.get("final_output")
    if final_output:
        print("📝 Final Response Generated: ✅")

        # Show preview of the response
        lines = final_output.split("\n")
        preview_lines = lines[:10]  # Show first 10 lines
        preview = "\n".join(preview_lines)

        print("\n📄 Content Preview:")
        print(preview)

        if len(lines) > 10:
            print("...")
    else:
        print("📝 Final Response Generated: ❌")

    print("=" * 60)


def interactive_mode() -> None:
    """Run the application in interactive mode."""
    print("🚀 PromptLifter Interactive Mode")
    print("Type 'quit', 'exit', or 'q' to exit")

    # Build the graph
    graph = build_graph()

    while True:
        try:
            query = input("\n🔍 Query: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not query:
                print("Please enter a valid query.")
                continue

            print(f"\n🚀 Processing query: {query}")

            # Run the workflow
            state = {"input": query}
            result = asyncio.run(graph.ainvoke(state))

            print_result_summary(result)

            # Ask if user wants to save the result
            save_choice = input("\n💾 Save result to file? (y/n): ").strip().lower()
            if save_choice in ["y", "yes"]:
                filename = input(
                    "📁 Filename (default: promptlifter_result.json): "
                ).strip()
                if not filename:
                    filename = "promptlifter_result.json"
                save_result_to_file(result, filename)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main() -> None:
    """Main application entry point."""
    # Setup logging
    setup_logging(level="INFO")
    # logger = get_logger(__name__)  # Unused for now

    parser = argparse.ArgumentParser(
        description="PromptLifter - LangGraph-powered research assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            """
Examples:
  python main.py --query "Research quantum computing trends"
  python main.py --interactive
  python main.py --query "AI in healthcare" --save result.json
            """
        ),
    )

    parser.add_argument("--query", "-q", type=str, help="Research query to process")

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument("--save", "-s", type=str, help="Save result to specified file")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate configuration
    validate_configuration()

    if args.interactive:
        interactive_mode()
    elif args.query:
        print(f"🚀 Processing query: {args.query}")

        # Build and run the graph
        graph = build_graph()
        state = {"input": args.query}
        result = asyncio.run(graph.ainvoke(state))

        print_result_summary(result)

        if args.save:
            save_result_to_file(result, args.save)
        elif args.verbose:
            print("\n📄 Full Result:")
            print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
