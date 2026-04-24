"""
Generate a simple IFC house model using ifcopenshell.api.

Creates a 10m x 10m single-storey house with:
- 4 walls (height=3m, thickness=0.2m)
- 1 floor slab

Output: house.ifc
"""

import math

import ifcopenshell
import ifcopenshell.api
import numpy as np


def create_wall(model, storey, body_context, x, y, length, angle, height=3.0, thickness=0.2):
    """Create an IfcWall with a swept-area representation.

    Parameters
    ----------
    model         : ifcopenshell.file  - the IFC model
    storey        : IfcBuildingStorey  - spatial container for the wall
    body_context  : IfcGeometricRepresentationSubContext
    x, y          : float - origin of the wall in plan (metres)
    length        : float - wall length along its local X axis (metres)
    angle         : float - rotation around the global Z axis (radians)
    height        : float - wall height (metres)
    thickness     : float - wall thickness (metres)
    """
    # Create the IfcWall entity
    wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

    # Build a parametric wall representation (SweptSolid)
    representation = ifcopenshell.api.run(
        "geometry.add_wall_representation",
        model,
        context=body_context,
        length=length,
        height=height,
        thickness=thickness,
    )
    ifcopenshell.api.run("geometry.assign_representation", model, product=wall, representation=representation)

    # Position and rotate the wall using a 4×4 transformation matrix.
    # NumPy uses row-major order: matrix[row][col], so the last column holds the translation
    # and the upper-left 3×3 block holds the rotation.
    matrix = np.eye(4)
    # Rotation around Z axis by `angle` radians
    matrix[0][0] = math.cos(angle)
    matrix[0][1] = -math.sin(angle)
    matrix[1][0] = math.sin(angle)
    matrix[1][1] = math.cos(angle)
    # Translation to wall origin
    matrix[0][3] = x
    matrix[1][3] = y

    ifcopenshell.api.run("geometry.edit_object_placement", model, product=wall, matrix=matrix)

    # Place the wall inside the building storey
    ifcopenshell.api.run("spatial.assign_container", model, relating_structure=storey, products=[wall])

    return wall


def create_slab(model, storey, body_context, width, depth, thickness=0.2):
    """Create an IfcSlab covering the full floor footprint.

    Parameters
    ----------
    model         : ifcopenshell.file  - the IFC model
    storey        : IfcBuildingStorey  - spatial container for the slab
    body_context  : IfcGeometricRepresentationSubContext
    width         : float - slab dimension along X (metres)
    depth         : float - slab dimension along Y (metres)
    thickness     : float - slab extrusion depth (metres)
    """
    # Create the IfcSlab entity
    slab = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSlab")

    # Define the rectangular footprint as a closed polyline and extrude it
    polyline = [(0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth)]
    representation = ifcopenshell.api.run(
        "geometry.add_slab_representation",
        model,
        context=body_context,
        depth=thickness,
        polyline=polyline,
    )
    ifcopenshell.api.run("geometry.assign_representation", model, product=slab, representation=representation)

    # Place the slab at the storey origin (elevation 0)
    matrix = np.eye(4)
    ifcopenshell.api.run("geometry.edit_object_placement", model, product=slab, matrix=matrix)

    # Place the slab inside the building storey
    ifcopenshell.api.run("spatial.assign_container", model, relating_structure=storey, products=[slab])

    return slab


