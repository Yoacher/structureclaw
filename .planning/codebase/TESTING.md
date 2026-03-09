# Testing Patterns

**Analysis Date:** 2026-03-09

## Test Frameworks

**Backend (Node.js/TypeScript):**
- Jest 29.7.0
- Config: `backend/jest.config.cjs`
- Environment: Node
- Test files: `.test.mjs` extension in `backend/tests/` directory
- No transformation (runs native ES modules)

**Core (Python):**
- pytest 8.1.1
- Test discovery via pytest conventions
- Regression test cases in `core/regression/` directory

**Frontend:**
- No test framework currently configured
- Type-checking only via `npm run type-check`

## Test Configuration

**Backend Jest Config (`backend/jest.config.cjs`):**
```javascript
/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'node',
  testMatch: ['<rootDir>/tests/**/*.test.mjs'],
  transform: {},
};
```

**Run Commands:**
```bash
npm run test --prefix backend        # Run backend tests
npm run lint --prefix backend        # Lint check
npm run type-check --prefix frontend # TypeScript check (frontend)
make backend-regression              # Backend + agent/chat contract regressions
make core-regression                 # Core analysis regression checks
```

## Test File Organization

**Backend:**
- Location: `backend/tests/` directory (separate from source)
- Naming: `*.test.mjs` pattern
- Import compiled JS from `dist/`:
  ```javascript
  import { AgentService } from '../dist/services/agent.js';
  ```

**Core (Python):**
- Regression tests: `core/regression/static_2d/`, `core/regression/static_3d/`
- Test case files: JSON fixtures named `case_XX_*.json`
- No dedicated `test_*.py` files detected in core (uses pytest fixtures/regression)

**Frontend:**
- No test files currently present

## Test Structure

**Backend Test Pattern (from `agent.service.test.mjs`):**
```javascript
import { describe, expect, test } from '@jest/globals';
import fs from 'node:fs';
import { AgentService } from '../dist/services/agent.js';

describe('AgentService orchestration', () => {
  test('should execute analyze -> code-check -> report closed loop', async () => {
    const svc = new AgentService();
    // Mock setup
    svc.llm = null;
    svc.engineClient.post = async (path, payload) => {
      if (path === '/validate') {
        return { data: { valid: true, schemaVersion: '1.0.0' } };
      }
      // ... more mock responses
      throw new Error(`unexpected path ${path}`);
    };

    const result = await svc.run({
      message: '...',
      mode: 'execute',
      context: { /* ... */ },
    });

    expect(result.success).toBe(true);
    expect(result.toolCalls.some((c) => c.tool === 'analyze')).toBe(true);
  });
});
```

**Patterns:**
- Jest globals imported from `@jest/globals`
- `describe`/`test` blocks for organization
- Async tests with `async/await`
- Mocking via direct property assignment on service instances
- File system assertions for artifact generation

## Mocking

**Backend Mocking Pattern:**
- Direct property assignment on service instances:
  ```javascript
  const svc = new AgentService();
  svc.llm = null;  // Disable LLM for unit testing
  svc.engineClient.post = async (path, payload) => {
    // Mock implementation returning fixture data
    if (path === '/analyze') {
      return { data: { success: true, ... } };
    }
  };
  ```

**What to Mock:**
- External HTTP clients (`engineClient.post`)
- LLM/chat models (`svc.llm = null`)
- Database connections (via dependency injection)

**What NOT to Mock:**
- Internal business logic
- Data transformations
- Schema validation (test real behavior)

## Fixtures and Factories

**Test Data:**
- Inline JSON objects for model payloads:
  ```javascript
  const result = await svc.run({
    message: '...',
    context: {
      model: {
        schema_version: '1.0.0',
        nodes: [{ id: '1', x: 0, y: 0, z: 0 }, ...],
        elements: [{ id: 'E1', type: 'beam', nodes: ['1', '2'], ... }],
        // ...
      },
    },
  });
  ```

**Regression Test Fixtures (Core):**
- Location: `core/regression/static_2d/`, `core/regression/static_3d/`
- Named test cases: `case_01_sym_v_truss.json`, `case_02_single_bar_axial.json`, etc.
- JSON format following StructureModel v1 schema

