---
name: implement
skill: implement-task
description: Execute task implementation with verification at each step
argument-hint: [task description or path]
---

$ARGUMENTS

Create a task list tracking each change needed. Run tests and lint after every step and do not advance past a failing check. Self-review each change critically as if another developer produced it, delegating stuck items to a subagent so investigation runs in parallel.