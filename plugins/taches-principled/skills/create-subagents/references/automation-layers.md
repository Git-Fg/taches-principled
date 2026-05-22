---
name: automation-layers
description: Three automation layers — Hooks, ScheduleWakeup, Monitor — and when to use each
---

# Three Automation Layers

Choose by trigger type:

| Tool | Trigger | Best for |
|------|---------|----------|
| Hooks | Tool events | Validate subagent outputs, enforce guardrails |
| ScheduleWakeup / CronCreate | Time | Recurring orchestration, long-poll retries |
| Monitor | External events | Real-time CI/log watching, instant reaction |

---

## Monitor vs ScheduleWakeup

**Never poll when you can watch.**

| Aspect | Monitor | ScheduleWakeup |
|--------|---------|----------------|
| Cost while silent | Zero | Tokens per interval |
| Trigger | Output matches filter | Timer fires |
| Latency | Instant | Until next interval |
| Use when | Process emits output | No event output |

**Use ScheduleWakeup when:** external system has no event output (simple polling).
**Use Monitor when:** the process emits structured output (logs, CI lines, test results).

---

## Monitor Patterns

### CI Failure Watching

```bash
Monitor(
  description = "CI failure detector",
  command = "tail -f /tmp/ci.log | grep --line-buffered -E 'FAILED|ERROR|Build failed'",
  timeout_ms = 3600000,
  persistent = true
)
```

### Dev Server Error Catching

```bash
Monitor(
  description = "dev server errors",
  command = "tail -f server.log | grep --line-buffered 'ERROR\\|panic'",
  timeout_ms = 7200000
)
```

**Always use `grep --line-buffered`** in pipes — pipe buffering delays events by minutes.

**Filter aggressively** — every stdout line becomes a conversation message. Too many events → auto-stop.

---

## Background Subagents

Spawn in background for concurrent work:

```bash
Agent(description = "...", background = true)
```

**Background behavior:**
- Runs concurrently while orchestrator continues
- Auto-denies tool calls that would prompt (continues silently)
- Permission prompts surface in terminal
- Results return when subagent completes

**Use background when:**
- Orchestrator can proceed without the result
- Task is long-running (monitoring, polling)
- Parallel independent workstreams