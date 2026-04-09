"""Debug the roof profile points."""
import ifcopenshell

model = ifcopenshell.open("casa_telhado_FIXED.ifc")

roofs = model.by_type("IfcRoof")
for roof in roofs:
    print("=" * 60)
    print("ROOF PROFILE ANALYSIS")
    print("=" * 60)
    
    for rep in roof.Representation.Representations:
        for item in rep.Items:
            if item.is_a("IfcExtrudedAreaSolid"):
                profile = item.SweptArea
                print(f"\nProfile: {profile.is_a()}")
                print(f"Profile Type: {profile.ProfileType}")
                
                if profile.OuterCurve:
                    curve = profile.OuterCurve
                    print(f"Curve: {curve.is_a()}")
                    
                    if curve.is_a("IfcPolyline"):
                        print(f"Points in polyline: {len(curve.Points)}")
                        for i, point in enumerate(curve.Points):
                            coords = point.Coordinates
                            print(f"  Point {i}: {coords}")
                
                print(f"\nExtrusion:")
                print(f"  Direction: {item.ExtrudedDirection.DirectionRatios}")
                print(f"  Depth: {item.Depth}")
                
                if item.Position:
                    pos = item.Position
                    print(f"\nPosition (local to extrusion):")
                    print(f"  Location: {pos.Location.Coordinates if pos.Location else 'default'}")
                    print(f"  Axis: {pos.Axis.DirectionRatios if pos.Axis else 'default Z'}")
                    print(f"  RefDirection: {pos.RefDirection.DirectionRatios if pos.RefDirection else 'default X'}")

print("\n" + "=" * 60)
print("UNIT ASSIGNMENT")
print("=" * 60)

# Check units
for unit_assign in model.by_type("IfcUnitAssignment"):
    print(f"\nUnit Assignment: {unit_assign}")
    for unit in unit_assign.Units:
        if unit.is_a("IfcSIUnit"):
            print(f"  {unit.UnitType}: {unit.Name} (prefix: {unit.Prefix})")
