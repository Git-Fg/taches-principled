# Nano-Spec: Ultra-Lightweight Task Capture

For one-liners, bug fixes, and hotfixes. No refinement — goes straight to implementation.

## When to Use

This spoke loads when scope-work infers Nano-Spec scale: a single sentence, a file path with an error, or a quick capture ask.

## Task Type Classification

| Type | Extension | Use When |
|------|-----------|----------|
| feature | `.feature.md` | New functionality or capability |
| bug | `.bug.md` | Something is broken or not working |
| refactor | `.refactor.md` | Code restructuring, no behavior change |
| test | `.test.md` | Adding or updating tests |
| docs | `.docs.md` | Documentation changes only |
| chore | `.chore.md` | Maintenance, dependency updates |
| ci | `.ci.md` | CI/CD configuration changes |

## Process

1. **Capture intent verbatim** — preserve the user's exact words
2. **Verify directory exists** — ensure `.specs/tasks/draft/` exists
3. **Classify type** — select extension from table above
4. **Generate filename** — title must start with action verb (Add, Fix, Update, Implement, Remove, Refactor)
5. **Persist to draft folder** — `.specs/tasks/draft/<name>.<type>.md`

## Output Format

```
Title: <action-oriented title>
Type: <feature|bug|refactor|test|docs|chore|ci>
Depends on: <list or "none">

## Original Intent
<user's exact words preserved>
```

## Design Decisions

- **Type as extension** — file extension encodes task type for visibility in listings
- **Draft separation** — unrefined tasks go to draft; refinement is a separate step
- **No verification rubrics** — nano-specs go straight to implement-task; verification happens there
- **Title action-verb rule** — titles must start with Add, Fix, Update, Implement, Remove, Refactor