def create_roof(model, storey, body_context, width, depth, wall_height, ridge_height=2.0):
    """Create a gable IfcRoof as an extruded triangular solid (SweptSolid).

    Parameters
    ----------
    model         : ifcopenshell.file
    storey        : IfcBuildingStorey
    body_context  : IfcGeometricRepresentationSubContext
    width         : float - house width along X (metres)
    depth         : float - house depth along Y (metres)
    wall_height   : float - elevation at which the roof base sits (metres)
    ridge_height  : float - height of the ridge above wall tops (metres)
    """
    # Create the IfcRoof entity
    roof = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcRoof")

    # Create triangular profile using 2D points (for profile plane)
    # Triangle: base at Y=0 from X=0 to X=width, apex at (width/2, ridge_height)
    points_2d = [
        model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0)),
        model.create_entity("IfcCartesianPoint", Coordinates=(float(width), 0.0)),
        model.create_entity("IfcCartesianPoint", Coordinates=(float(width / 2), float(ridge_height))),
        model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0)),  # Close the loop
    ]
    
    # Create polyline and profile
    polyline = model.create_entity("IfcPolyline", Points=points_2d)
    profile = model.create_entity("IfcArbitraryClosedProfileDef", 
                                   ProfileType="AREA", 
                                   ProfileName=None, 
                                   OuterCurve=polyline)

    # Position: place profile in XY plane, extrude along Z (depth direction)
    origin = model.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    axis_z = model.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    axis_x = model.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    placement = model.create_entity("IfcAxis2Placement3D", Location=origin, Axis=axis_z, RefDirection=axis_x)

    # Extrude along Y axis for depth
    extrude_direction = model.create_entity("IfcDirection", DirectionRatios=(0.0, 1.0, 0.0))
    extruded_solid = model.create_entity("IfcExtrudedAreaSolid",
                                          SweptArea=profile,
                                          Position=placement,
                                          ExtrudedDirection=extrude_direction,
                                          Depth=float(depth))

    # Create representation
    representation = model.create_entity("IfcShapeRepresentation",
                                          ContextOfItems=body_context,
                                          RepresentationIdentifier="Body",
                                          RepresentationType="SweptSolid",
                                          Items=[extruded_solid])

    # Assign representation
    ifcopenshell.api.run("geometry.assign_representation", model, product=roof, representation=representation)

    # Position roof at the top of walls
    matrix = np.eye(4)
    matrix[2][3] = float(wall_height)
    ifcopenshell.api.run("geometry.edit_object_placement", model, product=roof, matrix=matrix)

    # Assign to storey
    ifcopenshell.api.run("spatial.assign_container", model, relating_structure=storey, products=[roof])

    return roof


def main():
    # --- 1. Create a new blank IFC4 file ---
    model = ifcopenshell.api.run("project.create_file", version="IFC4")

    # --- 2. Create the IfcProject and assign SI units (metres) ---
    project = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcProject", name="House Project"
    )
    ifcopenshell.api.run("unit.assign_unit", model)

    # --- 3. Set up geometry contexts ---
    # Top-level "Model" context
    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    # "Body" sub-context used for all 3-D solid representations
    body = ifcopenshell.api.run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )

    # --- 4. Build the spatial hierarchy ---
    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcBuilding", name="Building"
    )
    storey = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor"
    )

    # Aggregate: Project → Site → Building → Storey
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, products=[site])
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, products=[building])
    ifcopenshell.api.run(
        "aggregate.assign_object", model, relating_object=building, products=[storey]
    )

    # --- 5. House dimensions ---
    house_width = 10.0      # metres, along X
    house_depth = 10.0      # metres, along Y
    wall_height = 3.0       # metres
    wall_thickness = 0.2    # metres

    # --- 6. Create 4 walls forming a closed rectangular perimeter ---
    #
    # Each wall's local X axis starts at its origin and extends along `length`.
    # The rotation angle turns the wall to face the correct side.
    #
    #   North (Y=10) ←←←←←←← (angle = π)
    #      ↑                         ↑
    #   West                       East  (angle = π/2)
    #   (angle = -π/2)              ↑
    #      ↑                         ↑
    #   South (Y=0) →→→→→→→→→ (angle = 0)

    # South wall: starts at (0, 0), runs east
    create_wall(model, storey, body, x=0.0, y=0.0,
                length=house_width, angle=0.0,
                height=wall_height, thickness=wall_thickness)

    # East wall: starts at (10, 0), runs north
    create_wall(model, storey, body, x=house_width, y=0.0,
                length=house_depth, angle=math.pi / 2,
                height=wall_height, thickness=wall_thickness)

    # North wall: starts at (10, 10), runs west
    create_wall(model, storey, body, x=house_width, y=house_depth,
                length=house_width, angle=math.pi,
                height=wall_height, thickness=wall_thickness)

    # West wall: starts at (0, 10), runs south
    create_wall(model, storey, body, x=0.0, y=house_depth,
                length=house_depth, angle=-math.pi / 2,
                height=wall_height, thickness=wall_thickness)

    # --- 7. Create the floor slab ---
    create_slab(model, storey, body,
                width=house_width, depth=house_depth, thickness=wall_thickness)

    # --- 8. Write the IFC file ---
    output_path = "house.ifc"
    model.write(output_path)
    print(f"IFC model saved as '{output_path}'")


if __name__ == "__main__":
    main()
