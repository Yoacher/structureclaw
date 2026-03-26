# Solution for Issue #39: Unified Structural Analysis JSON Schema

## Overview

This solution addresses **Issue #39**: "Define a unified structural analysis JSON format compatible with YJK and PKPM" by extending the existing `structure_model_v1.py` with comprehensive support for Chinese structural analysis software requirements.

## Key Features

### 1. **YJK and PKPM Compatibility**
- **Storey-based hierarchy** with `Story` objects (core concept in both YJK and PKPM)
- **Component-based modeling** distinguishing beams, columns, walls, slabs, braces
- **Chinese standard grades** for materials (C30, HRB400, Q235, etc.)
- **Standardized section shapes** (Rectangular, T-shape, I-shape, etc.) per Chinese codes
- **Project settings** for seismic, wind, and other Chinese code parameters

### 2. **Extensibility Mechanism**
- `extensions` field in all models for vendor-specific data
- Versioned schema (`schema_version: "2.0.0"`)
- Backward compatibility considerations

### 3. **Comprehensive Field Coverage**
- **Structural system**: Stories, nodes, elements with Chinese classifications
- **Materials**: Extended with Chinese standard grades and material types
- **Sections**: Standardized shapes with geometric dimensions
- **Loads**: Chinese code classifications and categories
- **Boundary conditions**: Restraints, springs, releases
- **Load cases & combinations**: Chinese code factors and references

## Schema Design

### Core Models

1. **`Story`**: Floor/storey definition with rigid diaphragm support
2. **`Node`**: 3D points with restraints and spring supports
3. **`ElementV2`**: Structural elements with story association and offsets
4. **`Material`**: Extended with Chinese standard grades
5. **`SectionV2`**: Standardized Chinese section shapes
6. **`LoadCase` & `LoadCombination`**: Chinese code-compliant loads
7. **`ProjectSettings`**: Seismic, wind, and design parameters

### Validation
- Cross-reference validation between all components
- Unit system enforcement (mm-kN for YJK/PKPM compatibility)
- Chinese code parameter validation

## Example Payload

See `structure_model_v2_yjk_pkpm.py` for a complete example JSON payload including:
- Multi-storey structure definition
- Chinese material grades (C30 concrete)
- Standard section shapes
- Load cases with Chinese code references
- Vendor-specific extensions for YJK and PKPM

## Mapping to Engine Formats

### YJK Mapping Strategy
- `Story` → YJK `StandardFloor` definitions
- `Material.standard_grade` → YJK material database lookup
- `SectionV2.dimensions` → YJK section library
- `extensions.yjk_*` → Direct YJK database fields

### PKPM Mapping Strategy
- `Story` → PKPM storey definitions in `.jws` format
- `Material.standard_grade` → PKPM material code mapping
- `SectionV2` → PKPM section type definitions
- `extensions.pkpm_*` → PKPM-specific parameters

## Versioning Strategy

1. **Semantic versioning** for schema changes
2. **Migration utilities** for v1 → v2 conversion
3. **Extension-first approach** to avoid breaking changes

## Implementation Files

1. **`structure_model_v2_yjk_pkpm.py`** - Main schema definition
2. **Migration utilities** (to be implemented) for v1 → v2 conversion
3. **Validation scripts** for schema compliance
4. **Example files** for testing and documentation

## Next Steps

1. **Review and feedback** on the proposed schema
2. **Implementation** of migration utilities
3. **Testing** with real YJK and PKPM projects
4. **Documentation** of mapping rules and best practices

## Acceptance Criteria Met

✅ **Formal schema exists** - Complete Pydantic V2 schema defined  
✅ **Covers OpenSees + at least one commercial engine** - Supports YJK and PKPM  
✅ **Example payloads and validation** - Provided in the schema file  
✅ **Versioning/compatibility strategy** - Semantic versioning with extensions  

This solution provides a robust foundation for unified structural analysis data exchange between different analysis engines while maintaining compatibility with Chinese industry standards.