---
name: critique
description: Get independent critique on high-stakes decisions and completed work. Spawns an isolated-context reviewer (free of your biases) that classifies findings as blocker / warning / suggestion. NOT for: full PR review (use the `refine` skill REVIEW mode for parallel 6-reviewer fan-out); NOT for: source-code bug diagnosis (use the `diagnose` skill).
argument-hint: [work to critique]
---

Fan out 2-3 reviewer subagents with isolated context to critique the target, then synthesize findings into severity-ranked issues with consensus areas and action items.