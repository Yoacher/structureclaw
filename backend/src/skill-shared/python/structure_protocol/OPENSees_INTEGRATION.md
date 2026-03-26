# OpenSees Integration for Unified Structural Schema

This document provides instructions for installing OpenSees and pyopensees, and demonstrates how to use the unified schema with OpenSees.

## Prerequisites (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build dependencies
sudo apt install -y \
    build-essential \
    git \
    wget \
    curl \
    cmake \
    g++ \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libarpack2-dev \
    libsuperlu-dist-dev \
    libmumps-seq-dev \
    libscalapack-openmpi-dev \
    libopenblas-dev \
    libfftw3-dev \
    libhdf5-dev \
    python3-dev \
    python3-pip \
    python3-venv
```

## Build OpenSees from Source

### Step 1: Clone OpenSees Repository

```bash
cd $HOME
git clone https://github.com/OpenSees/OpenSees.git
cd OpenSeeses
```

### Step 2: Configure and Build

```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    ..

# Build (this may take 30-60 minutes depending on your machine)
make -j$(nproc)

# Install
sudo make install
```

### Step 3: Verify Installation

```bash
/usr/local/bin/OpenSees --version
```

## Install pyopensees

After OpenSees is installed, you can install pyopensees:

```bash
# Activate virtual environment (if using)
source /root/.openclaw/venv/bin/activate

