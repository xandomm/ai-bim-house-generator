"""
Generator: converts HousePlan schemas into IFC files using ifcopenshell.

This module orchestrates the IFC generation pipeline:
  1. Create IFC project structure (project → site → building → storey)
  2. Generate geometry (walls, slab, roof) using helpers from generate_house
  3. Write IFC file to disk
"""

import math
from pathlib import Path

import ifcopenshell
import ifcopenshell.api
from models.schema import HousePlan

# Import geometry helpers
from generate_house import create_roof, create_slab, create_wall


def generate_ifc(plan: HousePlan, output: str | Path | None = None) -> str:
    """Generate an IFC file from a HousePlan schema.

    Args:
        plan: Validated HousePlan with all geometric parameters.
        output: Optional output path override (defaults to plan.output_path).

    Returns:
        Path to the generated IFC file.

    Raises:
        ValueError: If plan validation fails.
    """
    output_path = str(output) if output else plan.output_path

    # --- 1. Create IFC4 file and project structure ---
    model = ifcopenshell.api.run("project.create_file", version="IFC4")

    project = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcProject", name="House Project"
    )
    # Assign units explicitly: METRES (not millimetres)
    length = model.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    area = model.create_entity("IfcSIUnit", UnitType="AREAUNIT", Name="SQUARE_METRE")
    volume = model.create_entity("IfcSIUnit", UnitType="VOLUMEUNIT", Name="CUBIC_METRE")
    units = model.create_entity("IfcUnitAssignment", Units=[length, area, volume])
    project.UnitsInContext = units

    # Geometry contexts
    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body = ifcopenshell.api.run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )

    # Spatial hierarchy
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

    # --- 2. Generate geometry from plan ---
    w = plan.width
    d = plan.depth
    h = plan.wall_height
    t = plan.wall_thickness

    # Four walls (south, east, north, west)
    create_wall(model, storey, body, x=0.0, y=0.0, length=w, angle=0.0, height=h, thickness=t)
    create_wall(model, storey, body, x=w, y=0.0, length=d, angle=math.pi / 2, height=h, thickness=t)
    create_wall(model, storey, body, x=w, y=d, length=w, angle=math.pi, height=h, thickness=t)
    create_wall(model, storey, body, x=0.0, y=d, length=d, angle=-math.pi / 2, height=h, thickness=t)

    # Floor slab
    create_slab(model, storey, body, width=w, depth=d, thickness=t)

    # Optional gable roof
    if plan.with_roof:
        create_roof(model, storey, body, width=w, depth=d, wall_height=h, ridge_height=plan.ridge_height)

    # --- 3. Write IFC file ---
    model.write(output_path)

    return output_path


def generate_ifc_summary(plan: HousePlan, output_path: str) -> str:
    """Generate a human-readable summary of the IFC generation result.

    Args:
        plan: The HousePlan that was generated.
        output_path: Path to the written IFC file.

    Returns:
        Formatted summary string.
    """
    area = plan.width * plan.depth
    roof_info = (
        f"\n  Roof: gable, ridge height {plan.ridge_height:.1f} m"
        if plan.with_roof
        else ""
    )

    return (
        f"IFC house model saved to '{output_path}'.\n"
        f"  Footprint: {plan.width:.1f} m × {plan.depth:.1f} m ({area:.1f} m²)\n"
        f"  Wall height: {plan.wall_height:.1f} m\n"
        f"  Wall thickness: {plan.wall_thickness:.2f} m"
        f"{roof_info}"
    )
