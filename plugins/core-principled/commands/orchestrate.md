---
name: orchestrate
description: Select the execution mode for a task — inline, isolated-context subagents, or orchestration script — and dispatch. NOT for: planning a multi-phase project (use `plan-execute`); NOT for: just running a skill (use the skill's slash command directly).
argument-hint: [task to orchestrate]
---

Load the subagent-orchestration skill and dispatch using the selected execution mode, then surface status updates and the selected mode to the user.