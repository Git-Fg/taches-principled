---
name: failure-modes
description: Common subagent orchestration failure modes and prevention strategies
---

# Subagent Failure Modes Reference

| Failure Mode | Detection | Recovery Cost | Prevention |
|--------------|-----------|---------------|------------|
| **Over-delegation** | Obvious in hindsight | Low (do inline) | Default to inline for <5min tasks |
| **Context leakage** | Silent, subtle | High (full audit) | Non-semantic agent names; explicit subagent type |
| **Tool permission misconfig** | Immediate failure | Medium (reconfigure) | Validate YAML; use allowlists |
| **State management failures** | Silent corruption | High (validate outputs) | Schema validation at every tool boundary |
| **Blocking anti-patterns** | Appears productive | Very high (terminate all) | Hard iteration limits; don't race |
| **File conflicts** | Git conflicts visible | Medium (manual merge) | Worktree isolation; file-disjoint decomposition |
| **Rollback failures** | Broken state visible | High (manual revert) | Always specify rollback; verify before marking done |

---

## Retry Rules

| Failure Type | Action |
|--------------|--------|
| Non-deterministic (network, transient) | Retry with same prompt |
| Logic failure (misunderstanding) | Retry with corrected prompt |
| After 2 retries on same root cause | Stop, report findings, re-decompose |

**Never loop silently.** After 2 retries on same failure → re-decompose the task before respawning.