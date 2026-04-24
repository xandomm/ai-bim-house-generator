#!/usr/bin/env python
"""
CLI entrypoint for the AI BIM House Generator.

Usage:
    python scripts/generate_ifc.py "casa de 10x12 metros com telhado"
    python scripts/generate_ifc.py --width 10 --depth 12 --roof
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.agent import run_agent, run_agent_with_plan
from models.schema import HousePlan


def main():
    parser = argparse.ArgumentParser(
        description="Generate IFC house models from prompts or parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From natural language prompt
  python scripts/generate_ifc.py "casa moderna de 12x8 metros"

  # With explicit parameters
  python scripts/generate_ifc.py --width 10 --depth 12 --roof --output my_house.ifc

  # Interactive mode
  python scripts/generate_ifc.py --interactive
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Natural language description of the house",
    )
    parser.add_argument(
        "--width",
        type=float,
        help="House width in metres (X axis)",
    )
    parser.add_argument(
        "--depth",
        type=float,
        help="House depth in metres (Y axis)",
    )
    parser.add_argument(
        "--wall-height",
        type=float,
        default=3.0,
        help="Wall height in metres (default: 3.0)",
    )
    parser.add_argument(
        "--wall-thickness",
        type=float,
        default=0.2,
        help="Wall thickness in metres (default: 0.2)",
    )
    parser.add_argument(
        "--roof",
        action="store_true",
        help="Add a gable roof",
    )
    parser.add_argument(
        "--ridge-height",
        type=float,
        default=2.0,
        help="Roof ridge height in metres (default: 2.0)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="house.ifc",
        help="Output IFC filename (default: house.ifc)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode (prompt loop)",
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        run_interactive()
        return

    # Generate from explicit parameters
    if args.width and args.depth:
        plan = HousePlan(
            width=args.width,
            depth=args.depth,
            wall_height=args.wall_height,
            wall_thickness=args.wall_thickness,
            with_roof=args.roof,
            ridge_height=args.ridge_height,
            output_path=args.output,
        )
        file_path, summary = run_agent_with_plan(plan, output=args.output)
        print(summary)
        return

    # Generate from prompt
    if args.prompt:
        file_path, summary = run_agent(args.prompt, output=args.output)
        print(summary)
        return

    # No arguments provided
    parser.print_help()
    sys.exit(1)


def run_interactive():
    """Interactive mode: prompt loop."""
    print("AI BIM House Generator - Interactive Mode")
    print("Type your house description or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if user_input.lower() in {"quit", "exit", "sair", "q"}:
            print("Bye!")
            break

        if not user_input:
            continue

        try:
            file_path, summary = run_agent(user_input)
            print(f"\n{summary}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
