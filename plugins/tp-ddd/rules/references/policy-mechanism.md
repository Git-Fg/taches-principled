# Policy vs. Mechanism

**Mechanism** — a pure function that computes and returns a result without causing side effects. Given the same inputs, it always produces the same outputs. Examples: `isValid(result)` returns a boolean, `formatResult(result)` returns a string, `applyNewFeature(data)` returns transformed data.

**Policy** — the decision made by the caller about what to do with a mechanism's result. Policy decides whether to throw, log, branch, or ignore. Policy belongs at the call site where the reader can see it. Examples: `if (!isValid(result)) throw`, `logger.info(formatResult(result))`, `featureEnabled ? applyNewFeature(baseData) : baseData`.

## Key Principle

When policy is hidden inside a mechanism — a `validate` function that throws, an `apply` function that checks feature flags — the call site becomes deceptive. The reader sees what looks like a passive check but is actually a control flow branch. Keeping mechanisms pure and policies explicit makes code predictable and composable: the same mechanism can serve different policies without modification.

## Examples

| Mechanism (pure) | Policy (call-site decision) |
|------------------|------------------------------|
| `isValid(result)` returns boolean | `if (!isValid(result)) throw` |
| `applyNewFeature(data)` returns transformed data | `featureEnabled ? applyNewFeature(baseData) : baseData` |
| `formatResult(result)` returns string | `logger.info(formatResult(result))` |