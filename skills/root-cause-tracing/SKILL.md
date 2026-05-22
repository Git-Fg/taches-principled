---
name: root-cause-tracing
description: Traces bugs backward through the call stack to find the original invalid data or incorrect behavior trigger
when_to_use: |
  Use when the user says "trace this bug", "find where it started", "what called this", or "where did this come from".
  IMMEDIATELY when an error occurs deep in execution with a long call chain.
argument-hint: "[error description or symptom]"
---

## Decision Router

IF an error occurs deep in execution with a long call chain → trace backward one level at a time to find the original trigger
IF unable to trace manually because of missing context → add instrumentation (stack trace logging) before the failure point, not after
IF the immediate cause is obvious but its origin is unclear → trace one more level up: "what called this, and with what value?"
IF a test case pollutes global state but the source is unknown → bisect across tests to isolate the first polluter
IF multiple layers of validation could prevent recurrence → add defense-in-depth at each layer after fixing the source

# Root Cause Tracing

Bugs manifest deep in the call stack. Every error has an original trigger upstream from where it surfaces. Fix at the source, not the symptom.

## Core Principle

Never fix where the error appears. Trace backward through the call chain until you find where invalid data or incorrect behavior originated. Then fix at the source and add validation at every layer between source and symptom.

## Process

### Phase 1: Observe the Symptom
1. Read the error message — what failed and where
2. Identify the immediate failing operation (the line that throws)

### Phase 2: Trace Upward
1. Find what called the failing operation
2. What value was passed, and where did that value come from?
3. Repeat: keep asking "what called this?" and "what was the input?"
4. Stop when you reach the original trigger — where the wrong value was first introduced or the wrong path was first taken

### Phase 3: Fix at Source
1. Correct the original trigger (fix the data source, the condition, the test setup)
2. Add validation at the layer where the trigger occurs (guard the source)
3. Add validation at intermediate layers (defense-in-depth — catch it earlier next time)
4. Add validation at the symptom layer (last resort — but better than nothing)

### Phase 4: Verify
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

## Output

A root cause identified at its source with layered validation preventing recurrence. The fix includes:
- A correction at the original trigger point
- Validation guards at intermediate layers
- A last-resort guard at the symptom layer

## Design Decisions

### Trace backward, not forward
Forward tracing (from entry point to error) follows the happy path. Backward tracing (from error to entry point) follows the actual execution path. These can diverge when invalid state enters mid-execution.

### Instrumentation before, not after
Logging before a failure captures the state that caused the failure. Logging after captures the error but loses the cause context. Always instrument before the dangerous operation.

### Defense-in-depth is part of the fix
Fixing the source is necessary but not sufficient. Add validation at intermediate layers so the next similar bug is caught earlier. The fix is complete when the bug is impossible to reintroduce at any layer.
