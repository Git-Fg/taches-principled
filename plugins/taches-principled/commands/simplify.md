---
name: simplify
skill: refine
description: Simplify and refine recently modified code for clarity and maintainability
argument-hint: [file-pattern]
---

$ARGUMENTS

Analyze the code for patterns where structure obscures intent. Simplify within clear scope boundaries — refactor for clarity without expanding scope. Once changes are applied, confirm the full surface area still behaves correctly, especially edge cases beyond the initial report. Report what changed and what was intentionally left alone.