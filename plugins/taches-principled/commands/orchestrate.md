---
name: orchestrate
skill: subagents
description: Orchestrate parallel subagent execution for complex multi-file tasks
argument-hint: [task to orchestrate]
---

$ARGUMENTS

Decompose the work into independent tasks, fan out subagents in parallel, aggregate results, and verify completeness. Spawn a critic subagent to review the final output.