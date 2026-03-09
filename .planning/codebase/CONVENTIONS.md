# Coding Conventions

**Analysis Date:** 2026-03-09

## Language Conventions

**Backend (TypeScript/Node.js):**
- ES modules with `.js` extension in imports (e.g., `import { x } from './utils.js'`)
- TypeScript strict mode enabled
- Type annotations required for all function parameters and returns

**Frontend (TypeScript/React):**
- React functional components with hooks
- `'use client'` directive for client components
- JSX preserved, no emit (Next.js bundler)

**Core (Python):**
- Python 3.11+
- Type hints with `from typing import ...`
- Pydantic models for data validation
- ABC (Abstract Base Classes) for interfaces

## Naming Patterns

**Files:**
- TypeScript: `kebab-case.ts` (e.g., `agent.ts`, `static-analysis.ts`)
- React components: `kebab-case.tsx` (e.g., `agent-console.tsx`, `button.tsx`)
- Python: `snake_case.py` (e.g., `static_analysis.py`, `structure_model_v1.py`)
- Test files: `*.test.mjs` for backend, `*_test.py` for Python

**Functions:**
- TypeScript/JavaScript: `camelCase` (e.g., `createChatModel`, `registerRoutes`)
- Python: `snake_case` (e.g., `get_converter`, `migrate_structure_model_v1`)
- Private methods: `_prefix` in Python (e.g., `_run_with_opensees`)

**Variables:**
- camelCase in TypeScript/JavaScript
- snake_case in Python
- SCREAMING_SNAKE_CASE for module-level constants (e.g., `_CONVERTERS`)

**Types:**
- PascalCase for interfaces, types, classes (e.g., `AgentRunParams`, `StructureModelV1`)
- Type aliases use PascalCase (e.g., `AgentToolName`, `InferredModelType`)

**Components:**
- PascalCase for React components (e.g., `AgentConsole`, `Button`)
- `displayName` assigned for forwardRef components: `Button.displayName = "Button"`

## Code Style

**TypeScript Formatting:**
- Single quotes for strings
- Semicolons required
- 2-space indentation (implied from examples)
- Trailing commas in multiline structures

**Python Formatting:**
- Black formatter (version 24.3.0)
- Double quotes for strings
- 4-space indentation
- Docstrings with triple double quotes

**Linting (Backend):**
- ESLint with `@typescript-eslint` plugin
- Extends: `eslint:recommended`, `plugin:@typescript-eslint/recommended`
- Rule overrides:
  - `@typescript-eslint/no-explicit-any`: `off`
  - `@typescript-eslint/no-unused-vars`: `error` with `argsIgnorePattern: '^_'`

**Linting (Frontend):**
- ESLint with `next/core-web-vitals` preset

## Import Organization

**Backend TypeScript Order:**
1. External packages (e.g., `import Fastify from 'fastify'`)
2. Internal aliases with `@/` or relative paths (e.g., `import { config } from './config/index.js'`)
3. File extension `.js` required in imports for ES modules

**Frontend TypeScript Order:**
1. React/Next.js imports (e.g., `import { useMemo, useState } from 'react'`)
2. External packages (e.g., `import { Button } from '@/components/ui/button'`)
3. Internal aliases using `@/` path alias

**Python Order:**
1. Standard library (e.g., `from typing import Any, Dict, List`)
2. Third-party packages (e.g., `from pydantic import BaseModel`)
3. Local modules (e.g., `from schemas.structure_model_v1 import StructureModelV1`)
4. `from __future__ import annotations` at top when needed

**Path Aliases:**
- Backend: `@/*` maps to `./src/*`
- Frontend: `@/*` maps to `./src/*`

## Error Handling

**Backend Patterns:**
- HTTP errors via Fastify's HTTPException-style patterns
- Zod validation for API request schemas with `.parse()`:
  ```typescript
  const agentRunSchema = z.object({
    message: z.string().min(1).max(10000),
    mode: z.enum(['chat', 'execute', 'auto']).optional(),
  });
  const body = agentRunSchema.parse(request.body);
  ```
- Service methods return structured result objects with `success` boolean
- Error codes as SCREAMING_SNAKE_CASE strings (e.g., `CODE_CHECK_EXECUTION_FAILED`)

