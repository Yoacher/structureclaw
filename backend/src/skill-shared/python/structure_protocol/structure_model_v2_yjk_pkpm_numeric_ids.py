"""
Unified structural analysis JSON schema compatible with YJK and PKPM.
This schema extends the existing structure_model_v1.py to support Chinese
structural analysis software requirements.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator


class ExtendableModel(BaseModel):
    """Base model with extensibility for vendor-specific data."""
    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Placeholder for vendor-specific data (YJK/PKPM)"
    )


class Story(ExtendableModel):
    """Storey/floor definition for YJK/PKPM compatibility."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    height: float = Field(..., description="Storey height (mm)")
    elevation: float = Field(..., description="Bottom elevation (mm)")
    is_standard_floor: bool = True
    similar_to: Optional[str] = Field(None, description="ID of the standard floor it copies")
    rigid_diaphragm: bool = Field(True, description="Whether the floor acts as a rigid diaphragm")


class Node(BaseModel):
    """Node/point in 3D space."""
    id: str = Field(..., min_length=1)
    x: float = Field(..., description="X coordinate (mm)")
    y: float = Field(..., description="Y coordinate (mm)")
    z: float = Field(..., description="Z coordinate (mm)")
    restraints: Optional[List[bool]] = Field(
        default=None, min_length=6, max_length=6,
        description="[ux, uy, uz, rx, ry, rz] restraints (True = fixed)"
    )
    springs: Optional[Dict[str, float]] = Field(default=None, description="Spring stiffnesses (kN/mm)")


class Release(BaseModel):
    """End releases for members."""
    start: List[bool] = Field(default=[False]*6, min_length=6, max_length=6)
    end: List[bool] = Field(default=[False]*6, min_length=6, max_length=6)


class ElementV2(ExtendableModel):
    """Structural element with YJK/PKPM specific attributes."""
    id: str = Field(..., min_length=1)
    type: Literal["beam", "column", "wall", "slab", "brace", "truss"] = "beam"
    nodes: List[str] = Field(..., min_length=2)
    material_id: str = Field(..., min_length=1)
    section_id: str = Field(..., min_length=1)
    story_id: str = Field(..., min_length=1)
    offset: List[float] = Field(default=[0.0, 0.0, 0.0], min_length=3, max_length=3, description="Offset [dx, dy, dz] in mm")
    releases: Optional[Release] = None
    rotation_angle: float = Field(0.0, description="Rotation angle (degrees)")
    group_id: Optional[str] = Field(None, description="Group ID for similar elements")


class Material(ExtendableModel):
    """Material properties with Chinese standard grades."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    standard_grade: str = Field(..., description="Chinese standard grade (e.g., 'C30', 'HRB400')")
    material_type: Literal["concrete", "steel", "rebar", "other"] = "concrete"
    E: float = Field(..., gt=0, description="Elastic modulus (MPa)")
    nu: float = Field(..., ge=0, le=0.5, description="Poisson's ratio")
    rho: float = Field(..., gt=0, description="Density (kg/m^3)")
    fy: Optional[float] = Field(None, gt=0, description="Yield strength (MPa)")
    fu: Optional[float] = Field(None, gt=0, description="Ultimate strength (MPa)")


class SectionV2(ExtendableModel):
    """Cross-section with Chinese standard shapes."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    shape_type: Literal["R", "T", "I", "C", "L", "PIPE", "BOX", "CIRCULAR"] = "R"
    dimensions: Dict[str, float] = Field(..., description="Geometric dimensions (mm)")
    properties: Dict[str, float] = Field(default_factory=dict, description="Calculated properties")


