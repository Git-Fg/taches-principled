---
name: archive
description: Archive completed plans and run memory hygiene. Use when wrapping up work or cleaning Claude memory.
argument-hint: "[plan-archive|memory-audit|memory-dedup|memory-archive|memory-clean] [path] [--abandoned] [--days 30]"
---

## Context

- Mode and arguments: $ARGUMENTS
- If empty, default to `plan-archive` for the most recent completed plan.

## Your task

Route to the `project-maintenance` skill with the provided mode and arguments. If no mode is given, the skill's decision router will select based on context. Do not duplicate the skill's body — invoke it and follow its mode-specific workflow.
