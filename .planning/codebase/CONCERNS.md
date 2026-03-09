# Codebase Concerns

**Analysis Date:** 2026-03-09

## Tech Debt

**Large Monolithic Agent Service:**
- Issue: `backend/src/services/agent.ts` is 1599 lines with 10 async functions in a single class
- Files: `/home/guyi/structureclaw/backend/src/services/agent.ts`
- Impact: Difficult to maintain, test, and understand. High cognitive load for developers
- Fix approach: Extract into separate services (DraftService, ConvertService, AnalyzeService, CodeCheckService, ReportService) following single responsibility principle

**Loose Typing Throughout Backend:**
- Issue: Extensive use of `any`, `unknown`, and `Record<string, unknown>` types reducing type safety
- Files: `/home/guyi/structureclaw/backend/src/services/agent.ts`, `/home/guyi/structureclaw/backend/src/services/analysis.ts`
- Impact: Type errors only caught at runtime instead of compile time
- Fix approach: Define strict TypeScript interfaces for all data structures, especially model schemas, analysis parameters, and tool results

**Python Core Uses Loose Typing:**
- Issue: 120+ uses of `Any` type hints across core Python modules
- Files: `/home/guyi/structureclaw/core/fem/static_analysis.py`, `/home/guyi/structureclaw/core/main.py`
- Impact: Reduced code clarity and IDE support, potential runtime errors
- Fix approach: Define Pydantic models or TypedDict for structured data, use specific types instead of `Any`

## Known Bugs

**Bare Except Clauses in Core Analysis:**
- Issue: Silent failure with bare `except:` clauses catching all exceptions including KeyboardInterrupt
- Files: `/home/guyi/structureclaw/core/fem/static_analysis.py:131`, `/home/guyi/structureclaw/core/fem/dynamic_analysis.py:122`
- Trigger: Any exception during element force extraction silently ignored
- Workaround: None - forces dict may be incomplete without any indication

**Fallback to Zero Results When All Solvers Fail:**
- Issue: Analysis returns empty results when all solver fallbacks fail
- Files: `/home/guyi/structureclaw/core/fem/static_analysis.py:1392`
- Trigger: Invalid model parameters or unsupported structure types
- Workaround: Validate model before analysis

## Security Considerations

**Weak Password Hashing:**
- Risk: SHA256 is not a password hashing function - vulnerable to rainbow table attacks
- Files: `/home/guyi/structureclaw/backend/src/utils/demo-data.ts:6-8`
- Current mitigation: Only used for demo user in development
- Recommendations: Use bcrypt or argon2 for password hashing (10-12 rounds minimum)

**Default JWT Secret:**
- Risk: Default JWT secret in code could be used in production if env var not set
- Files: `/home/guyi/structureclaw/backend/src/config/index.ts:33`
- Current mitigation: Warning comment, but no enforcement
- Recommendations: Throw error on startup if JWT_SECRET not set in production environment

**Overly Permissive CORS in Core:**
- Risk: Core API allows all origins with `allow_origins=["*"]`
- Files: `/home/guyi/structureclaw/core/main.py:40`
- Current mitigation: Core runs on port 8001, typically not exposed publicly
- Recommendations: Restrict to specific origins in production, read from environment variable

**Hardcoded Demo Credentials:**
- Risk: Demo user with known password `demo-password` exists in database
- Files: `/home/guyi/structureclaw/backend/src/utils/demo-data.ts:16`
- Current mitigation: Only created in development environments
- Recommendations: Ensure demo user creation is disabled in production builds

## Performance Bottlenecks

**Large Static Analysis File:**
- Problem: `static_analysis.py` is 1408 lines with multiple fallback solver implementations
- Files: `/home/guyi/structureclaw/core/fem/static_analysis.py`
- Cause: Contains OpenSees, 2D frame, 3D frame, 3D truss solvers all in one file
- Improvement path: Extract each solver into separate modules, use strategy pattern

**Redis Caching Without Invalidation Strategy:**
- Problem: Model data cached for 1 hour with no invalidation on updates
- Files: `/home/guyi/structureclaw/backend/src/services/analysis.ts:49-53`
- Cause: No cache invalidation when model is updated or deleted
- Improvement path: Implement cache invalidation in update/delete operations

