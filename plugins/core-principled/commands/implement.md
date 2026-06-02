---
name: implement
description: Execute task implementation with verification at each step
argument-hint: "[task-title-or-path] [--continue] [--refine] [--human-in-the-loop]"
---

Execute the task with verification at each step by spawning developer subagents per step with independent judge verification, honoring --continue to resume, --refine to re-verify after manual edits, and --human-in-the-loop for checkpoint review.