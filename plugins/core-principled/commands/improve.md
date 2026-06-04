---
name: improve
description: Improve the quality of any artifact — code, prose, or decisions
argument-hint: [artifact or file to improve]
---

# /improve

**Shorthand for the `refine` skill's CRITIQUE mode.**

`/improve <artifact>` is the "I just want this to be better, you decide how" entry point. It dispatches to the `refine` skill in **CRITIQUE** mode, which fans out reviewer subagents in parallel, aggregates their findings, and returns a severity-rated report plus the refined artifact.

## When to use `/improve` vs the `refine` skill directly

| Want | Use |
|---|---|
| "Make this better — your call on how" | `/improve <artifact>` (this command) |
| "Simplify this code" / "clean up" | `refine SIMPLIFY` (the skill) |
| "Review this PR" / "check my changes" | `refine REVIEW` (the skill, PR workflow) |
| "Critique this approach" / "what could be better" | `refine CRITIQUE` (same machinery as `/improve`, with explicit mode) |
| "Polish this prose" / "make this clearer" | `refine POLISH` (the skill) |
| "Capture this learning" | `refine MEMORIZE` (the skill) |

If the user just says "improve X", `/improve` is the right entry point. If they name a specific mode, use the skill directly. The command and the skill share underlying machinery — the command is a thin wrapper that defaults the mode to CRITIQUE and handles the spawn/aggregate/return flow.

Do not duplicate CRITIQUE's logic in this command. The skill is the source of truth; this command is a discoverable entry point.
