---
name: diagnose
description: "Investigate and find the root cause of complex bugs, recurring failures, or unexpected behavior. Use when the user says 'why is this happening', 'find the bug', 'analyze the failure', 'what broke', 'regression', 'incident analysis'. Four modes: A3 (structured root-cause doc), FIVE-WHYS (single causal chain), FISHBONE (multi-factor), STACK-TRACE (call-chain tracing). NOT for: general code improvement (use `refine`); NOT for: design/architecture issues (use `ddd`)."
allowed-tools: Read, Write
when_to_use: |
  - User is dealing with a bug that has a long call chain or is hard to reproduce.
  - User wants to understand why a previous fix failed or why an incident occurred.
  - Use when a problem is "causal" (investigating the past) rather than "decisional" (evaluating the future).
argument-hint: "[problem description]"
---

## Activation Triggers

- IMMEDIATELY when investigating incidents, recurring issues, systemic failures, or bugs with long call chains.
- CONTRAST with fpf and refine: diagnose investigates why something is broken (past, causal, unknown type); fpf evaluates competing options to decide a path forward (future); refine improves known artifacts (present, corrective). Prefer diagnose when "problem" or "issue" appears without alternatives.

## What This Skill Changes

**Default behavior:** Claude assumes symptoms are the problem — it fixes where errors appear and follows the happy path forward through code, missing the actual trigger.

**With this skill:** Claude traces backward from symptoms to root causes. Each investigation method (A3, Five Whys, Fishbone, Stack Trace) targets a different problem structure. AUTO mode removes method-selection overhead when the problem type is already clear.

**Why this matters:** Fixing symptoms is the most expensive kind of fix. Every "I fixed it" that recurs with a different input is a symptom-level fix. Systematic root cause tracing produces solutions that don't come back.

---

## Decision Router

IF investigating a specific incident, recurring issue, or major problem needing structured documentation → use **A3** mode — ALWAYS spawn a `tp-explorer` subagent (scope: "investigate the incident; map the code paths involved") before analysis. You MUST read `references/a3-methodology.md` BEFORE executing A3 mode.
IF problem has a clear single causal chain from symptom to root → use **FIVE-WHYS** mode. You MUST read `references/five-whys.md` BEFORE executing FIVE-WHYS mode.
IF problem has multiple potential contributing factors across domains → use **FISHBONE** mode — ALWAYS spawn category-specific `tp-explorer` subagents in parallel, each scoped to one factor's code paths. You MUST read `references/fishbone.md` BEFORE executing FISHBONE mode.
IF an error surfaces deep in execution with a long call chain → use **STACK-TRACE** mode — ALWAYS spawn a `tp-explorer` subagent (scope: "instrument code before the failure point and trace the call chain backward to its trigger") to investigate before analysis. You MUST read `references/stack-trace.md` BEFORE executing STACK-TRACE mode.
**Note:** STACK-TRACE tracing is also used by `session-analytics` CROSS-ANALYZE mode for debug log root-cause tracing.
IF the problem type is unclear or the user wants auto-selection → use **AUTO** mode
IF user specifies a mode explicitly → apply that mode directly

---

## Routing Guidance

Problem investigation across five complementary methods. Each method targets a distinct problem structure. AUTO mode removes decision overhead when the target type is clear.

## AUTO Mode

Auto-selects the most appropriate method based on problem type when the user has not specified one.

| If the problem is... | Use... |
|---|---|
| A specific incident, recurring issue, or major failure | A3 |
| A clear single causal chain from symptom to root cause | Five Whys |
| Multiple potential contributing factors across domains | Fishbone |
| An error deep in execution with unknown origin | Stack Trace |

---

## Relationship Between Methods

AUTO mode handles method selection when the problem structure is unclear. When AUTO selects deeper analysis or when the method is already known, use the specific mode directly:

- **A3** — Structured documentation for incidents and major problems
- **FIVE-WHYS** — Single-path causal chain drilling
- **FISHBONE** — Multi-category cause mapping
- **STACK-TRACE** — Call-chain debugging for errors

A3 can incorporate Five Whys or Fishbone within its root cause section. Stack Trace is standalone for deep execution errors.

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | completed_portion | retry_possible |
|--------|--------|-------------------|----------------|
| `failed` | `investigation-dead-end` | Evidence gathered but root cause not found | `true` (reformulate hypothesis) |
| `failed` | `insufficient-context` | Missing environment or logs for analysis | `false` (need more info from user) |
| `failed` | `method-selection-failed` | AUTO mode could not determine appropriate method | `true` (manually specify method) |
| `failed` | `five-whys-loop` | Causal chain exceeds 10 iterations without resolution | `false` (escalate to human) |
| `failed` | `stack-trace-incomplete` | Call stack truncated or unavailable | `true` (add instrumentation and retry) |
| `failed` | `a3-template-invalid` | Template structure not followed | `true` (restart A3 with guidance) |

**Fields:**
- `status`: `"failed"` when investigation cannot complete; `"success"` when root cause found
- `reason`: Specific failure mode from the options above
- `completed_portion`: What was completed before failure (e.g., "5 whys completed, cause unclear")
- `retry_possible`: `true` if recoverable with different approach; `false` if needs human input

## CONTRAST

- NOT for: runtime debugging with breakpoints or live instrumentation — use the debug skill
- NOT for: first-principles reasoning on competing hypotheses — use fpf
- NOT for: general code improvement or cleanup — use refine
