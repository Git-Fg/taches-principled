---
name: plan-execute
description: Run an existing PLAN.md end-to-end — load the plan, pick the right execution strategy, and orchestrate workers and critics through every phase
argument-hint: "[path to PLAN.md] [--resume] [--phase N]"
---

Load the user's referenced PLAN.md and any prior execution context. Hand off to the plan-lifecycle skill in EXECUTE mode to pick the right execution strategy (autonomous, segmented, or sequential) and run the plan with appropriate worker and critic subagents. Surface any checkpoint decisions that need user input.