**Core Regression Cases:**
```
case_01_sym_v_truss.json
case_02_single_bar_axial.json
case_03_frame_cantilever_tip_load.json
case_04_frame_cantilever_udl.json
case_05_truss_load_combination.json
case_06_frame_two_element_cantilever_tip_load.json
case_07_frame_cantilever_udl_long.json
case_08_truss_batch_cases_envelope.json
case_09_frame_batch_cases_controls.json
case_10_batch_envelope_tables.json
```

## Coverage

**Requirements:** None explicitly enforced in configuration

**Coverage Commands:**
- No coverage flags in current test commands
- Jest supports `--coverage` flag if needed

## Test Types

**Unit Tests (Backend):**
- Service method testing with mocked dependencies
- Focus on business logic and orchestration
- Example: `agent.service.test.mjs` tests AgentService.run() behavior

**Integration Tests:**
- Regression scripts via Makefile targets:
  - `make backend-regression` - Backend + agent/chat contract tests
  - `make core-regression` - Core analysis engine contract tests
- Contract testing for API endpoints

**E2E Tests:**
- Not currently configured
- Frontend console page (`/console`) used for manual integration testing

## Common Patterns

**Async Testing:**
```javascript
test('should execute closed loop', async () => {
  const result = await svc.run({ ... });
  expect(result.success).toBe(true);
});
```

**Error Testing:**
```javascript
test('should fail when code-check fails', async () => {
  const svc = new AgentService();
  svc.engineClient.post = async (path, payload) => {
    if (path === '/code-check') {
      const error = new Error('code check failed');
      error.response = { data: { errorCode: 'CODE_CHECK_EXECUTION_FAILED' } };
      throw error;
    }
  };

  const result = await svc.run({ ... });
  expect(result.success).toBe(false);
  expect(codeCheckCall?.errorCode).toBe('CODE_CHECK_EXECUTION_FAILED');
});
```

**File System Assertions:**
```javascript
test('should export report artifacts to files', async () => {
  // ... setup and execution

  expect(Array.isArray(result.artifacts)).toBe(true);
  for (const artifact of result.artifacts) {
    expect(fs.existsSync(artifact.path)).toBe(true);
    fs.unlinkSync(artifact.path);  // Cleanup
  }
});
```

**Multiple Assertions per Test:**
- Tests verify multiple aspects of results
- Check success flag, tool call presence, specific field values

## Running Tests

**Backend:**
```bash
cd backend
npm test                              # Run all tests
npm test -- --testNamePattern="..."   # Run specific tests
NODE_OPTIONS=--experimental-vm-modules npm test  # Full command (from package.json)
```

**Core:**
```bash
make core-regression  # Run regression suite via script
```

**Full Suite:**
```bash
make backend-regression  # Backend contract tests
make core-regression     # Core engine tests
```

## Test Data Patterns

**Model Fixtures:**
- Follow StructureModel v1 schema
- Minimal viable model for test case:
  ```javascript
  {
    schema_version: '1.0.0',
    nodes: [{ id: '1', x: 0, y: 0, z: 0 }, { id: '2', x: 3, y: 0, z: 0 }],
    elements: [{ id: 'E1', type: 'beam', nodes: ['1', '2'], material: '1', section: '1' }],
    materials: [{ id: '1', name: 'steel', E: 205000, nu: 0.3, rho: 7850 }],
    sections: [{ id: '1', name: 'B1', type: 'beam', properties: { A: 0.01, Iy: 0.0001 } }],
    load_cases: [],
    load_combinations: [],
  }
  ```

**Response Fixtures:**
- Mock API responses match real API schema:
  ```javascript
  {
    data: {
      schema_version: '1.0.0',
      analysis_type: 'static',
      success: true,
      error_code: null,
      message: 'ok',
      data: {},
      meta: {},
    }
  }
  ```

## Testing Best Practices (Observed)

1. **Test real behavior, not implementation details** - Mock external services, not internal logic
2. **Use descriptive test names** - "should execute analyze -> code-check -> report closed loop"
3. **Test both success and failure paths** - Happy path and error scenarios
4. **Cleanup side effects** - Remove generated files after tests
5. **Contract testing** - Regression tests verify API contracts remain stable

## Gaps and Recommendations

**Missing Test Coverage:**
- Frontend has no test framework configured
- No unit tests for Python core modules (only regression fixtures)
- No E2E testing infrastructure

**Potential Additions:**
- Vitest for frontend (aligned with Vite/Next.js)
- pytest files for Python unit tests
- Playwright or Cypress for E2E

---

*Testing analysis: 2026-03-09*
