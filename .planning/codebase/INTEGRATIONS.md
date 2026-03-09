# External Integrations

**Analysis Date:** 2026-03-09

## APIs & External Services

**LLM Providers (Multi-provider support):**
- OpenAI - Primary LLM provider
  - SDK: `openai` 4.33.0, `@langchain/openai`
  - Auth: `OPENAI_API_KEY` or `LLM_API_KEY`
  - Config: `LLM_PROVIDER=openai`
  - Default model: `gpt-4-turbo-preview`
  - Default base URL: `https://api.openai.com/v1`

- Zhipu AI (GLM) - Chinese LLM provider
  - SDK: `@langchain/openai` (OpenAI-compatible)
  - Auth: `ZAI_API_KEY` or `LLM_API_KEY`
  - Config: `LLM_PROVIDER=zhipu`
  - Default model: `glm-4-plus`
  - Base URL: `https://open.bigmodel.cn/api/paas/v4/`

- OpenAI-Compatible - Custom endpoints
  - SDK: `@langchain/openai`
  - Auth: `LLM_API_KEY`
  - Config: `LLM_PROVIDER=openai-compatible`
  - Custom: `LLM_BASE_URL` and `LLM_MODEL` required

**Implementation:**
- Chat service: `backend/src/services/chat.ts`
- Agent service: `backend/src/services/agent.ts`
- LLM factory: `backend/src/utils/llm.ts`
- Fallback behavior: Returns error message if no API key configured

## Data Storage

**Databases:**
- PostgreSQL 15
  - Connection: `DATABASE_URL` (e.g., `postgresql://postgres:postgres@localhost:5432/structureclaw`)
  - ORM: Prisma 5.12.0
  - Schema: `backend/prisma/schema.prisma`
  - Client: `@prisma/client` via `backend/src/utils/database.ts`

**File Storage:**
- Local filesystem
  - Upload directory: `./uploads` (configurable via `UPLOAD_DIR`)
  - Max file size: 100MB (configurable via `MAX_FILE_SIZE`)
  - Mounted in Docker: `./uploads:/app/uploads`

**Caching:**
- Redis 7
  - Connection: `REDIS_URL` (can be set to `disabled` for fallback)
  - Client: ioredis 5.3.2
  - Implementation: `backend/src/utils/redis.ts`
  - Fallback: In-memory Map cache when Redis unavailable

## Authentication & Identity

**Auth Provider:**
- Custom JWT-based authentication
  - Library: `@fastify/jwt` 8.0.0
  - Secret: `JWT_SECRET`
  - Expiry: `JWT_EXPIRES_IN` (default: 7d)
  - Password hashing: Stored as `passwordHash` in User model

**User Model:**
- Email/password authentication
- Profile fields: name, avatar, organization, title, bio, expertise
- Schema: `backend/prisma/schema.prisma` - `User` model

## Monitoring & Observability

**Error Tracking:**
- Not detected - no external error tracking service configured

**Logs:**
- Pino logger (structured JSON logging)
  - Implementation: `backend/src/utils/logger.ts`
  - Level: Configurable via `LOG_LEVEL` (default: info)
  - Pretty printing: `pino-pretty` in development

**Health Checks:**
- Backend: `GET /health` - checks database and Redis connectivity
- Analysis Engine: `GET /health` - simple status check
- Frontend: HTTP HEAD check on port 3000

## CI/CD & Deployment

**Hosting:**
- Docker containers via docker-compose
- Services: postgres, redis, backend, analysis-engine, frontend, nginx

**CI Pipeline:**
- GitHub Actions
  - `backend-regression.yml` - Backend contract tests on PR/push
  - `core-regression.yml` - Python analysis engine tests on PR/push
  - Triggers: Pull requests and pushes to master branch
  - Node 20, Python 3.11

**Deployment Commands:**
- `make docker-up` - Full stack deployment
- `make docker-down` - Stop all services
- `make local-up` - Local development with hot reload

## Environment Configuration

**Required env vars:**
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing secret

**Optional env vars:**
- `REDIS_URL` - Redis connection (or `disabled`)
- `LLM_PROVIDER` - LLM provider selection (openai|zhipu|openai-compatible)
- `LLM_API_KEY` - Primary LLM API key
- `LLM_MODEL` - Model name
- `LLM_BASE_URL` - API endpoint URL
- `OPENAI_API_KEY` - OpenAI-specific key (fallback)
- `ZAI_API_KEY` - Zhipu-specific key (fallback)
- `ANALYSIS_ENGINE_URL` - Analysis engine URL (default: http://localhost:8001)
- `CORS_ORIGINS` - Allowed CORS origins
- `UPLOAD_DIR` - File upload directory
- `MAX_FILE_SIZE` - Max upload size in bytes
- `LOG_LEVEL` - Logging verbosity

**Secrets location:**
- `.env` files (not committed, see `.env.example`)
- Docker Compose environment variables

## Internal Service Communication

**Backend to Analysis Engine:**
- Protocol: HTTP REST
- Base URL: `ANALYSIS_ENGINE_URL` (default: http://localhost:8001)
- Client: axios
- Endpoints:
  - `POST /validate` - Validate structure model
  - `POST /convert` - Convert model formats
  - `POST /analyze` - Run analysis (static, dynamic, seismic, nonlinear)
  - `POST /code-check` - Code compliance check
  - `POST /design/beam` - Beam design
  - `POST /design/column` - Column design

**Frontend to Backend:**
- Protocol: HTTP REST
- Base URL: `NEXT_PUBLIC_API_URL` (default: http://localhost:8000)
- Client: axios
- API prefix: `/api/v1`
- Endpoints: `/users`, `/chat`, `/projects`, `/skills`, `/analysis`, `/agent`, `/community`

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Model Format Converters

**Supported Formats:**
- `structuremodel-v1` - Native format (Pydantic schema)
- `compact-v1` - Compact representation
- `simple-v1` - Simplified model format
- `midas-text-v1` - MIDAS Text format import

**Implementation:**
- Registry: `core/converters/registry.py`
- Base class: `core/converters/base.py`
- Converters: `core/converters/*_converter.py`

---

*Integration audit: 2026-03-09*
