---
description: Audit a subagent for effectiveness and routing quality
argument-hint: <subagent-path>
---

Evaluate the subagent at $ARGUMENTS.

## Goal
Determine if this subagent will accomplish its task effectively.

## What Matters

**Goal clarity** — Is the job obvious? Can it succeed without user interaction?

**Tool selection** — Does it have the tools it needs? Are there unnecessary tools (security risk)?

**Routing** — Will Claude know when to invoke? The description field is how routing happens.

**Context completeness** — Since subagents can't ask follow-ups, is everything provided upfront?

## Output

Provide findings with file:line references. Be specific. Don't just say "improve X" — say exactly what to change.
