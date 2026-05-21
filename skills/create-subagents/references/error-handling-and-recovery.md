---
name: error-handling-and-recovery
description: Failure modes, recovery strategies, and retry patterns for subagents
---

# Error Handling and Recovery

Subagents encounter failures that require structured response. This document defines failure taxonomy, detection patterns, and recovery workflows.

---

## Subagent Failure Modes

| Mode | Description | Common Triggers |
|------|-------------|-----------------|
| **Logic failure** | Subagent produces incorrect or incomplete output due to flawed reasoning | Ambiguous prompt, missing domain context |
| **Transient failure** | Temporary condition causes failure (network, rate limit, timeout) | External API errors, resource contention |
| **Context exhaustion** | LLM exceeds context window or tool call budget | Complex task, deep call chains |
| **Tool permission denied** | Subagent attempts action it lacks permission for | Restricted tools, sandbox constraints |

---

## Detection and Diagnosis

Diagnose failure type by examining error output and return structure:

**Logic failure signals:**
- Compilation errors, type mismatches, or runtime exceptions in output
- Output contains hallucinations or contradicts known facts
- Subagent requests clarification mid-task that indicate misunderstanding

**Transient failure signals:**
- HTTP 429/503 responses, connection timeouts, EOF errors
- Intermittent tool failures that succeed on retry
- Resource temporarily unavailable messages

**Context exhaustion signals:**
- Truncated output, incomplete file writes, or cut-off responses
- Model returns context window error
- Tool call count exceeds budget without completion

**Permission denial signals:**
- Permission denied errors from tool layer
- Access control violations in error output
- Missing credentials or authentication errors

---

## Recovery Strategies

| Failure Mode | First Retry | Second Retry | Final Action |
|--------------|-------------|--------------|--------------|
| Logic failure | Retry with same prompt | Retry with corrected prompt + additional context | Stop and report with diagnosis |
| Transient failure | Retry with same prompt | Retry with exponential backoff | Stop and report after backoff |
| Context exhaustion | Simplify task, reduce scope | Split into smaller sub-tasks | Stop and report with partial output |
| Tool permission denied | Verify permission configuration | Retry with alternative tool | Stop and report permission gap |

---

## Retry Rules

**Rule 1:** Maximum two retries per distinct failure root cause.

**Rule 2:** If the same failure repeats after two retries, stop and report. Do not loop silently.

**Rule 3:** Distinguish new failures from recurring failures. A new transient error after a logic error retry is a fresh attempt — reset retry counter for the new root cause.

**Rule 4:** Always log the retry count and root cause. Future diagnostic work depends on this trail.

**Rule 5:** Never retry without changing something. Re-sending identical prompt to a failing subagent produces identical failure.

---

## Failure Signal Format

When a subagent encounters a failure it cannot resolve, it returns a structured failure signal:

```json
{
  "status": "failed",
  "failure_mode": "logic_failure|transient_failure|context_exhaustion|permission_denied",
  "root_cause": "Description of what caused the failure",
  "attempts": [
    {"prompt": "...", "error": "...", "timestamp": "ISO8601"},
    {"prompt": "...", "error": "...", "timestamp": "ISO8601"}
  ],
  "partial_output": "Any output produced before failure (may be null)",
  "diagnosis": "What the orchestrator should understand about this failure",
  "suggested_recovery": "Retry with corrected prompt | Stop and manual resolve | Alternative approach"
}
```

**Orchestrator contract:** A subagent that returns `status: failed` has exhausted its retry budget. The orchestrator must decide next action — retry with modified context, spawn alternative subagent, or escalate to human review.