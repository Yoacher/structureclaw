# Codebase Structure

**Analysis Date:** 2026-03-09

## Directory Layout

```
structureclaw/
├── backend/                 # Fastify API service (TypeScript)
│   ├── src/                 # Source code
│   ├── prisma/              # Database schema and migrations
│   ├── tests/               # Test files
│   └── package.json         # Node dependencies
├── core/                    # FastAPI analysis engine (Python)
│   ├── fem/                 # Finite element analysis modules
│   ├── design/              # Design and code check modules
│   ├── converters/          # Format converters
│   ├── schemas/             # Data models
│   ├── regression/          # Regression test cases
│   └── main.py              # FastAPI app entry
├── frontend/                # Next.js frontend (TypeScript/React)
│   ├── src/                 # Source code
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities
│   └── package.json         # Node dependencies
├── docker/                  # Docker configuration
│   └── nginx/               # Nginx config and SSL
├── scripts/                 # Development and validation scripts
├── docs/                    # Documentation (placeholder)
├── uploads/                 # File uploads (reports, etc.)
├── .runtime/                # Runtime files (pids, logs)
├── .planning/               # Planning documents (generated)
├── sclaw                    # CLI entry script
├── Makefile                 # Development commands
├── docker-compose.yml       # Full stack orchestration
└── package.json             # Root package (CLI wrapper)
```

## Directory Purposes

**backend/:**
- Purpose: API service handling business logic, agent orchestration, data persistence
- Contains: TypeScript source, Prisma schema, tests
- Key files: `src/index.ts`, `src/services/agent.ts`, `src/api/routes.ts`, `prisma/schema.prisma`

**core/:**
- Purpose: Structural analysis engine with FEM capabilities
- Contains: Python modules for analysis, design, conversion
- Key files: `main.py`, `fem/static_analysis.py`, `schemas/structure_model_v1.py`

**frontend/:**
- Purpose: Web UI for agent console and user interaction
- Contains: React components, Next.js pages, styling
- Key files: `src/app/console/page.tsx`, `src/components/console/agent-console.tsx`

**scripts/:**
- Purpose: Development automation and validation scripts
- Contains: Shell scripts for regression, startup, validation
- Key files: `dev-up.sh`, `check-backend-regression.sh`, `validate-*.sh`

**docker/:**
- Purpose: Container configuration
- Contains: Nginx reverse proxy config
- Key files: `nginx/nginx.conf`

**uploads/:**
- Purpose: Generated file storage (reports, exports)
- Contains: Runtime-generated files
- Not committed to git

**.runtime/:**
- Purpose: Local development runtime state
- Contains: PID files, log files
- Not committed to git

## Key File Locations

**Entry Points:**
- `backend/src/index.ts`: Backend API server entry
- `core/main.py`: Core analysis engine entry
- `frontend/src/app/layout.tsx`: Frontend root layout
- `sclaw`: CLI wrapper script

**Configuration:**
- `backend/src/config/index.ts`: Backend configuration (env-based)
- `core/requirements.txt`: Python full dependencies
- `core/requirements-lite.txt`: Python lite dependencies
- `.env.example`: Environment variable template
- `docker-compose.yml`: Container orchestration config

**Core Logic:**
- `backend/src/services/agent.ts`: Agent orchestration service
- `backend/src/services/chat.ts`: Chat/conversation service
- `core/fem/static_analysis.py`: Static FEM analysis
- `core/design/code_check.py`: Code compliance checking
- `core/converters/registry.py`: Format converter registry

**Data Models:**
- `backend/prisma/schema.prisma`: Database schema (PostgreSQL)
- `core/schemas/structure_model_v1.py`: Canonical structure model

**Testing:**
- `backend/tests/`: Backend test files
- `core/regression/`: Core regression test cases
- `scripts/validate-*.sh`: Validation scripts

**API Routes:**
- `backend/src/api/routes.ts`: Route registration
- `backend/src/api/agent.ts`: Agent endpoints
- `backend/src/api/chat.ts`: Chat endpoints

