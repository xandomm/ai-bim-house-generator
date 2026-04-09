"""
AI BIM House Generator Agent

An AI agent powered by LangChain + Google Gemini that generates IFC house models
from natural language descriptions.

Usage:
    uv run agent.py
"""

import math
import os

import ifcopenshell
import ifcopenshell.api
import numpy as np
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from generate_house import create_roof, create_slab, create_wall

load_dotenv()


# ---------------------------------------------------------------------------
# Tools exposed to the agent
# ---------------------------------------------------------------------------


@tool
def generate_rectangular_house(
    width: float,
    depth: float,
    wall_height: float = 3.0,
    wall_thickness: float = 0.2,
    with_roof: bool = False,
    ridge_height: float = 2.0,
    output_path: str = "house.ifc",
) -> str:
    """Generate an IFC house model with a rectangular footprint.

    Args:
        width: House width in metres along the X axis.
        depth: House depth in metres along the Y axis.
        wall_height: Height of the walls in metres (default 3.0).
        wall_thickness: Thickness of the walls in metres (default 0.2).
        with_roof: Whether to add a gable roof (default False).
        ridge_height: Height of the roof ridge above the wall tops in metres (default 2.0).
        output_path: Filename for the output IFC file (default 'house.ifc').

    Returns:
        A message confirming the file was created and describing the house.
    """
    model = ifcopenshell.api.run("project.create_file", version="IFC4")

    project = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcProject", name="House Project"
    )
    ifcopenshell.api.run("unit.assign_unit", model)

    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body = ifcopenshell.api.run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )

    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcBuilding", name="Building"
    )
    storey = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor"
    )

    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, products=[site])
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, products=[building])
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=building, products=[storey])

    # South wall
    create_wall(model, storey, body, x=0.0, y=0.0, length=width, angle=0.0,
                height=wall_height, thickness=wall_thickness)
    # East wall
    create_wall(model, storey, body, x=width, y=0.0, length=depth, angle=math.pi / 2,
                height=wall_height, thickness=wall_thickness)
    # North wall
    create_wall(model, storey, body, x=width, y=depth, length=width, angle=math.pi,
                height=wall_height, thickness=wall_thickness)
    # West wall
    create_wall(model, storey, body, x=0.0, y=depth, length=depth, angle=-math.pi / 2,
                height=wall_height, thickness=wall_thickness)

    # Floor slab
    create_slab(model, storey, body, width=width, depth=depth, thickness=wall_thickness)

    # Gable roof (optional)
    if with_roof:
        create_roof(model, storey, body,
                    width=width, depth=depth,
                    wall_height=wall_height, ridge_height=ridge_height)

    model.write(output_path)

    area = width * depth
    roof_info = f"\n  Roof: gable, ridge height {ridge_height:.1f} m" if with_roof else ""
    return (
        f"IFC house model saved to '{output_path}'.\n"
        f"  Footprint : {width:.1f} m × {depth:.1f} m ({area:.1f} m²)\n"
        f"  Wall height: {wall_height:.1f} m\n"
        f"  Wall thickness: {wall_thickness:.2f} m"
        f"{roof_info}"
    )


# ---------------------------------------------------------------------------
# Agent setup
# ---------------------------------------------------------------------------

TOOLS = [generate_rectangular_house]

SYSTEM_PROMPT = (
    "You are an expert BIM (Building Information Modeling) assistant that generates "
    "IFC house models. When the user describes a house, extract the dimensions and "
    "call the appropriate tool to generate the IFC file. "
    "The tool supports: width, depth, wall height, wall thickness, and an optional "
    "gable roof (with_roof=True) with a configurable ridge height. "
    "Always confirm what was built and mention the output file. "
    "If the user does not specify dimensions, use sensible defaults (10 m × 10 m, "
    "3 m wall height). If the user asks for a roof, set with_roof=True. "
    "Respond in the same language the user uses."
)


def main() -> None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise EnvironmentError(
            "GOOGLE_API_KEY not set. Add your key to the .env file."
        )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=api_key)
    agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)

    print("AI BIM House Generator Agent")
    print("Type your house description or 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit", "sair"}:
            print("Bye!")
            break
        if not user_input:
            continue

        response = agent.invoke({"messages": [("human", user_input)]})
        last_message = response["messages"][-1]
        print(f"\nAgent: {last_message.content}\n")


if __name__ == "__main__":
    main()
