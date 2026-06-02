---
name: ddd
description: "Analyze code structure, domain logic placement, and REST API design. Use when code quality or architectural nesting issues occur."
when_to_use: "Use when user asks about business logic placement, naming, transparency, function complexity, or REST endpoint modeling."
---

## Routing Guidance

- ARCHITECTURE: 'where does business logic go', 'too much nesting', 'too many parameters', 'function does too much', 'business logic in controllers'
- QUALITY: 'what should I name this', 'should I use a library', 'silent failure'
- TRANSPARENCY: 'hidden side effect', 'does this return or mutate', 'is this a side effect', 'mutation disguised as query'
- API: 'design REST API', 'API endpoint design', 'HTTP semantics', 'API versioning'

## Relationship to kaizen

ddd and kaizen are complementary, not redundant. They operate at different layers of the same concern (preventing bad code from entering the codebase).

**ddd** is a detailed analysis methodology with 4 modes (ARCHITECTURE, QUALITY, TRANSPARENCY, API) invoked when a specific structural question surfaces. It produces a written analysis, may spawn subagents (codebase scanner, endpoint auditor), and is selected per mode based on the question at hand.

**kaizen** is a lightweight 4-pillar filter applied to every code decision. It runs continuously in the background as guardrails — a developer does not "invoke" kaizen, they apply it as they write. No artifact, no analysis mode, no spawned subagent. The output is shaped code, not a written report.

**When to use which:**

- "Where should this business logic live?", "function does too much", "is this side effect visible?", "design a REST endpoint" → ddd (select the matching mode for deep analysis)
- Routine implementation, refactoring, or design decision → kaizen (apply the 4 pillars as guardrails)
- Both at once → apply kaizen constraints while ddd analyzes structure; they do not conflict

**Conceptual layering:** kaizen is the immune system (always on, lightweight, prevents infection); ddd is the specialist (called in for specific diagnoses, produces a treatment plan).

## Decision Router

IF code structure or layering issue → ARCHITECTURE mode — ALWAYS spawn a **`tp-explorer`** subagent to map structure
IF naming or error handling issue → QUALITY mode
IF behavior visibility or data flow issue → TRANSPARENCY mode
IF REST API contract design, resource modeling, or versioning issue → API mode — ALWAYS spawn a **`tp-endpoint-auditor`** subagent to review contracts

---

# Mode: ARCHITECTURE

Structure code for maintainability with four principles: layered architecture, functional core, early returns, function size limits.

**ALWAYS spawn a `tp-explorer` subagent to map structure and identify layering violations.** The explorer should:
- Map current module dependencies and layering
- Identify business logic leaks into framework/infrastructure adapters
- Detect deep nesting (>3 levels) and oversized functions (>80 lines)
- Report on file size distribution (>200 lines)

## Layered Architecture

Keep business logic in pure domain and use case layers, free of framework or infrastructure dependencies. When domain logic is coupled to controllers, ORMs, or HTTP libraries, it becomes untestable and unreusable.

**Q: Where do I put this code?**
- Business rule/calculation needing no I/O → **pure function** in domain layer
- Orchestration of multiple steps → **use case/service** delegating to interfaces
- HTTP/event handling → **controller/adapter** delegating to use cases
- Data persistence → **repository** implementing domain interface
- Side effects (email, logging, external APIs) → **imperative shell** at composition root

## Functional Core, Imperative Shell

Keep business logic in pure functions (inputs → outputs, no side effects). Push all I/O — database calls, HTTP requests, logging, file I/O — to an outer imperative shell.

Pure functions are deterministic and trivially testable without mocks.

**Why:** Business logic tangled with logging, database reads, and persistence requires mocking everything to test. Pure core + imperative shell = testable domain.

## Early Returns

Handle error conditions and edge cases at the top of functions instead of nested conditionals. Keeps happy path at the top level, reducing cognitive load.

**Rule:** Never nest more than 3 levels. Use guard clauses for all error conditions.

## Function Size Limits

