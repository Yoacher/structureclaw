#!/usr/bin/env python3
"""
Test script for unified structural schema with OpenSeesPy export.
Validates the model and exports to OpenSees Python (openseespy) format.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from structure_model_v2_yjk_pkpm_numeric_ids import (
    StructureModelV2,
    example_payload_numeric,
    Story,
    Node,
    ElementV2,
    Material,
    SectionV2,
    LoadCase,
    LoadCombination,
    ProjectSettings
)


def validate_example_model():
    """Validate the example payload with pydantic."""
    print("=" * 60)
    print("1. Validating example model with pydantic...")
    print("=" * 60)

    example = example_payload_numeric()
    model = StructureModelV2(**example)

    print(f"✅ Schema validation successful!")
    print(f"   - Schema version: {model.schema_version}")
    print(f"   - Unit system: {model.unit_system}")
    print(f"   - Stories: {len(model.stories)}")
    print(f"   - Nodes: {len(model.nodes)}")
    print(f"   - Elements: {len(model.elements)}")
    print(f"   - Materials: {len(model.materials)}")
    print(f"   - Sections: {len(model.sections)}")
    print(f"   - Load cases: {len(model.load_cases)}")
    print(f"   - Load combinations: {len(model.load_combinations)}")

    return model


def export_to_opensees_py(model: StructureModelV2, output_path: str):
    """Export the model to OpenSees Python script using openseespy."""
    print("\n" + "=" * 60)
    print("2. Exporting to OpenSees Python (openseespy)...")
    print("=" * 60)

    lines = []

    # Header
    lines.append("# OpenSees model generated from unified schema (openseespy)")
    lines.append("# Schema version: {}".format(model.schema_version))
    lines.append("")

    # Import openseespy
    lines.append("# Import OpenSeesPy")
    lines.append("import openseespy.opensees as ops")
    lines.append("")

    # Basic settings (2D for demonstration)
    lines.append("# Initialize model")
    lines.append("ops.wipe()")
    lines.append("ops.model('basic', '-ndm', 2, '-ndf', 3)")
    lines.append("")

    # Define nodes (2D: use x, y only)
    lines.append("# Define nodes (2D)")
    for node in model.nodes:
        nid = int(node.id) if node.id.isdigit() else node.id
        x, y = node.x, node.y
        lines.append(f"ops.node({nid}, {x}, {y})")
        if node.restraints:
            # 2D: use first 3 DOF (ux, uy, rz)
            ux, uy, rz = int(node.restraints[0]), int(node.restraints[1]), int(node.restraints[5] if len(node.restraints) > 5 else 0)
            lines.append(f"ops.fix({nid}, {ux}, {uy}, {rz})")
    lines.append("")

    # Define materials
    lines.append("# Define materials")
    for mat in model.materials:
        mat_id = int(mat.id) if mat.id.isdigit() else mat.id
        E = mat.E
        lines.append(f"# Material: {mat.name} (grade: {mat.standard_grade})")
        lines.append(f"ops.uniaxialMaterial('Elastic', {mat_id}, {E})")
    lines.append("")

    # Define sections
    lines.append("# Define sections")
    for sec in model.sections:
        sec_id = int(sec.id) if sec.id.isdigit() else sec.id
        shape_type = sec.shape_type
        dims = sec.dimensions

        lines.append(f"# Section: {sec.name} (type: {shape_type})")

        if shape_type == "R":
            B = dims.get("B", 300)
            H = dims.get("H", 600)
            A = B * H
            Iy = B * H**3 / 12
            Iz = B * H**3 / 12
            J = Iy
            E = model.materials[0].E if model.materials else 30000.0
            nu = model.materials[0].nu if model.materials else 0.2
            G = E / (2 * (1 + nu))
            lines.append(f"ops.section('Elastic', {sec_id}, {A}, {E}, {G}, {J}, {Iy}, {Iz})")
        elif shape_type in ["I", "C"]:
            props = sec.properties
            A = props.get("A", 10000)
            Iy = props.get("Iy", 1e9)
            Iz = props.get("Iz", 1e9)
            J = Iy
            E = model.materials[0].E if model.materials else 30000.0
            nu = model.materials[0].nu if model.materials else 0.2
            G = E / (2 * (1 + nu))
            lines.append(f"ops.section('Elastic', {sec_id}, {A}, {E}, {G}, {J}, {Iy}, {Iz})")
        else:
            lines.append(f"# Section type {shape_type} not fully implemented; using placeholder")
            lines.append(f"ops.section('Elastic', {sec_id}, 10000, 30000, 12000, 10000, 1e9, 1e9)")
    lines.append("")

    # Define coordinate transformation for elements
    lines.append("# Define coordinate transformation")
    lines.append("ops.geomTransf('Linear', 1)  # 3D linear transformation")
    lines.append("")

    # Define elements
    lines.append("# Define elements")
    for elem in model.elements:
        elem_id = int(elem.id) if elem.id.isdigit() else elem.id
        nodes = [int(n) if n.isdigit() else n for n in elem.nodes]
        nodes_str = ", ".join(str(n) for n in nodes)
        sec_id = int(elem.section_id) if elem.section_id.isdigit() else elem.section_id
        # Use elasticBeamColumn: elementTag, node1, node2, secTag, transfTag
        lines.append(f"ops.element('elasticBeamColumn', {elem_id}, {nodes_str}, {sec_id}, 1)")
    lines.append("")

    # Define load cases
    lines.append("# Define load patterns")
    for lc in model.load_cases:
        lc_id = int(lc.id) if lc.id.isdigit() else lc.id
        lc_name = lc.name
        lc_type = lc.type

        lines.append(f"# Load case: {lc_name} (type: {lc_type})")

        if lc_type == "dead":
            ts_id = f"ts_{lc_id}"
            pat_id = f"pat_{lc_id}"
            lines.append(f"ops.timeSeries('Constant', {ts_id})")
            lines.append(f"ops.pattern('Plain', {pat_id}, {ts_id})")

            for load in lc.loads:
                load_type = load.get("type", "uniform")
                if load_type == "uniform":
                    elem_id_raw = load["element_id"]
                    elem_id = int(elem_id_raw) if elem_id_raw.isdigit() else elem_id_raw
                    value = load["value"]
                    direction = load.get("direction", "z")
                    if direction == "z":
                        lines.append(f"ops.eleLoad('-ele', {elem_id}, '-type', '-beamUniform', 0, {value}, 0)")
                    elif direction == "y":
                        lines.append(f"ops.eleLoad('-ele', {elem_id}, '-type', '-beamUniform', {value}, 0, 0)")
                    else:
                        lines.append(f"ops.eleLoad('-ele', {elem_id}, '-type', '-beamUniform', 0, 0, {value})")
                else:
                    lines.append(f"# Unsupported load type: {load_type}")

            lines.append("")

    # Define load combinations
    lines.append("# Define load combinations")
    for combo in model.load_combinations:
        combo_id = int(combo.id) if combo.id.isdigit() else combo.id
        combo_name = combo.name
        combo_type = combo.combination_type
        factors = combo.factors

        lines.append(f"# Combination: {combo_name} ({combo_type})")
        line_parts = [f"ops.pattern('Combine', {combo_id}"]
        for case_id_raw, factor in factors.items():
            case_id = int(case_id_raw) if case_id_raw.isdigit() else case_id_raw
            line_parts.append(f", {factor}, {case_id}")
        line_parts.append(")")
        lines.append("".join(line_parts))
    lines.append("")

    # Analysis settings
    lines.append("# Basic analysis settings")
    lines.append("ops.constraints('Transformation')")
    lines.append("ops.numberer('RCM')")
    lines.append("ops.system('BandGeneral')")
    lines.append("ops.integrator('LoadControl', 0.1)")
    lines.append("ops.test('NormUnbalance', 1e-6, 100)")
    lines.append("ops.algorithm('Newton')")
    lines.append("ops.analysis('Static')")
    lines.append("")

    # Perform analysis
    lines.append("# Perform analysis")
    lines.append("if ops.analyze(1) != 0:")
    lines.append("    print('Analysis failed')")
    lines.append("else:")
    lines.append("    print('Analysis successful')")
    lines.append("")

    lines.append("# End of generated model")
    lines.append("print('OpenSeesPy model generated successfully')")

    # Write to file
    output_file = Path(output_path)
    output_file.write_text("\n".join(lines))
    print(f"✅ Python script written to: {output_path}")
    print(f"   Total lines: {len(lines)}")


def main():
    """Main test workflow."""
    print("\n" + "=" * 60)
    print("UNIFIED STRUCTURAL SCHEMA TEST SUITE (OPENSEESPY)")
    print("=" * 60)

    # Step 1: Validate the schema
    model = validate_example_model()

    # Step 2: Export to OpenSees Python
    export_to_opensees_py(model, "opensees_model.py")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: /root/.openclaw/venv/bin/python opensees_model.py")
    print("2. Or import in your own Python script")
    print()


if __name__ == "__main__":
    main()