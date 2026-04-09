"""
Pydantic schemas for the AI BIM House Generator.

These models define the contract between the planner (LLM) and generator (IFC).
"""

from pydantic import BaseModel, Field


class HousePlan(BaseModel):
    """Schema for a rectangular house with optional roof."""

    width: float = Field(
        ...,
        description="House width in metres along the X axis",
        gt=0,
        example=10.0,
    )
    depth: float = Field(
        ...,
        description="House depth in metres along the Y axis",
        gt=0,
        example=10.0,
    )
    wall_height: float = Field(
        default=3.0,
        description="Height of the walls in metres",
        gt=0,
    )
    wall_thickness: float = Field(
        default=0.2,
        description="Thickness of the walls in metres",
        gt=0,
    )
    with_roof: bool = Field(
        default=False,
        description="Whether to add a gable roof",
    )
    ridge_height: float = Field(
        default=2.0,
        description="Height of the roof ridge above the wall tops in metres",
        gt=0,
    )
    output_path: str = Field(
        default="house.ifc",
        description="Output IFC filename",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "width": 10.0,
                "depth": 8.0,
                "wall_height": 3.0,
                "wall_thickness": 0.2,
                "with_roof": True,
                "ridge_height": 2.5,
                "output_path": "house.ifc",
            }
        }
