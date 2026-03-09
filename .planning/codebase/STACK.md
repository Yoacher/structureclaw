# Technology Stack

**Analysis Date:** 2026-03-09

## Languages

**Primary:**
- TypeScript 5.4.3 - Backend service (`backend/`) and frontend (`frontend/`)
- Python 3.11 - Analysis engine (`core/`)

**Secondary:**
- Shell/Bash - CLI scripts and deployment automation (`scripts/`, `sclaw`)

## Runtime

**Environment:**
- Node.js 20.x - Backend API and frontend build
- Python 3.11 - Analysis engine with uvicorn

**Package Manager:**
- npm - Node.js dependency management
  - Lockfile: `backend/package-lock.json`, `frontend/package-lock.json`
- pip - Python dependency management
  - Requirements: `core/requirements.txt`, `core/requirements-lite.txt`
- uv (optional) - Fast Python package manager for local development

## Frameworks

**Core:**
- Fastify 4.26.2 - Backend HTTP API framework
- Next.js 14.1.4 - Frontend React framework with SSR
- FastAPI 0.110.1 - Python analysis engine HTTP API
- React 18.2.0 - Frontend UI library

**Testing:**
- Jest 29.7.0 - Backend unit/integration tests
- Pytest 8.1.1 - Python analysis engine tests

**Build/Dev:**
- TypeScript 5.4.3 - Type checking and compilation
- tsx 4.7.1 - TypeScript execution for development
- Tailwind CSS 3.4.3 - Frontend styling
- SWC - Next.js built-in minification

## Key Dependencies

**Backend (`backend/package.json`):**
- `@prisma/client` 5.12.0 - Database ORM
- `@fastify/cors` 9.0.1 - CORS middleware
- `@fastify/jwt` 8.0.0 - JWT authentication
- `@fastify/swagger` 8.14.0 - API documentation
- `@langchain/openai` - LLM integration for chat/agent features
- `langchain` 0.1.36 - LLM orchestration
- `openai` 4.33.0 - OpenAI API client
- `ioredis` 5.3.2 - Redis client
- `axios` 1.6.8 - HTTP client
- `zod` 3.22.4 - Runtime validation
- `pino` 8.19.0 - Logging
- `uuid` 9.0.1 - UUID generation

**Frontend (`frontend/package.json`):**
- `@react-three/fiber` 8.15.16 - 3D rendering
- `@react-three/drei` 9.99.7 - 3D helpers
- `three` 0.163.0 - WebGL 3D library
- `@tanstack/react-query` 5.28.4 - Data fetching
- `zustand` 4.5.2 - State management
- `axios` 1.6.8 - HTTP client
- `lucide-react` 0.363.0 - Icon library
- `react-markdown` 9.0.1 - Markdown rendering
- `tailwind-merge` 3.5.0 - CSS class merging
- `class-variance-authority` 0.7.1 - Component variants
- `date-fns` 3.6.0 - Date utilities

**Analysis Engine (`core/requirements.txt`):**
- `openseespy` 3.5.1.6 - OpenSees finite element analysis
- `numpy` 1.26.4 - Numerical computing
- `scipy` 1.12.0 - Scientific computing
- `pynite` 0.0.84 - Finite element analysis
- `ananstruct` 1.1.0 - Structural analysis
- `pandas` 2.2.1 - Data manipulation
- `matplotlib` 3.8.4 - Plotting
- `plotly` 5.20.0 - Interactive visualization
- `pydantic` 2.6.4 - Data validation
- `sqlalchemy` 2.0.29 - SQL toolkit
- `asyncpg` 0.29.0 - Async PostgreSQL
- `httpx` 0.27.0 - Async HTTP client
- `redis` 5.0.3 - Redis client

**Lite Dependencies (`core/requirements-lite.txt`):**
For local development without heavy FEA toolchains:
- `fastapi`, `uvicorn`, `pydantic`, `numpy`, `httpx`, `redis`

## Configuration

**Environment:**
- dotenv-based configuration
- Environment files: `.env`, `.env.example`
- Backend config: `backend/src/config/index.ts`
- Frontend config: `frontend/next.config.js`

**Build:**
- `tsconfig.json` - TypeScript configuration (both backend and frontend)
- `jest.config.cjs` - Jest test configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `prisma/schema.prisma` - Database schema

**Docker:**
- `docker-compose.yml` - Full stack orchestration
- `backend/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container
- `core/Dockerfile` - Analysis engine container
- `docker/nginx/` - Nginx reverse proxy configuration

## Platform Requirements

**Development:**
- Node.js 18+ (Node 20 recommended)
- Python 3.11
- Docker and Docker Compose (for infrastructure services)
- PostgreSQL 15 (via Docker or local)
- Redis 7 (via Docker or local)

**Production:**
- Docker containers orchestrated via docker-compose
- PostgreSQL 15 Alpine
- Redis 7 Alpine
- Nginx reverse proxy for SSL termination and routing

---

*Stack analysis: 2026-03-09*
