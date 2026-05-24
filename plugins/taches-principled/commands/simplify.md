---
name: simplify
skill: refine
description: Simplify and refine recently modified code for clarity and maintainability
argument-hint: [file-pattern]
---

$ARGUMENTS

Fan out subagents onto each file to identify nesting, duplication, and dead code. Refactor within scope boundaries only — do not expand scope during simplification. After changes, run tests and verify edge cases beyond the initial report, summarizing what changed and what was intentionally preserved.