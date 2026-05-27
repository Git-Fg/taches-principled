---
name: tdd
description: "Complete test lifecycle — Red-Green-Refactor TDD, post-hoc coverage addition, and failing test repair."
when_to_use: "Use when the user says 'TDD', 'test-driven', 'RED-GREEN', 'write the test first', 'test first', or 'red green refactor'. IMMEDIATELY when the user says 'fix tests', 'fix failing tests', 'tests are broken', 'restore test suite', or 'update assertions'. BEFORE implementing any new feature or bug fix when tests do not yet exist. CONTRAST with test: tdd handles execution (write tests, red-green-refactor, fix broken tests); test handles strategy (what to test, mocking decisions, fixture design). Use tdd when you know what to test; use test when deciding what to test."
---

## Decision Router

**Priority Order:** Test-Driven Development is the first step (use when no tests exist for a feature). Write Tests is for post-hoc coverage (use when TDD wasn't followed). Fix Tests is for restoration after refactoring.

IF implementing a new feature from scratch → use Test-Driven Development (RED first)
IF fixing a bug → use Test-Driven Development (write reproducing test first)
IF adding test coverage for existing uncommitted changes → use Write Tests
IF fixing failing tests after refactoring or dependency updates → use Fix Tests
IF refactoring → tests must already exist and pass before starting
IF no tests exist for existing code → code is untested — start with Test-Driven Development

# TDD

Complete test lifecycle management. Three complementary methods cover the full development cycle: Red-Green-Refactor discipline for new work, coverage addition for existing changes, and repair for failing tests.

All methods preserve test intent, follow project conventions, and verify by running the full test suite. The choice between methods depends on whether you are creating, covering, or fixing tests.

## Test-Driven Development

Write the test first. Watch it fail for the right reason. Write minimal code to pass. Never skip the failure step — a test you never saw fail proves nothing.

### Core Principle

If you did not watch the test fail, you do not know whether it tests the right thing.

### The Iron Law

ALWAYS write the failing test FIRST. NEVER write production code before the test fails. Write code before the test? MUST delete it. Start over. Not "keep as reference." Not "adapt it while writing tests." Delete means delete. Implement fresh from tests. Period.

### Red-Green-Refactor

**RED — Write Failing Test:** Write one minimal test for one behavior. Clear name, real code (mocks only if unavoidable), minimal setup. Requirements: one behavior, clear name, real code.

**Verify RED — Watch It Fail:** MANDATORY. Never skip. Run the test. Confirm it fails (not errors), the failure message matches expectations, and it fails because the feature is missing (not a typo). Test passes? You are testing existing behavior — fix the test. Test errors? Fix the error, re-run until it fails correctly.

**GREEN — Minimal Code:** Write the simplest code to pass the test. No extra features, no refactoring, no improvements.

**Verify GREEN — Watch It Pass:** MANDATORY. Run the test. Confirm pass, other tests still pass, output is pristine. If the test fails, fix the code — not the test.

**REFACTOR — Clean Up:** After green only. Remove duplication, improve names, extract helpers. Keep tests green. Do not add behavior.

**Repeat:** Next failing test for the next behavior. Return to RED.

### Anti-Patterns

- **Testing Mock Behavior** — Asserting on mock existence tests nothing about real behavior
- **Test-Only Methods in Production** — Methods only used in tests pollute production classes and create risk
- **Mocking Without Understanding** — Mocks that break side effects the test depends on produce false passes
- **Incomplete Mocks** — Partial mocks that omit fields downstream code uses cause silent failures

### When Stuck

| Problem | Solution |
|---------|----------|
| Do not know how to test | Write the wished-for API. Write the assertion first. |
| Test is too complicated | The design is too complicated. Simplify the interface. |
| Must mock everything | The code is too coupled. Use dependency injection. |
| Test setup is huge | Extract helpers. Still complex? Simplify the design. |

### Verification Checklist

- Every new function or method has a test
- Watched each test fail before implementing
- Each test failed for the expected reason (feature missing, not typo)
- Wrote minimal code to pass each test
- All tests pass — pristine output (no errors, warnings)
- Tests use real code (mocks only if unavoidable)
- Edge cases and error paths are covered

Cannot check every box? You skipped TDD. Start over.

## Write Tests

Systematically add test coverage for existing local changes. For when code already exists and needs coverage after the fact.

### Process

1. **Preparation** — Read project testing conventions, identify test command and coverage tools, run full suite for baseline
2. **Analysis** — Identify changed files via git status (uncommitted) or latest commit if everything committed. Filter non-code files. Assess complexity.
3. **Direct Writing** (simple single-file) — Read changed file, review existing test patterns for style and conventions, create tests for all identified cases, run and iterate until passing
4. **Agent Dispatch** (complex multi-file) — Launch one analysis agent per file to identify test cases, then one developer agent per file to create tests, then one verification agent per file to confirm coverage. Coordinate through shared test case lists.

### Agent Templates

**Analysis:** "Analyze {FILE_PATH} for test coverage needs. The diff shows: {GIT_DIFF}. Read the file and understand its business logic. Identify code paths needing tests: new functions, modified logic, edge cases, error handling. Review existing tests to avoid duplication. Output prioritized test cases (CRITICAL, IMPORTANT, NICE_TO_HAVE)."

**Development:** "Create tests for {FILE_PATH}. Required test cases: {TEST_CASES}. Review project testing conventions from README. Read the target file and existing test files for patterns. Create comprehensive tests for all cases. Run tests with: {TEST_COMMAND}. Iterate until all pass."

**Verification:** "Verify test coverage for {FILE_PATH}. Tests were added at: {TEST_FILES}. Read the changed file and the new test files. Confirm all critical business logic is covered. Report PASS or list specific gaps."

### Design Logic

Operates after implementation but before commit. Ensures changes are tested before entering the commit workflow. For multi-file changes, separate agents analyze each file in parallel and coordinate through shared test case lists — faster and more thorough than sequential manual work.

## Fix Tests

Fix failing tests after business logic changes, refactoring, or dependency updates. Preserve test intent — update assertions, not behavior.

### Core Principle

Fix the test, not the business logic — unless the logic itself contains a bug.

### Process

1. **Preparation** — Read project conventions, identify test command, run full suite to establish baseline, parse output for all failing files
2. **Analysis** — For each failing file, determine cause: test expectations outdated (update assertions), test setup broken (fix mocks or fixtures), or business logic bug (rare — confirm before changing)
3. **Fix** — Simple single-file: read the test, identify root cause, fix to match current behavior, run to verify, iterate until passing. Complex multi-file: dispatch one agent per failing file with context (why it broke), target (specific file), run command, and constraint to preserve test intent.
4. **Verification** — Run full suite, iterate on remaining failures, verify coverage maintained

### Agent Template

"The business logic has changed and test file {FILE_PATH} is now failing. Read the test file and understand what it tests. Read project testing conventions from README for context. Run the test and analyze the failure. Test expectations outdated? Fix test assertions. Test setup broken? Fix mocks or fixtures. Business logic bug? Fix logic (rare case — confirm first). Fix the test and verify it passes. Iterate until the test passes."

### Design Logic

After refactoring, behavior should be the same — only implementation changed. Tests that fail due to implementation details need updating. Tests that fail because behavior actually changed signal a logic bug. Operates after refactoring or dependency updates to restore the test suite to green so the commit workflow can proceed.

### Relationship Between Methods

Test-Driven Development is the first step of any implementation cycle — it defines correct behavior before code exists. Write Tests adds coverage for code where TDD was not followed. Fix Tests restores green after refactoring or dependency updates. Together they cover the full test lifecycle from creation through maintenance.
