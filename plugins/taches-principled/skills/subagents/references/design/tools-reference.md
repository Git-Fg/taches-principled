---
name: tools-reference
description: Subagent orchestration tools reference — TaskGet, TaskOutput, TaskStop, Monitor, SendMessage
---

# Orchestration Tools Reference

## Spawn Subagent

```bash
Agent(
  description = "...",
  subagent_type = "general-purpose",
  model = "sonnet",
  tools = ["Read", "Grep", "Bash"],
  background = true
)
```

## List Running Subagents

```bash
TaskList
```

## Inspect Subagent State Mid-Flight

```bash
TaskGet(taskId = "agent-id")
```

Returns full subagent details: status, errors, progress.

## Retrieve Output Without Blocking

```bash
TaskOutput(taskId = "agent-id", block = false, timeout_ms = 0)
```

Returns subagent's accumulated output file directly. Parse before using.

**Workflow:**
```
Agent spawned (background=true)
→ After expected time, TaskGet(taskId) to check status
  → If stuck: TaskStop + respawn with corrected prompt
  → If failed: TaskGet for error details → root-cause → re-decompose
  → If running: wait or continue other work
```

## Stop Running Subagent

```bash
TaskStop(taskId = "agent-id")
```

## Resume Subagent

```bash
SendMessage(to = "agent-id", message = "Continue the previous work")
```

## Failure Signal Format

Require subagents to report:

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

If status is "failed" with retry_possible=true → retry once with corrected prompt.
If status is "failed" with retry_possible=false → re-decompose, don't retry same way.