---
name: test
description: "Test strategy decisions — what to test, when to mock, fixture patterns, generative testing. Triggers: coverage analysis, mock strategy, test data design, property-based testing, minimal reproduction."
when_to_use: "Use when deciding WHAT to test. Trigger phrases: 'what should I test', 'test coverage', 'coverage analysis', 'mock this', 'fake dependencies', 'test doubles', 'test fixtures', 'test data', 'setup teardown', 'property-based testing', 'generative testing', 'shrink wrapping'. CONTRAST with tdd: tdd teaches how to write tests (red-green-refactor); this skill teaches what decisions to make before writing tests. Use this skill for test strategy questions; use tdd for implementation execution."
argument-hint: "[mode] [target]"
user-invocable: true
---

## Decision Router

**Priority Order:** Strategy precedes implementation. Use COVERAGE when uncertain what to test. Use MOCK-STRATEGY when dependencies complicate tests. Use FIXTURE when test data becomes unwieldy. Use PROPERTY-BASED when edge cases need systematic exploration.

IF unsure what to test or what coverage matters → use COVERAGE
IF deciding whether to mock or use real dependencies → use MOCK-STRATEGY
IF test setup exceeds 10 lines or data management is messy → use FIXTURE
IF need to find edge cases systematically or generate minimal reproduction → use PROPERTY-BASED

# COVERAGE

What to test, what to skip, what coverage matters.

## The Coverage Illusion

100% line coverage is achievable but often meaningless. A test that executes every line but never asserts is worse than no test. Coverage is a proxy, not a goal.

**Coverage that matters:**
- Critical paths (money, security, data integrity)
- Public interfaces of modules with complex internals
- Error and edge cases in business logic
- Integration points where systems meet

**Coverage that doesn't matter:**
- Getter/setter boilerplate
- Framework glue code
- Private implementation details
- Trivial one-liners with obvious behavior

## Decision Framework

| What | Why test | Why skip |
|------|----------|---------|
| Public API | Contract must hold | Implementation details |
| Business rules | Behavior matters | Internal structure |
| Error paths | Failure modes count | Happy path already covered |
| Integration points | Where systems break | Internal logic |
| Configuration | Environment affects behavior | Hardcoded safe defaults |

## Heuristics by System Type

**Business logic:** Test rules, not implementation. If you can explain the rule in one sentence, it's testable. If it requires a paragraph, split it first.

**Data access:** Test queries, not ORMs. Verify the query does what you expect; ORM behavior is covered by the library's own tests.

**External services:** Mock at boundary. Test what you send and receive; don't test the service's internal behavior.

**Configuration:** Test the configuration parsing, not the default values. If the code does X when config is Y, test that mapping.

## Anti-Patterns

- **Testing private methods** — You're testing implementation, not behavior. If the private method matters, make it public (or extract a class).
- **Assertion-free tests** — Tests that execute code but never assert anything: no expect() calls, no assert statements, no comparison assertions. These provide zero confidence — they pass whether the code works or not.
- **Coverage as quality** — High coverage with low assertion density is a false signal. Quality is in assertions, not execution.

# MOCK-STRATEGY

When to mock dependencies, when to use real implementations.

## The Mocking Spectrum

```
Real dependency → In-memory implementation → Test double (mock/stub/fake) → No dependency
```

## Decision Criteria

**Use real dependencies when:**
- The dependency is fast and deterministic (in-memory DB, mocked HTTP server)
- You need to verify integration behavior (end-to-end contracts)
- The behavior is well-understood and stable

**Use mocks when:**
- The dependency is slow, non-deterministic, or has side effects (real API, filesystem, time)
- You need to control specific inputs to reach edge cases (error responses, timeout scenarios)
- The dependency is external and not your responsibility to test

**Never mock when:**
- The mock would duplicate the production implementation's complexity
- You're testing behavior that spans multiple components
- The test becomes more complicated than the code it's testing

## The Trust Boundary

```
Your code ←→ Mock at boundary ←→ External system
```

**Inside your codebase:** Use real implementations or in-memory substitutes. The goal is confidence that components work together.

**At boundaries:** Mock external systems (APIs, databases, file systems). Test your side of the contract, not theirs.

## Mock Types

| Type | Use when | Anti-pattern |
|------|----------|--------------|
| **Stub** | You need to provide specific responses | Asserting on what was never called |
| **Mock** | You need to verify interactions (calls, arguments) | Testing implementation details |
| **Fake** | You need simplified behavior that's still useful | When real implementation is faster |
| **Spy** | You need to observe calls without controlling them | Complex setup for simple verification |