Decompose functions longer than 80 lines into smaller, focused functions of 50 lines or fewer. Keep files under 200 lines.

**Rule:** If a function grows beyond 80 lines, it is doing more than one thing. Extract by responsibility.

---

# Mode: QUALITY

Apply idiom checks: domain-specific naming, library-first approach, visible error handling.

## Domain Naming

Avoid generic names: `utils`, `helpers`, `common`, `shared`. Use domain-specific names reflecting bounded context: `OrderCalculator`, `UserAuthenticator`, `InvoiceGenerator`.

**Rule:** Name by behavior, not category. A module named `order-pricing.ts` can only do one thing by design. A module named `utils.ts` attracts everything.

## Library First

Search for existing battle-tested libraries before writing custom code. Every line of custom code is a liability requiring maintenance, testing, and documentation.

**Custom code only justified when:**
- Specific business logic unique to domain
- Performance-critical paths with special requirements
- External dependencies would be overkill
- Security-sensitive code requiring full control
- Existing solutions don't meet requirements after thorough evaluation

**NIH anti-patterns:** Custom auth when Auth0 exists, custom state when Redux/Zustand exist, custom validation when Zod handles it, custom retry logic when Cockatiel provides proven solutions.

## Visible Errors

Never silently swallow exceptions. Every catch block needs typed error handling and logging before rethrowing.

**Rule:** Generic `catch (e)` blocks hide root cause. Use typed catch blocks distinguishing domain errors from system failures.

---

# Mode: TRANSPARENCY

Ensure code reveals its behavior at the call site.

## Four Principles

1. **Visible Side Effects** — Side effects (persistence, notifications, external calls) must be visible at call site, not hidden in implementation.

2. **Data Flow Through Return Values** — Data flows through return values so reader can trace where each value came from. Never rely on mutation of input parameters.

3. **Explicit Control Flow** — Error conditions and branching visible at call site. Policy (what to do) stays at call site; mechanism (pure computation) can be extracted.

4. **Command-Query Separation** — A function must either return a value (query) or cause a side effect (command), never both.

## Command-Query Separation

```typescript
// WRONG: mutation disguised as query
const result = {}
if (featureEnabled)
  applyNewFeature(result)  // mutates in-place

// WRONG: hidden throw at call site
const result = performProcess(param)
validateResult(result)  // throws — caller sees no branching

// RIGHT: return value directly
const result = featureEnabled ? applyNewFeature(baseData) : {}

// RIGHT: explicit control flow
const result = performProcess(param)
if (!isValid(result))
  throw new ProcessingError(result)
```

## Anti-Patterns to Avoid

| Pattern | Problem | Fix |
|---------|---------|-----|
| `const x = compute()` then `compute()` again | Mutation disguised as command | Return value, assign once |
| `let x = {}; mutate(x)` | Mutation hidden behind assignment | Return new value, use const |
| `validate(x)` without return check | Hidden throw at call site | Return boolean, explicit if |
| `process(order)` as single opaque call | Side effects hidden in implementation | Expand at call site |
| `if (x) transform(x)` unclear if x mutated | Data flow opaque | Return new value, assign to new name |

---

# Mode: API

Design REST API contracts with proper resource modeling, HTTP semantics, and versioning strategies.

**ALWAYS spawn a `tp-endpoint-auditor` subagent to review contracts.** The auditor should:
- Validate URL noun/verb usage and hierarchy
- Verify HTTP method semantics (GET=safe, PUT=idempotent, etc.)
- Check status code mappings for success and error paths
- Detect potential breaking changes and recommend versioning strategies
- Ensure consistent error response shapes

## When to Use

- Designing new REST endpoints
- Evaluating API contract quality
- Versioning decisions
- Breaking change analysis

## Resource Modeling

Design URLs as nouns representing resources, not verbs representing operations.

**Rules:**
- Use nouns, not verbs: `/users` not `getUsers` or `createUser`
- Proper hierarchy: `/users/{id}/posts` for nested resources
- Idempotency where appropriate: `PUT /users/{id}` for updates
- Avoid deep nesting: flatten when nesting exceeds 2 levels

