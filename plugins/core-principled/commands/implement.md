---
name: implement
description: Execute task implementation with verification at each step
argument-hint: "[task-title-or-path] [--continue] [--refine] [--human-in-the-loop]"
---

## Context

- Task: $ARGUMENTS

## Your task

Execute the task above with verification at each step. Spawn developer subagents per step with independent judge verification. Honor `--continue` to resume, `--refine` to re-verify after manual edits, and `--human-in-the-loop` for checkpoint review.