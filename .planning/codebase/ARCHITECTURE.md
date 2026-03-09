# Architecture

**Analysis Date:** 2026-03-09

## Pattern Overview

**Overall:** Multi-tier microservices with LLM-driven agent orchestration

**Key Characteristics:**
- Three-tier separation: Frontend (Next.js) -> Backend API (Fastify) -> Core Engine (FastAPI/Python)
- Agent-based workflow orchestration with tool chain execution
- Domain-driven structure within each service layer
- Graceful degradation patterns (Redis -> memory cache, OpenSeesPy -> simplified analysis)
- Polyglot architecture: TypeScript backend, Python analysis engine

## Layers

**Frontend Layer:**
- Purpose: Web UI for structural engineering AI console
- Location: `frontend/`
- Contains: React components, pages, API client code
- Depends on: Backend API via HTTP
- Used by: End users through browser

**Backend API Layer:**
- Purpose: Business logic, authentication, agent orchestration, data persistence
- Location: `backend/src/`
- Contains: API routes, services, utilities, configuration
- Depends on: PostgreSQL, Redis, Core Engine, LLM providers
- Used by: Frontend, external clients

**Core Analysis Engine Layer:**
- Purpose: Finite element analysis, code checking, structural design calculations
- Location: `core/`
- Contains: FEM analyzers, design modules, converters, schemas
- Depends on: OpenSeesPy, NumPy, SciPy (optional, with fallbacks)
- Used by: Backend via HTTP

**Infrastructure Layer:**
- Purpose: Data persistence, caching, orchestration
- Location: `docker/`, `docker-compose.yml`
- Contains: PostgreSQL database, Redis cache, Nginx reverse proxy
- Depends on: Docker runtime
- Used by: All application services

## Data Flow

**Agent Execution Flow:**

1. User sends message via Frontend console (`/console`)
2. Frontend POSTs to Backend `/api/v1/agent/run` or `/api/v1/chat/execute`
3. Backend AgentService determines execution mode (chat/execute/auto)
4. If execute mode, AgentService runs tool chain: `text-to-model-draft -> convert -> validate -> analyze -> code-check -> report`
5. Each tool calls Core Engine HTTP endpoints (`/validate`, `/analyze`, `/code-check`)
6. Results aggregated with metrics (traceId, durationMs, toolCalls)
7. Response returned to Frontend with structured result

**Chat Flow:**

1. User sends message to `/api/v1/chat/message` or `/api/v1/chat/stream`
2. ChatService uses LangChain with conversation memory
3. LLM (OpenAI/Zhipu) generates response with structural engineering context
4. Messages persisted to PostgreSQL via Prisma
5. Response returned (streaming or complete)

**State Management:**
- Conversations: PostgreSQL `conversations` and `messages` tables
- Draft states: In-memory Map in AgentService keyed by conversationId
- Session memory: LangChain BufferMemory per conversation
- Cache: Redis with fallback to in-memory Map

## Key Abstractions

**StructureModelV1:**
- Purpose: Canonical data model for structural analysis models
- Examples: `core/schemas/structure_model_v1.py`
- Pattern: Pydantic model with validation (nodes, elements, materials, sections, load cases)

**FormatConverter:**
- Purpose: Transform between different structural model formats
- Examples: `core/converters/base.py`, `core/converters/simple_v1_converter.py`
- Pattern: Abstract base class with `to_v1()` and `from_v1()` methods

**AgentTool:**
- Purpose: Encapsulate executable operations in the agent workflow
- Examples: `backend/src/services/agent.ts` (text-to-model-draft, convert, validate, analyze, code-check, report)
- Pattern: Sequential execution with metrics collection

**Service Classes:**
- Purpose: Encapsulate business logic per domain
- Examples: `backend/src/services/agent.ts`, `backend/src/services/chat.ts`, `backend/src/services/project.ts`
- Pattern: Class-based services with injected dependencies (Prisma, Redis, LLM)

## Entry Points

**Backend API Server:**
- Location: `backend/src/index.ts`
- Triggers: `npm run dev` or `npm start`
- Responsibilities: Fastify server initialization, plugin registration, route mounting, health checks, graceful shutdown

**Core Analysis Engine:**
- Location: `core/main.py`
- Triggers: `uvicorn main:app` or `make dev-core-lite`
- Responsibilities: FastAPI app with endpoints for validate, convert, analyze, code-check, design

**Frontend Dev Server:**
- Location: `frontend/src/app/layout.tsx` (root layout)
- Triggers: `npm run dev` in frontend directory
- Responsibilities: Next.js app rendering, React Query provider setup

**CLI Entry:**
- Location: `sclaw` (shell script at project root)
- Triggers: `./sclaw <command>` or `sclaw <command>` after global install
- Responsibilities: Orchestrates local development (start, stop, status, logs)

## Error Handling

**Strategy:** Multi-layer with graceful degradation

**Patterns:**
- Backend: HTTP errors via Fastify with structured JSON responses (errorCode, message)
- Core Engine: HTTPException with detailed validation errors, try/catch with AnalysisResponse containing success flag
- LLM: Null-safe initialization with fallback messages when API key missing
- Analysis: ImportError catch with simplified calculation fallback when OpenSeesPy unavailable
- Redis: Connection failure silently falls back to in-memory Map cache

## Cross-Cutting Concerns

**Logging:**
- Backend: Pino logger with configurable log level
- Core: Python logging module with INFO level

**Validation:**
- Backend: Zod for request schemas
- Core: Pydantic models with model validators for cross-reference integrity

**Authentication:**
- Approach: JWT-based (Fastify JWT plugin)
- Configuration: JWT_SECRET from environment

**Configuration:**
- Centralized config module: `backend/src/config/index.ts`
- Environment-driven with sensible defaults
- Supports multiple LLM providers (OpenAI, Zhipu, OpenAI-compatible)

---

*Architecture analysis: 2026-03-09*