**Examples:**
```
/users              GET (list), POST (create)
/users/{id}         GET, PUT, DELETE
/users/{id}/posts   GET (user's posts)
/posts/{id}/author GET (single relation)
```

## HTTP Semantics

Match HTTP methods to their semantic meaning.

| Method | Semantics | Idempotent | Safe |
|--------|-----------|------------|------|
| GET | Read resource | Yes | Yes |
| POST | Create new resource | No | No |
| PUT | Full replace | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

**Status Code Rules:**
- 2xx: Success (200 OK, 201 Created, 204 No Content)
- 4xx: Client error (400 Bad Request, 404 Not Found, 409 Conflict)
- 5xx: Server error (500 Internal Server Error)

Never return 200 with an error body. Never return 404 with a 2xx status.

## Breaking Changes

A breaking change requires a version bump.

**Breaking changes:**
- Removing or renaming fields in response
- Changing field types
- Adding required request fields
- Changing URL structure
- Removing endpoints
- Changing error response format

**Non-breaking changes:**
- Adding optional request fields
- Adding new fields to response
- Adding new endpoints

## Versioning Strategies

**URL versioning** (explicit, cache-friendly):
```
/v1/users
/v2/users
```
Simple but pollutes URL space.

**Header versioning** (clean URLs, requires client awareness):
```
Accept: application/vnd.api+json;version=1
```
URLs stay clean; clients control version via headers.

**Deprecation pattern:**
```
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

## Response Shapes

**Error format consistency:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [{ "field": "email", "issue": "invalid format" }]
  }
}
```

**Pagination patterns:**
```json
{
  "data": [...],
  "pagination": {
    "cursor": "abc123",
    "hasMore": true
  }
}
```

## Anti-Patterns

- Verb-based endpoints: `POST /createUser`, `GET /getUserById`
- Status code misuse: 200 OK with error body, 404 with 2xx
- Inconsistent error format across endpoints
- Breaking changes without version bump
- PUT without idempotency guarantees
- GET with side effects (logging is OK; persistence is not)

## Cross-Reference

**Contrast with refine REVIEW mode:** The refine skill's REVIEW mode covers contract testing (verifying mocks match actual APIs). This API mode covers contract design (shaping the contract itself). Use refine for validation; use this skill for design.

---

## Unified Example

All four principles working together:

```typescript
// Query: pure, returns, no mutation
function calculatePrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

// Query: pure, returns, no mutation
function applyDiscount(price: number, code: string): number {
  return code === "SAVE20" ? price * 0.8 : price
}

// Policy visible at call site
const price = calculatePrice(order.items)
const discounted = applyDiscount(price, order.couponCode)
if (discounted > 1_000_000)
  throw new ValidationError("Price exceeds limit")

// Commands: side effects visible
await db.save({ orderId: order.id, total: discounted })
await paymentGateway.charge(order.customerId, discounted)
```

---

## Quality Checklist

- [ ] Module names reflect behavior, not generic categories
- [ ] No `utils`, `helpers`, `common`, or `shared` files
- [ ] No utility/helper functions duplicating library functionality
- [ ] Every catch block has typed handling and logging
- [ ] No silent swallowing of exceptions
- [ ] Side effects visible at call site
- [ ] Data flows through return values, not mutation
- [ ] Control flow explicit, no hidden throws

### API Checklist

- [ ] Endpoints use nouns, not verbs
- [ ] HTTP methods match semantics (GET=read, POST=create, etc.)
- [ ] Status codes match semantics (2xx for success, 4xx/5xx for errors)
- [ ] Consistent error format across all endpoints
- [ ] Breaking changes planned for versioning
- [ ] Pagination uses consistent pattern

---

## Reference Index

IF mapping code structure or layering → spawn **`tp-explorer`**
IF auditing REST API contracts or resource modeling → spawn **`tp-endpoint-auditor`**