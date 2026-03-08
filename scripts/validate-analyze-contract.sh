#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x core/.venv-uv-lite/bin/python ]]; then
  PYTHON_BIN="core/.venv-uv-lite/bin/python"
elif [[ -x core/.venv/bin/python ]]; then
  PYTHON_BIN="core/.venv/bin/python"
else
  echo "No Python environment found at core/.venv or core/.venv-uv-lite" >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import asyncio
import sys

sys.path.insert(0, 'core')
from fastapi import HTTPException
from main import AnalysisRequest, analyze
from schemas.structure_model_v1 import StructureModelV1, Node, Element, Material, Section

model = StructureModelV1(
    schema_version='1.0.0',
    nodes=[
        Node(id='1', x=0, y=0, z=0, restraints=[True, True, True, True, True, True]),
        Node(id='2', x=0, y=0, z=3),
    ],
    elements=[Element(id='1', type='beam', nodes=['1', '2'], material='1', section='1')],
    materials=[Material(id='1', name='steel', E=200000, nu=0.3, rho=7850, fy=345)],
    sections=[
        Section(
            id='1',
            name='W',
            type='beam',
            properties={'A': 0.01, 'E': 200000, 'Iz': 0.0001, 'Iy': 0.0001, 'G': 79000, 'J': 0.0001},
        )
    ],
)

ok_request = AnalysisRequest(type='static', model=model, parameters={})
ok_result = asyncio.run(analyze(ok_request)).model_dump()
required = {'schema_version', 'analysis_type', 'success', 'error_code', 'message', 'data', 'meta'}
missing = required - set(ok_result.keys())
if missing:
    raise SystemExit(f'Missing analyze envelope fields: {sorted(missing)}')
if ok_result['success'] is not True:
    raise SystemExit('Expected success=true for static request')
if ok_result['analysis_type'] != 'static':
    raise SystemExit(f"Expected analysis_type=static, got {ok_result['analysis_type']}")
if ok_result['schema_version'] != '1.0.0':
    raise SystemExit(f"Expected schema_version=1.0.0, got {ok_result['schema_version']}")
if 'engineVersion' not in ok_result['meta'] or 'timestamp' not in ok_result['meta']:
    raise SystemExit('meta.engineVersion/meta.timestamp required')
print('[ok] analyze success envelope contract')

bad_request = AnalysisRequest(type='unknown', model=model, parameters={})
try:
    asyncio.run(analyze(bad_request))
    raise SystemExit('Expected HTTPException for invalid analysis type')
except HTTPException as exc:
    if exc.status_code != 400:
        raise SystemExit(f'Expected HTTP 400, got {exc.status_code}')
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    if detail.get('errorCode') != 'INVALID_ANALYSIS_TYPE':
        raise SystemExit(f"Expected INVALID_ANALYSIS_TYPE, got {detail.get('errorCode')}")
    print('[ok] analyze invalid type error contract')
PY