## Anti-Patterns

- **Mocking value objects** — Strings, numbers, dates don't need mocks. Mock the services that consume them.
- **Mocking what you're testing** — If you're testing module A, don't mock module B if A calls B. Use real B or restructure.
- **Excessive stub setup** — If your test setup is longer than your assertions, the design is wrong.

# FIXTURE

Test data management patterns — setup, factories, builders.

## Fixture Complexity Signal

Test setup complexity is a design smell. If setup grows beyond 10 lines for a single test, the code under test likely has too many dependencies. Fix the code, not the fixture.

## Patterns by Complexity

**Simple (0-3 fixtures):** Inline data. Direct object construction in the test. Works when dependencies are minimal.

**Medium (4-10 fixtures):** Factory methods. Shared setup in a method, customized per test. "createValidOrder()" returning an order with sensible defaults.

**Complex (10+ fixtures):** Builder pattern. Chain methods to construct objects step by step. "OrderBuilder().withItem(product).withShipping(express).build()"

## Factory vs Builder

**Factory:** Creates complete objects with sensible defaults. Good for "most tests use this shape." Less flexible, simpler.

**Builder:** Constructs objects piece by piece. Good for "each test needs a different slice." More flexible, more verbose.

```
Factory: order = createOrder()     // complete, ready to use
Builder: order = OrderBuilder()    // configure then build
        .withItem(sKU: "SKU-1")
        .withShipping(expedited)
        .build()
```

## Shared Fixtures vs Local Fixtures

| Approach | Use when | Trade-off |
|----------|----------|-----------|
| **Shared fixture** | Same data across many tests | One change breaks many tests |
| **Local fixture** | Each test needs different shape | More setup code, isolation |
| **Parameterized** | Many tests need same data shape | DRY but less explicit |

## Anti-Patterns

- **God fixtures** — One fixture used by 50 tests. Change it, break 50 tests.
- **Mystery data** — Fixtures with unexplained fields: `{name: "x", amount: 100, flag: true}`. Document or remove.
- **Fixture inheritance chains** — BaseFixture → OrderFixture → ValidOrderFixture. Hard to trace, easy to break.

# PROPERTY-BASED

Generative testing approaches — finding edge cases systematically.

## When to Use

Property-based testing shines when:
- Input space is large (strings, numbers, dates)
- Edge cases are non-obvious (null, empty, boundary values)
- Human intuition misses patterns (combinatorial explosion)
- Same property should hold across all inputs

## The Property Mindset

Instead of "test these 5 specific inputs," ask "what invariant must hold for ALL inputs?"

```
Example: Sort is reversible
- Pick 10 random arrays
- Sort each array
- Verify: original array == sorted array.sort()  // reverse sort

Example: Parser rejects invalid input
- Pick 100 random strings
- Verify: invalid strings raise ParseError
```

## Shrink Wrapping

When a generated input causes a failure, the test framework tries smaller inputs to find the minimal reproduction. This minimal case is the "shrunk" input — the simplest version that still triggers the bug.

**Why it matters:** A failing test that generates "f8xK29!@#qwer" is unhelpful. A shrunk input of "" (empty string) pinpoints the actual issue.

## Test Frameworks

| Language | Framework | Shrink algorithm |
|----------|-----------|------------------|
| JavaScript | fast-check | Power of 2 tree |
| Python | hypothesis | Binary search |
| TypeScript | fast-check | Power of 2 tree |
| Rust | proptest | Linear search |
| Go | testing/quick | Binary search |

## Common Properties to Test

- **Round-trip:** Serialize then deserialize, verify equality
- **Commutativity:** A op B == B op A
- **Idempotence:** op(op(x)) == op(x)
- **Identity:** op(x, identity) == x
- **Distributivity:** A op (B op C) == (A op B) op C
- **Monotonicity:** input grows → output doesn't decrease (or similar)

## Anti-Patterns

- **Testing implementation** — "Property holds for random inputs" is fragile if implementation changes. Test behavior, not structure.
- **Weak invariants** — "Result is defined" is not a property. "Result is in range [0, max]" is a property.
- **Too many properties** — One strong property beats five weak ones. Each property is a potential false failure.

## Integration with TDD

Property-based tests complement TDD: use TDD for known cases and edge cases you can anticipate; use property-based for combinatorial exploration. A complete test suite has both.