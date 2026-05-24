---
name: debug
skill: diagnose
description: Apply systematic debugging methodology to investigate issues deeply
argument-hint: [issue description]
---

$ARGUMENTS

Use web search and code inspection to trace backward from the failure to its root cause. Fan out subagents onto independent hypotheses so candidates are tested in parallel, not sequentially. After fan-out, write all findings to a scratch file, then apply the confirmed fix and verify the full surface area still works.