**Python Patterns:**
- Pydantic `ValidationError` for model validation
- FastAPI `HTTPException` for API errors:
  ```python
  raise HTTPException(
      status_code=422,
      detail={
          "errorCode": "INVALID_STRUCTURE_MODEL",
          "message": "Input model failed StructureModel v1 validation",
          "errors": e.errors(),
      },
  )
  ```
- Error codes as SCREAMING_SNAKE_CASE strings (e.g., `UNSUPPORTED_TARGET_SCHEMA`)
- Try/except with specific exception types
- Graceful fallbacks (e.g., OpenSeesPy import failure → simplified analysis)

**Frontend Patterns:**
- Try/catch with typed error messages:
  ```typescript
  try {
    const response = await fetch(endpointUrl, { ... })
    // ...
  } catch (error: any) {
    setErrorText(error.message || 'request failed')
  }
  ```
- Result type discrimination via optional chaining

## Logging

**Backend:**
- Pino logger (`pino` + `pino-pretty` in development)
- Log level from `config.logLevel` (default: `info`)
- Development uses pretty-printed, colorized output
- Example from `backend/src/utils/logger.ts`:
  ```typescript
  export const logger = pino({
    level: config.logLevel,
    transport: config.nodeEnv === 'development'
      ? { target: 'pino-pretty', options: { colorize: true, translateTime: 'SYS:standard' } }
      : undefined,
  });
  ```

**Python Core:**
- Standard `logging` module
- Configured with `logging.basicConfig(level=logging.INFO)`
- Module-level loggers: `logger = logging.getLogger(__name__)`

**Frontend:**
- Console for debugging (no structured logging framework)

## Comments

**When to Comment:**
- Chinese comments for business logic explanations (e.g., `// 注册插件`, `# 配置日志`)
- English for technical documentation and docstrings
- JSDoc-style comments for public API endpoints

**Docstrings (Python):**
- Module-level docstrings at file top
- Function docstrings with Args/Returns:
  ```python
  def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
      """
      Execute static analysis

      Args:
          parameters: Analysis parameters

      Returns:
          Analysis results
      """
  ```

**JSDoc/TSDoc:**
- Swagger annotations for API documentation:
  ```typescript
  schema: {
    tags: ['Agent'],
    summary: 'OpenClaw style Agent orchestration entry',
  }
  ```

## Function Design

**Size:** Functions typically under 50 lines, complex services may be longer

**Parameters:**
- Use objects/interfaces for multiple parameters
- Optional parameters via `?:` or `= default`
- Context objects for complex configurations

**Return Values:**
- Services return structured result objects with success/status fields
- API responses follow consistent schema patterns:
  ```typescript
  {
    success: boolean;
    error_code?: string | null;
    message?: string;
    data?: Record<string, unknown>;
    meta?: Record<string, unknown>;
  }
  ```

## Module Design

**Exports:**
- Named exports preferred over default exports
- Service classes exported with their type:
  ```typescript
  export class AgentService { ... }
  export interface AgentRunParams { ... }
  ```

**Barrel Files:**
- Route registration via dedicated modules (e.g., `routes.ts` aggregates route modules)
- Converter registry pattern for extensibility

**Class Design:**
- Constructor for dependency injection and initialization
- Public methods for external API
- Private methods prefixed with `_` in Python

## React Component Patterns

**Component Structure:**
- Functional components with hooks
- Props interface defined alongside component:
  ```typescript
  export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
      VariantProps<typeof buttonVariants> {
    asChild?: boolean
  }
  ```

**Styling:**
- Tailwind CSS with `cn()` utility for class merging
- `class-variance-authority` for variant-based styling
- CSS variables for theming (HSL color system)

**State Management:**
- Zustand for global state
- React Query for server state (`@tanstack/react-query`)
- `useState` for local component state

## API Design Patterns

**Route Registration:**
- Fastify plugin pattern with prefix:
  ```typescript
  await fastify.register(agentRoutes, { prefix: `${apiPrefix}/agent` });
  ```

**Request Validation:**
- Zod schemas for request body validation
- Fastify schema for Swagger documentation

**Response Format:**
- JSON responses with consistent structure
- Error responses include `errorCode` and `message` fields

---

*Convention analysis: 2026-03-09*