## Naming Conventions

**Files:**
- TypeScript: `kebab-case.ts` for modules, `PascalCase.tsx` for components
- Python: `snake_case.py` for all modules
- Shell scripts: `kebab-case.sh`
- Config: `snake_case.txt` for requirements, `camelCase.json` for package files

**Directories:**
- TypeScript: `kebab-case` (e.g., `components`, `services`)
- Python: `snake_case` (e.g., `static_analysis`, `code_check`)

**Classes/Types:**
- TypeScript services: `PascalCase` class names (e.g., `AgentService`, `ChatService`)
- Python classes: `PascalCase` (e.g., `StaticAnalyzer`, `StructureModelV1`)

**Functions/Methods:**
- TypeScript: `camelCase` (e.g., `sendMessage`, `runRequest`)
- Python: `snake_case` (e.g., `run_analysis`, `validate_structure_model`)

## Where to Add New Code

**New API Endpoint:**
- Route definition: `backend/src/api/<domain>.ts`
- Service logic: `backend/src/services/<domain>.ts`
- Register route: `backend/src/api/routes.ts`

**New Analysis Type:**
- Analyzer class: `core/fem/<type>_analysis.py`
- Register in: `core/main.py` analyze endpoint switch
- Add regression: `core/regression/<type>/`

**New Format Converter:**
- Converter class: `core/converters/<format>_converter.py`
- Extend base: `core/converters/base.py` (FormatConverter)
- Register in: `core/converters/registry.py`

**New Frontend Page:**
- Page component: `frontend/src/app/<route>/page.tsx`
- Shared components: `frontend/src/components/`
- UI primitives: `frontend/src/components/ui/`

**New Database Model:**
- Schema definition: `backend/prisma/schema.prisma`
- Migration: `npm run db:migrate --prefix backend`
- Service methods: `backend/src/services/<domain>.ts`

**New Agent Tool:**
- Tool implementation: `backend/src/services/agent.ts` (add to tool execution)
- Tool registration: Update `AgentToolName` type
- Validation script: `scripts/validate-agent-tools-contract.sh`

**New Validation Script:**
- Script file: `scripts/validate-<feature>.sh`
- Register in: `scripts/check-backend-regression.sh` or `scripts/check-core-regression.sh`

## Special Directories

**node_modules/:**
- Purpose: NPM dependencies
- Generated: Yes (npm install)
- Committed: No (in .gitignore)
- Location: `backend/node_modules/`, `frontend/node_modules/`

**.venv/:**
- Purpose: Python virtual environment
- Generated: Yes (make setup-core-*)
- Committed: No
- Location: `core/.venv/`

**.next/:**
- Purpose: Next.js build output
- Generated: Yes (npm run build)
- Committed: No
- Location: `frontend/.next/`

**__pycache__/:**
- Purpose: Python bytecode cache
- Generated: Yes (Python interpreter)
- Committed: No
- Location: Various in `core/`

**.runtime/:**
- Purpose: Local development process management
- Contains: PID files, log files
- Generated: Yes (dev-up.sh)
- Committed: No

**uploads/reports/:**
- Purpose: Generated analysis reports (when reportOutput=file)
- Generated: Yes (agent execution)
- Committed: No (typically in .gitignore or empty)

## Import Path Patterns

**Backend:**
- Relative imports with `.js` extension for ESM: `import { foo } from './bar.js'`
- Config import: `import { config } from '../config/index.js'`
- Utils import: `import { logger } from '../utils/logger.js'`

**Core:**
- Absolute imports from package root: `from fem.static_analysis import StaticAnalyzer`
- Schema imports: `from schemas.structure_model_v1 import StructureModelV1`
- Converter imports: `from converters.base import FormatConverter`

**Frontend:**
- Path alias `@/`: `import { Button } from '@/components/ui/button'`
- Relative for local: `import { AgentConsole } from './agent-console'`

---

*Structure analysis: 2026-03-09*