**Synchronous LLM Calls in Agent Service:**
- Problem: LLM calls block the event loop during model drafting
- Files: `/home/guyi/structureclaw/backend/src/services/agent.ts`
- Cause: Direct await of LLM responses without streaming or queueing
- Improvement path: Implement request queuing or streaming for long-running LLM operations

## Fragile Areas

**Agent Tool Orchestration:**
- Files: `/home/guyi/structureclaw/backend/src/services/agent.ts`
- Why fragile: Complex state machine managing text-to-model-draft, convert, validate, analyze, code-check, report tools
- Safe modification: Add new tools through the existing tool registration pattern
- Test coverage: Integration tests exist in `backend/tests/agent.service.test.mjs` but only cover happy paths

**Model Conversion Pipeline:**
- Files: `/home/guyi/structureclaw/core/converters/midas_text_v1_converter.py`, `/home/guyi/structureclaw/core/converters/registry.py`
- Why fragile: Multiple converter implementations with different error handling patterns
- Safe modification: Add new converters implementing the BaseConverter interface
- Test coverage: Regression scripts in `scripts/validate-*.sh` but no unit tests

**Static Analysis Fallback Chain:**
- Files: `/home/guyi/structureclaw/core/fem/static_analysis.py:146-182`
- Why fragile: Multiple fallback paths with inconsistent error handling
- Safe modification: Add new solvers at the end of fallback chain
- Test coverage: Regression scripts exist but edge cases not covered

## Scaling Limits

**Redis Connection Pool:**
- Current capacity: Single Redis connection
- Limit: Will bottleneck under high concurrent load
- Scaling path: Implement connection pooling with ioredis built-in pool

**PostgreSQL JSON Storage:**
- Current capacity: Structural models stored as JSON in PostgreSQL
- Limit: Large models (>10k elements) will cause slow queries
- Scaling path: Consider separate document store or partition JSON fields

**No Request Rate Limiting:**
- Current capacity: No rate limiting on API endpoints
- Limit: Vulnerable to DoS attacks and resource exhaustion
- Scaling path: Implement rate limiting middleware (fastify-rate-limit)

**LLM API Timeout:**
- Current capacity: 20 second timeout configured
- Limit: Complex models may timeout during drafting
- Scaling path: Implement retry logic with exponential backoff, increase timeout for batch operations

## Dependencies at Risk

**OpenSeesPy:**
- Risk: Heavy dependency (3.5.1.6) - may not be available on all systems
- Impact: Core analysis falls back to simplified solvers with reduced accuracy
- Migration plan: Ensure fallback solvers are well-tested, document OpenSeesPy as optional

**LangChain:**
- Risk: Fast-moving dependency with breaking changes
- Impact: LLM integration could break between versions
- Migration plan: Pin version in requirements, test before upgrades

**Multiple FEA Libraries:**
- Risk: Both openseespy, pynite, and ananstruct listed as dependencies
- Impact: Increased bundle size, potential conflicts
- Migration plan: Evaluate and consolidate to primary solver library

## Missing Critical Features

**No Authentication on Core API:**
- Problem: Core analysis engine has no authentication
- Blocks: Secure production deployment

**No Request Validation in Core:**
- Problem: Only Pydantic validation on request models, no business logic validation
- Blocks: Catching invalid model configurations before expensive analysis

**No Analysis Job Queue:**
- Problem: Analyses run synchronously
- Blocks: Handling long-running analyses without blocking HTTP requests

## Test Coverage Gaps

**Core Python Modules:**
- What's not tested: Unit tests for individual analyzer methods
- Files: `/home/guyi/structureclaw/core/fem/*.py`, `/home/guyi/structureclaw/core/design/*.py`
- Risk: Solver logic changes could break analysis without detection
- Priority: High

**Frontend Components:**
- What's not tested: No test files found for React components
- Files: `/home/guyi/structureclaw/frontend/src/**/*.tsx`
- Risk: UI regressions during updates
- Priority: Medium

**Error Paths in Agent Service:**
- What's not tested: Error handling when tools fail
- Files: `/home/guyi/structureclaw/backend/tests/agent.service.test.mjs`
- Risk: Only one error scenario tested (code-check failure)
- Priority: High

**Converter Edge Cases:**
- What's not tested: Invalid input handling in converters
- Files: `/home/guyi/structureclaw/core/converters/*.py`
- Risk: Malformed input could cause unhandled exceptions
- Priority: Medium

---

*Concerns audit: 2026-03-09*