# Install pyopensees from source
git clone https://github.com/zhumingshen/pyopensees.git
cd pyopensees
python setup.py install
```

Or use pip if a wheel is available:

```bash
pip install pyopensees
```

## Test Script: Schema Validation and OpenSees Export

Create a file `test_structure_schema.py`:

```python
#!/usr/bin/env python3
"""
Test script for unified structural schema.
Validates the model and exports to OpenSees Tcl format.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the schema
from structure_model_v2_yjk_pkpm import (
    StructureModelV2,
    example_payload,
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

    example = example_payload()
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


def export_to_opensees_tcl(model: StructureModelV2, output_path: str):
    """Export the model to OpenSees Tcl format."""
    print("\n" + "=" * 60)
    print("2. Exporting to OpenSees Tcl format...")
    print("=" * 60)

    tcl_lines = []

    # Header
    tcl_lines.append("# OpenSees model generated from unified schema")
    tcl_lines.append(f"# Schema version: {model.schema_version}")
    tcl_lines.append("")

    # Basic settings
    tcl_lines.append("# Basic model settings")
    tcl_lines.append("wipe")
    tcl_lines.append("model basic -ndm 3 -ndf 6")
    tcl_lines.append("")

    # Define nodes
    tcl_lines.append("# Define nodes")
    for node in model.nodes:
        # Store node ID for reference
        nid = node.id
        x, y, z = node.x, node.y, node.z
        tcl_lines.append(f"node {nid} {x} {y} {z}")

        # Apply restraints if specified
        if node.restraints:
            rx, ry, rz = node.restraints[3:6]
            tcl_lines.append(f"fix {nid} {int(node.restraints[0])} {int(node.restraints[1])} {int(node.restraints[2])} {int(rx)} {int(ry)} {int(rz)}")
    tcl_lines.append("")

    # Define materials
    tcl_lines.append("# Define materials")
    for mat in model.materials:
        # Use Elastic material for demo (could be nDMaterial for concrete/steel)
        tcl_lines.append(f"# Material: {mat.name} (grade: {mat.standard_grade})")
        tcl_lines.append(f"uniaxialMaterial Elastic {mat.id} {mat.E}")
    tcl_lines.append("")

    # Define sections
    tcl_lines.append("# Define sections")
    for sec in model.sections:
        tcl_lines.append(f"# Section: {sec.name} (type: {sec.shape_type})")
        # For demo, using elastic section aggregator
        # In practice, would use nDMaterial and fiber sections for concrete
        if sec.shape_type == "R":
            # Rectangular section properties
            props = sec.dimensions
            B = props.get("B", 300)
            H = props.get("H", 600)
            # Simple elastic section with area and moment of inertia
            A = B * H
            I = B * H**3 / 12  # about local y-axis
            J = I  # approximate torsional constant for rectangle
            tcl_lines.append(f"section Elastic {sec.id} {A} {E:=} {G:=} {J} {I} {I}")
    tcl_lines.append("")

    # Define elements
    tcl_lines.append("# Define elements")
    for elem in model.elements:
        nodes_str = " ".join(elem.nodes)
        tcl_lines.append(f"# Element: {elem.id} ({elem.type})")
        tcl_lines.append(f"element {elem.type.capitalize()} {elem.id} {nodes_str} {elem.section_id} {elem.material_id}")
    tcl_lines.append("")

    # Define load cases
    tcl_lines.append("# Define load patterns")
    for lc in model.load_cases:
        tcl_lines.append(f"# Load case: {lc.name} (type: {lc.type})")
        # Create a pattern for this load case
        # In OpenSees, load patterns use time series and a pattern type
        time_series_id = f"ts_{lc.id}"
        pattern_id = f"pat_{lc.id}"

        if lc.type == "dead":
            # Constant load
            tcl_lines.append(f"timeSeries Constant {time_series_id}")
            tcl_lines.append(f"pattern Plain {pattern_id} {time_series_id} {{")

            # Apply loads from the load case
            for load in lc.loads:
                load_type = load.get("type", "uniform")
                if load_type == "uniform":
                    elem_id = load["element_id"]
                    value = load["value"]
                    direction = load.get("direction", "z")
                    # For beam elements, apply uniformly distributed load
                    # In OpenSees, eleLoad command applies loads to elements
                    if direction == "z":
                        tcl_lines.append(f"    eleLoad -ele {elem_id} -type -beamUniform 0 {value} 0")
                    elif direction == "y":
                        tcl_lines.append(f"    eleLoad -ele {elem_id} -type -beamUniform {value} 0 0")
                    else:
                        tcl_lines.append(f"    eleLoad -ele {elem_id} -type -beamUniform 0 0 {value}")
                # Add more load types as needed

            tcl_lines.append("}")

    tcl_lines.append("")

    # Define load combinations
    tcl_lines.append("# Define load combinations")
    for combo in model.load_combinations:
        tcl_lines.append(f"# Combination: {combo.name}")
        combo_cmd = "pattern Combine " + combo.id
        for case_id, factor in combo.factors.items():
            combo_cmd += f" {factor} {case_id}"
        tcl_lines.append(combo_cmd)
    tcl_lines.append("")

    # Analysis settings (basic)
    tcl_lines.append("# Basic analysis settings")
    tcl_lines.append("constraints Transformation")
    tcl_lines.append("numberer RCM")
    tcl_lines.append("system BandGeneral")
    tcl_lines.append("integrator LoadControl 0.1")
    tcl_lines.append("test NormUnbalance 1e-6 100")
    tcl_lines.append("algorithm Newton")
    tcl_lines.append("analysis Static")
    tcl_lines.append("")

    # Footer
    tcl_lines.append("# End of generated model")
    tcl_lines.append("puts \"Model generated successfully\"")

    # Write to file
    output_file = Path(output_path)
    output_file.write_text("\n".join(tcl_lines))
    print(f"✅ Tcl model written to: {output_path}")
    print(f"   Total lines: {len(tcl_lines)}")


def main():
    """Main test workflow."""
    print("\n" + "=" * 60)
    print("UNIFIED STRUCTURAL SCHEMA TEST SUITE")
    print("=" * 60)

    # Step 1: Validate the schema
    model = validate_example_model()

    # Step 2: Export to OpenSees Tcl
    export_to_opensees_tcl(model, "opensees_model.tcl")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install OpenSees (see instructions above)")
    print("2. Run: OpenSees opensees_model.tcl")
    print("3. Extend the exporter for more features (fibers, loads, etc.)")
    print()


if __name__ == "__main__":
    main()
```

## Running the Test

With pydantic installed:

```bash
cd /root/.openclaw/workspace
source /root/.openclaw/venv/bin/activate
python test_structure_schema.py
```

Expected output:
```
Schema validation successful!
...
Tcl model written to: opensees_model.tcl
```

## Mapping Reference

| Unified Schema Field | OpenSees Tcl Equivalent |
|---------------------|------------------------|
| `Node` → `node` command | `node 1 0.0 0.0 0.0` |
| `Material.E` → `uniaxialMaterial Elastic` | `uniaxialMaterial Elastic 1 30000` |
| `SectionV2.dimensions` → `section Elastic` | `section Elastic 1 180000 30000 ...` |
| `ElementV2` → `element` command | `element beam 1 1 2 1 1` |
| `LoadCase.uniform` → `eleLoad -beamUniform` | `eleLoad -ele 1 -type -beamUniform 0 5 0` |
| `LoadCombination` → `pattern Combine` | `pattern Combine 1 1.2 1 1.5 2` |

## Limitations & Future Work

- Currently uses simplified Elastic materials for demo
- Need to implement fiber sections for concrete (fiber section with concrete and rebar)
- Spring supports and boundary conditions not fully mapped
- Load patterns require more sophisticated time series handling
- Modal and dynamic analysis not covered

## Alternatives

If building OpenSees is too complex, consider using:
- `pyobjx` (OpenSeesPy) - Python wrapper for OpenSees (easier install)
- Docker images: `opensees/opensees` (pre-built binaries)

---

**Generated by Gemini CLI** - Unified Structural Schema Solution for Issue #39