class LoadCase(ExtendableModel):
    """Load case with Chinese code classifications."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    type: Literal["dead", "live", "wind", "seismic", "snow", "temperature", "other"] = "other"
    code_category: Optional[str] = Field(None, description="Chinese code category")
    loads: List[Dict[str, Any]] = Field(default_factory=list)


class LoadCombination(ExtendableModel):
    """Load combination with Chinese code factors."""
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    combination_type: Literal["basic", "seismic", "accidental", "serviceability"] = "basic"
    factors: Dict[str, float] = Field(default_factory=dict)
    code_reference: Optional[str] = Field(None, description="Chinese code reference")


class ProjectSettings(ExtendableModel):
    """Project-level design parameters for Chinese codes."""
    design_code: str = Field("GB50011-2010", description="Primary design code")
    seismic_intensity: float = Field(7.0, ge=6.0, le=9.0, description="Seismic intensity")
    site_class: str = Field("II", description="Site classification")
    wind_pressure: float = Field(0.45, description="Basic wind pressure (kN/m^2)")
    damping_ratio: float = Field(0.05, description="Damping ratio")
    importance_factor: float = Field(1.0, description="Structure importance factor")
    design_life: int = Field(50, description="Design life (years)")


class StructureModelV2(BaseModel):
    """Unified structural analysis model for YJK and PKPM compatibility."""
    schema_version: str = Field("2.0.0")
    unit_system: str = Field("mm-kN", description="Units: mm for length, kN for force")
    project_settings: ProjectSettings
    stories: List[Story] = Field(default_factory=list)
    nodes: List[Node] = Field(default_factory=list)
    elements: List[ElementV2] = Field(default_factory=list)
    materials: List[Material] = Field(default_factory=list)
    sections: List[SectionV2] = Field(default_factory=list)
    load_cases: List[LoadCase] = Field(default_factory=list)
    load_combinations: List[LoadCombination] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_references(self):
        """Validate all cross-references between model components."""
        story_ids = {s.id for s in self.stories}
        node_ids = {n.id for n in self.nodes}
        material_ids = {m.id for m in self.materials}
        section_ids = {s.id for s in self.sections}
        load_case_ids = {lc.id for lc in self.load_cases}

        for elem in self.elements:
            if elem.story_id not in story_ids:
                raise ValueError(f"Element '{elem.id}' references unknown story '{elem.story_id}'")
            for node_id in elem.nodes:
                if node_id not in node_ids:
                    raise ValueError(f"Element '{elem.id}' references unknown node '{node_id}'")
            if elem.material_id not in material_ids:
                raise ValueError(f"Element '{elem.id}' references unknown material '{elem.material_id}'")
            if elem.section_id not in section_ids:
                raise ValueError(f"Element '{elem.id}' references unknown section '{elem.section_id}'")

        for combo in self.load_combinations:
            for case_id in combo.factors.keys():
                if case_id not in load_case_ids:
                    raise ValueError(f"Load combination '{combo.id}' references unknown load case '{case_id}'")

        return self


def example_payload_numeric() -> Dict[str, Any]:
    """Generate an example JSON payload with numeric IDs for OpenSees compatibility."""
    return {
        "schema_version": "2.0.0",
        "unit_system": "mm-kN",
        "project_settings": {
            "design_code": "GB50011-2010",
            "seismic_intensity": 8.0,
            "site_class": "II",
            "wind_pressure": 0.45,
            "damping_ratio": 0.05,
            "importance_factor": 1.0,
            "design_life": 50,
            "extensions": {"yjk_optimization_level": 2, "pkpm_analysis_method": "modal"}
        },
        "stories": [{
            "id": "1", "name": "1F", "height": 4500.0, "elevation": 0.0,
            "is_standard_floor": True, "rigid_diaphragm": True,
            "extensions": {"yjk_floor_type": "standard"}
        }],
        "nodes": [
            {"id": "1", "x": 0.0, "y": 0.0, "z": 0.0, "restraints": [True, True, True, False, False, False]},
            {"id": "2", "x": 6000.0, "y": 0.0, "z": 0.0, "restraints": [True, True, True, False, False, False]}
        ],
        "materials": [{
            "id": "1", "name": "C30 Concrete", "standard_grade": "C30",
            "material_type": "concrete", "E": 30000.0, "nu": 0.2, "rho": 2500.0,
            "extensions": {"yjk_material_id": 1, "pkpm_material_code": 3}
        }],
        "sections": [{
            "id": "1", "name": "300x600 Rectangular", "shape_type": "R",
            "dimensions": {"B": 300, "H": 600},
            "properties": {"A": 180000, "Ix": 5.4e9, "Iy": 1.35e9},
            "extensions": {"yjk_section_library": "standard", "pkpm_section_type": 1}
        }],
        "elements": [{
            "id": "1", "type": "beam", "nodes": ["1", "2"],
            "material_id": "1", "section_id": "1", "story_id": "1",
            "offset": [0.0, 0.0, 0.0], "rotation_angle": 0.0,
            "extensions": {"yjk_element_group": 1, "pkpm_reinforcement_type": "normal"}
        }],
        "load_cases": [{
            "id": "1", "name": "Dead Load", "type": "dead",
            "code_category": "GB50009-2012",
            "loads": [{"type": "uniform", "element_id": "1", "value": 5.0, "direction": "z"}]
        }],
        "load_combinations": [{
            "id": "1", "name": "Basic Combination 1", "combination_type": "basic",
            "factors": {"1": 1.2},
            "code_reference": "GB50009-2012 3.2.3"
        }],
        "metadata": {
            "created_by": "StructureClaw",
            "created_date": "2026-03-26",
            "description": "Example structure for YJK/PKPM compatibility (numeric IDs for OpenSees)"
        }
    }


if __name__ == "__main__":
    import json
    example = example_payload_numeric()
    model = StructureModelV2(**example)
    print("Schema validation successful!")
    print(f"Model has {len(model.stories)} stories, {len(model.nodes)} nodes, {len(model.elements)} elements")
    json_output = model.model_dump_json(indent=2)
    print("\nExample JSON output (first 1000 chars):")
    print(json_output[:1000] + "...")