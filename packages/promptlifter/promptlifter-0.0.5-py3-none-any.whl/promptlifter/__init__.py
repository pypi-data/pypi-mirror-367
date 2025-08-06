"""
PromptLifter - LLM-powered contextual expansion using LangGraph.

A research assistant that orchestrates LLM-powered contextual expansion
to produce structured, expert-level answers from complex queries.
"""

__version__ = "0.1.0a1"
__author__ = "PromptLifter Team"
__description__ = "LLM-powered contextual expansion using LangGraph"

from .config import validate_config
from .graph import build_graph

__all__ = [
    "build_graph",
    "validate_config",
    "__version__",
    "__author__",
    "__description__",
]
