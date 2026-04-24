"""
Agent orchestrator: coordinates the planner → generator pipeline.

This module provides the main entry point for converting natural language
prompts into IFC files.
"""

from pathlib import Path

from agent.generator import generate_ifc, generate_ifc_summary
from agent.planner import parse_prompt
from models.schema import HousePlan


def run_agent(prompt: str, output: str | Path | None = None) -> tuple[str, str]:
    """Convert a natural language prompt into an IFC file.

    Pipeline:
        1. Planner: prompt → HousePlan (structured data)
        2. Generator: HousePlan → IFC file

    Args:
        prompt: Natural language description of the house.
        output: Optional output file path (overrides planner's default).

    Returns:
        Tuple of (file_path, summary_message).

    Examples:
        >>> file, summary = run_agent("casa de 12x8 metros com telhado")
        >>> print(summary)
        IFC house model saved to 'house.ifc'.
          Footprint: 12.0 m × 8.0 m (96.0 m²)
          ...
    """
    # Step 1: Parse prompt into structured plan
    plan = parse_prompt(prompt)

    # Step 2: Generate IFC file
    file_path = generate_ifc(plan, output=output)

    # Step 3: Generate summary
    summary = generate_ifc_summary(plan, file_path)

    return file_path, summary


def run_agent_with_plan(plan: HousePlan, output: str | Path | None = None) -> tuple[str, str]:
    """Generate IFC file from a pre-validated HousePlan.

    Use this when you already have a structured plan (e.g., from API payload).

    Args:
        plan: Pre-validated HousePlan instance.
        output: Optional output file path override.

    Returns:
        Tuple of (file_path, summary_message).
    """
    file_path = generate_ifc(plan, output=output)
    summary = generate_ifc_summary(plan, file_path)
    return file_path, summary
