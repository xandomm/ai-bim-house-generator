"""Debug script to inspect roof geometry in IFC file."""
import ifcopenshell

# Open the IFC file
model = ifcopenshell.open("casa_telhado_v2.ifc")

print("=" * 60)
print("IFC ROOF DEBUG")
print("=" * 60)

# Find all roofs
roofs = model.by_type("IfcRoof")
print(f"\n📐 Roofs found: {len(roofs)}\n")

for roof in roofs:
    print(f"Roof: {roof}")
    print(f"  GlobalId: {roof.GlobalId}")
    print(f"  Name: {roof.Name}")
    
    # Check representation
    if roof.Representation:
        print(f"  ✅ Has Representation: {roof.Representation}")
        for rep in roof.Representation.Representations:
            print(f"    - Type: {rep.RepresentationType}")
            print(f"    - Identifier: {rep.RepresentationIdentifier}")
            print(f"    - Items: {len(rep.Items)} item(s)")
            
            for item in rep.Items:
                print(f"      • {item.is_a()}")
                if item.is_a("IfcExtrudedAreaSolid"):
                    print(f"        Depth: {item.Depth}")
                    print(f"        Profile: {item.SweptArea}")
                    print(f"        Extrude Direction: {item.ExtrudedDirection.DirectionRatios}")
    else:
        print(f"  ❌ No Representation")
    
    # Check placement
    if roof.ObjectPlacement:
        print(f"  ✅ Has Placement: {roof.ObjectPlacement.is_a()}")
        if roof.ObjectPlacement.is_a("IfcLocalPlacement"):
            rel = roof.ObjectPlacement.RelativePlacement
            if rel.is_a("IfcAxis2Placement3D"):
                print(f"    Location: {rel.Location.Coordinates if rel.Location else 'None'}")
    else:
        print(f"  ❌ No Placement")
    
    # Check container
    for rel in model.by_type("IfcRelContainedInSpatialStructure"):
        if roof in rel.RelatedElements:
            print(f"  ✅ Contained in: {rel.RelatingStructure.Name}")
    
    print()

# Check all walls for comparison
walls = model.by_type("IfcWall")
print(f"\n🧱 Walls found: {len(walls)} (for comparison)")
for i, wall in enumerate(walls[:2], 1):  # Show first 2 walls
    print(f"  Wall {i}: {wall.Name}, HasRep: {bool(wall.Representation)}")

print("\n" + "=" * 60)
