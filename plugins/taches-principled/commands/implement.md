---
name: implement
skill: implement-task
description: Execute task implementation with verification at each step
argument-hint: [task description or path]
---

$ARGUMENTS

Create a task list tracking each change needed. Fan out implementation subagents in parallel, each tracking their own task list. Run tests and lint after every step and do not advance past a failing check. Only self-review for final synthesis.