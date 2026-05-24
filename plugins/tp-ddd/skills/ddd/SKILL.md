---
name: ddd
description: "Domain-Driven Design code quality — structure code with layered architecture and functional core (ARCHITECTURE), apply domain-specific naming and library-first principles (QUALITY), ensure code reveals behavior with visible side effects and explicit control flow (TRANSPARENCY)."
when_to_use: |
  ARCHITECTURE: 'where does business logic go', 'where should this logic go', 'should domain know about database', 'how do I test without mocks', 'too much nesting', 'too many parameters', 'function does too much', 'function is too long', 'business logic in controllers'
  QUALITY: 'what should I name this', 'is utils a good name', 'should I use a library', 'why did this error happen', 'silent failure'
  TRANSPARENCY: 'hidden side effect', 'does this return or mutate', 'command vs query', 'should this function mutate or return', 'is this a side effect', 'pure function', 'where should I put error handling', 'data unexpectedly changing', 'can't trace value origin', 'mutation disguised as query'
  Use when code has excessive nesting, domain logic leaks into infrastructure, or tests require heavy mocking.
---

## Decision Router

IF code structure or layering issue → ARCHITECTURE mode
IF naming or error handling issue → QUALITY mode
IF behavior visibility or data flow issue → TRANSPARENCY mode

# Mode: ARCHITECTURE

Structure code for maintainability with four principles: layered architecture, functional core, early returns, function size limits.

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