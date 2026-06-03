# Stack Trace Methodology

Trace bugs backward through the call stack to find the original trigger.

## Core Principle

Bugs manifest deep in the call stack. Every error has an original trigger upstream from where it surfaces. Fix at the source, not the symptom. Never fix where the error appears — trace backward until you find where invalid data or incorrect behavior originated.

## Process

**Phase 1: Observe the Symptom**
1. Read the error message — what failed and where
2. Identify the immediate failing operation (the line that throws)

**Phase 2: Trace Upward**
1. Find what called the failing operation
2. What value was passed, and where did that value come from?
3. Repeat: keep asking "what called this?" and "what was the input?"
4. Stop when you reach the original trigger — where the wrong value was first introduced or the wrong path was first taken

**Phase 3: Fix at Source**
1. Correct the original trigger (fix the data source, the condition, the test setup)
2. Add validation at the layer where the trigger occurs (guard the source)
3. Add validation at intermediate layers (defense-in-depth — catch it earlier next time)
4. Add validation at the symptom layer (last resort — but better than nothing)

**Phase 4: Verify**
1. Confirm the symptom no longer reproduces
2. Confirm the fix does not break upstream behavior
3. Run the full test suite

## Adding Instrumentation

When manual tracing hits a dead end:

```typescript
// Before the problematic operation — log context, not just the error
const stack = new Error().stack;
console.error('DEBUG [operation]:', { input, cwd, stack });
```

- Use `console.error()` in tests (logger may be suppressed in test output)
- Log before the operation, not after it fails
- Include all context: directory, cwd, environment variables, timestamps

## Design Decisions

- **Trace backward, not forward** — Forward tracing follows the happy path. Backward tracing follows the actual execution path. These diverge when invalid state enters mid-execution.
- **Instrumentation before, not after** — Logging before a failure captures the state that caused it. Logging after loses the cause context.
- **Defense-in-depth is part of the fix** — Fixing the source is necessary but not sufficient. Add validation at intermediate layers so the next similar bug is caught earlier.
