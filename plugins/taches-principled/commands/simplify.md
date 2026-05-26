---
name: simplify
skill: refine
description: Simplify and refine recently modified code for clarity and maintainability
argument-hint: [file-pattern]
---

$ARGUMENTS

Fan out subagents onto each file to identify nesting, duplication, and dead code. Refactor within scope boundaries, then run tests and verify edge cases.