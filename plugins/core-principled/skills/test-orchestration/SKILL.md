---
name: test-orchestration
description: "Plan test strategies and execute test-driven development cycles, including coverage addition and test repair."
when_to_use: "Use for planning test suites, mocking, or TDD cycles. Triggers: coverage strategy, red-green-refactor, write tests first, add coverage, or fix broken tests."
argument-hint: "[mode] [target]"
---

## Routing Guidance

**Priority Order:** Strategy precedes execution. Use STRATEGY when making decisions about tests. Use EXECUTE when writing or fixing tests.

IF deciding what to test, coverage strategy, mocking approach, fixture design, or property-based testing → use STRATEGY
IF writing tests first, running red-green-refactor, adding post-hoc coverage, or fixing failing tests → use EXECUTE

IMMEDIATELY when the user says: 'fix tests', 'fix failing tests', 'tests are broken', 'restore test suite', 'update assertions'
BEFORE implementing any new feature or bug fix when tests do not yet exist

## Decision Router

| Mode | Trigger | Sub-modes |
|------|---------|-----------|
| STRATEGY | Deciding what to test, coverage, mocks, fixtures | COVERAGE, MOCK-STRATEGY, FIXTURE, PROPERTY-BASED |
| EXECUTE | Writing tests, red-green-refactor, coverage addition | Test-Driven Development, Write Tests, Fix Tests |

IF implementing a new feature from scratch → use Test-Driven Development (RED first)
IF fixing a bug → use Test-Driven Development (write reproducing test first)
IF adding test coverage for existing uncommitted changes → use Write Tests
IF fixing failing tests after refactoring or dependency updates → use Fix Tests
IF refactoring → tests must already exist and pass before starting

---

## §CONTRAST

**DO NOT use this skill for:**
- "Run the tests / see if they pass" — just run `cargo test` / `pytest` etc. directly; this skill is for *planning* and *fixing*, not for routine test runs
- "Review my code quality" → `refine` REVIEW mode
- "Investigate a failing test's root cause" → `diagnose` (this skill fixes symptoms; diagnose finds the underlying cause)
- "Plan the project / break it into phases" → `plan-lifecycle` (or `/plan` slash command)
- "Scan code for security vulnerabilities" → `security` skill

CONTRAST with `task-lifecycle`: task-lifecycle manages individual task SPECS end-to-end; this skill focuses specifically on the test layer.

---

# STRATEGY

Test planning decisions — what to test, what to mock, how to structure test data.

## COVERAGE

IF deciding what to test or what coverage matters → BEFORE proceeding read `references/strategy-coverage.md`. Do not proceed without reading this file.

## MOCK-STRATEGY

IF deciding whether to mock or use real dependencies → BEFORE proceeding read `references/strategy-mock.md`. Do not proceed without reading this file.

## FIXTURE

IF test setup exceeds 10 lines or data management is messy → BEFORE proceeding read `references/strategy-fixture.md`. Do not proceed without reading this file.

## PROPERTY-BASED

IF finding edge cases systematically or generating minimal reproduction → BEFORE proceeding read `references/strategy-property.md`. Do not proceed without reading this file.

---

# EXECUTE

Test execution — red-green-refactor cycles, coverage addition, test repair.

## Test-Driven Development

IF writing the test first and running red-green-refactor → BEFORE proceeding read `references/execute-tdd.md`. Do not proceed without reading this file.

## Write Tests

IF adding post-hoc test coverage for existing code → BEFORE proceeding read `references/execute-write-tests.md`. Do not proceed without reading this file.

## Fix Tests

IF fixing failing tests after refactoring or dependency updates → BEFORE proceeding read `references/execute-fix-tests.md`. Do not proceed without reading this file.

---

## Reference Index

| IF condition | Read this reference |
|-------------|---------------------|
| Deciding what to test or coverage strategy | `references/strategy-coverage.md` |
| Deciding mocking approach | `references/strategy-mock.md` |
| Test data management or fixture design | `references/strategy-fixture.md` |
| Finding edge cases with property-based testing | `references/strategy-property.md` |
| Writing tests first (red-green-refactor) | `references/execute-tdd.md` |
| Adding post-hoc coverage for existing code | `references/execute-write-tests.md` |
| Fixing failing tests after refactoring | `references/execute-fix-tests.md` |