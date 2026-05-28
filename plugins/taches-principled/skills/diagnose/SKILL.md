---
name: diagnose
description: "Auto-selects investigation method: A3, Five Whys, Fishbone, Stack Trace. Use when analyzing problems or finding root causes."
when_to_use: |
  Use when the user says:
  - "analyze this problem"
  - "find the root cause"
  - "why did this happen"
  - "trace this back"
  - "what's causing this"
  - "dig deeper into why X is broken"
  - "what's the underlying cause"
  - "trace the root cause of X"
  - "apply five whys to this"
  - "run a fishbone analysis on X"
  - "why is X failing" (when X is a recurring problem)
  - "analyze this"
  - "look into this code"
  - "what's wrong here"
  - "find the problem"
  - "trace this bug"
  - "find where it started"
  - "what called this"
  - "where did this come from"
  - "figure out what's wrong"
  - "root cause"
  - "why is this happening"
  IMMEDIATELY when investigating incidents, recurring issues, systemic failures, or bugs with long call chains. Use AUTO mode for method auto-selection when the problem type is unclear.
  CONTRAST with fpf: diagnose investigates why something is broken (past-focused); fpf evaluates competing options to decide a path forward (future-focused). Prefer diagnose when "problem" or "issue" appears without alternatives specified.
  CONTRAST with refine: diagnose investigates why something is broken (past, causal); refine improves quality of existing artifacts (present, corrective). Prefer diagnose when the issue is unknown; prefer refine when the issue is known and needs fixing.
argument-hint: "[problem description] [--mode A3|FIVE-WHYS|FISHBONE|STACK-TRACE|AUTO]"
---

## Decision Router

IF investigating a specific incident, recurring issue, or major problem needing structured documentation → use **A3** mode — ALWAYS spawn an explorer subagent to investigate before analysis
IF problem has a clear single causal chain from symptom to root → use **FIVE-WHYS** mode
IF problem has multiple potential contributing factors across domains → use **FISHBONE** mode — ALWAYS spawn category-specific explorer subagents in parallel for each factor
IF an error surfaces deep in execution with a long call chain → use **STACK-TRACE** mode — ALWAYS spawn a debug-tracer subagent to instrument code before failure points and trace backward through the call chain
IF the problem type is unclear or the user wants auto-selection → use **AUTO** mode
IF user specifies a mode explicitly → apply that mode directly

---

# Diagnose

Problem investigation across five complementary methods. Each method targets a distinct problem structure. AUTO mode removes decision overhead when the target type is clear.

## Core Principle

Match the investigation method to the problem structure. Surface symptoms need root cause tracing. Recurring incidents need structured documentation. Complex multifactorial problems need systematic cause mapping.

## AUTO Mode

Auto-selects the most appropriate method based on problem type when the user has not specified one.

| If the problem is... | Use... |
|---|---|
| A specific incident, recurring issue, or major failure | A3 |
| A clear single causal chain from symptom to root cause | Five Whys |
| Multiple potential contributing factors across domains | Fishbone |
| An error deep in execution with unknown origin | Stack Trace |
| Code implementation, legacy systems, docs vs reality gaps | Gemba Walk (via AUTO sub-selection) |
| Workflows, CI/CD pipelines, cycle time | Value Stream Mapping (via AUTO sub-selection) |
| Code quality, technical debt, waste | Muda Analysis (via AUTO sub-selection) |

### AUTO Sub-Selection

When AUTO mode selects deeper analysis or when the problem type is already clear:

- **Gemba Walk** — Observe actual code: entry points, data flow, compare assumptions against reality, document surprises
- **Value Stream Mapping** — Measure flow: map steps, measure processing vs waiting time, calculate lead time and efficiency
- **Muda Analysis** — Classify waste: examine seven waste types, quantify impact, prioritize by severity

---

## A3 Mode

Structured one-page problem documentation and resolution planning using the A3 format — named after the paper size that constrains analysis to concise, complete thinking.

### Core Principle

Force complete, concise root-cause-to-resolution thinking onto a single page. If it doesn't fit, the problem isn't well enough understood yet.

### Process

Observe symptom, define scope, identify causes using Five Whys or Fishbone, fix at the origin, verify. A3 paper size constraint forces complete thinking — if analysis exceeds one page, decompose into sub-problems.

### Template

```
TITLE: [Concise problem statement]

1. BACKGROUND — Why this matters
2. CURRENT CONDITION — What's happening (data, not opinions)
3. GOAL/TARGET — Specific, measurable targets
4. ROOT CAUSE ANALYSIS — Five Whys or Fishbone
5. COUNTERMEASURES — Actions tied to root causes
6. IMPLEMENTATION PLAN — Who, what, when, dependencies
7. FOLLOW-UP — Success metrics, monitoring, review dates
```

### Design Decisions

- **One-page constraint** — A3 paper size is the forcing function. If analysis requires more space, problem scope is too broad — decompose into sub-problems.
- **Countermeasures tied to root causes** — Every countermeasure traces to a specific root cause. This prevents treating symptoms.
- **Living document until closed** — Update as understanding grows or situation changes. Close only when follow-up metrics confirm success.

---

## FIVE-WHYS Mode

Iteratively ask "why" to trace from surface symptoms to fundamental systemic causes.

### Core Principle

Every surface symptom is the end of a causal chain. Treating the symptom leaves the chain intact. The goal is to find the systemic cause — a missing validation, unclear process, absent automation, or design choice.

### Process

Ask "why" iteratively until reaching a systemic cause. Every answer becomes the next question. Stop when reaching a missing process, validation, automation, or design gap. Propose solutions at the root cause level, not intermediate answers. "Five" is a guideline — stop when systemic.

### Output

A causal chain from symptom to root cause with solutions tied to the root cause level.

---

## FISHBONE Mode

Systematic exploration of all potential causes across six categories using the Ishikawa method.

### Core Principle

Every surface symptom has multiple potential contributing factors. Treating one branch leaves others intact. The goal is systematic cause mapping across all domains.

### The Six Categories

| Category | What to Examine |
|----------|----------------|
| **People** | Skills, training gaps, communication, team dynamics |
| **Process** | Workflows, procedures, standards, reviews |
| **Technology** | Tools, infrastructure, dependencies, config |
| **Environment** | Workspace, deployment targets, external factors |
| **Methods** | Approaches, patterns, architectures, practices |
| **Materials** | Data quality, third-party services, inputs |

### Process

State the problem as the "head." Explore all six categories (People, Process, Technology, Environment, Methods, Materials) — don't stop at the first cause. Cross-reference causes spanning multiple categories (systemic). Prioritize by impact and likelihood. Propose solutions tied to root causes.

### Output

A categorized cause map identifying root causes across six dimensions with prioritized solutions.

---

## STACK-TRACE Mode

Trace bugs backward through the call stack to find the original trigger.

### Core Principle

Bugs manifest deep in the call stack. Every error has an original trigger upstream from where it surfaces. Fix at the source, not the symptom. Never fix where the error appears — trace backward until you find where invalid data or incorrect behavior originated.

### Process

**Phase 1: Observe the Symptom**
1. Read the error message — what failed and where
2. Identify the immediate failing operation (the line that throws)

**Phase 2: Trace Upward**
1. Find what called the failing operation
2. What value was passed, and where did that value come from?
3. Repeat: keep asking "what called this?" and "what was the input?"
4. Stop when you reach the original trigger — where the wrong value was first introduced or the wrong path was first taken

**Phase 3: Fix at Source**
1. Correct the original trigger (fix the data source, the condition, the test setup)
2. Add validation at the layer where the trigger occurs (guard the source)
3. Add validation at intermediate layers (defense-in-depth — catch it earlier next time)
4. Add validation at the symptom layer (last resort — but better than nothing)

**Phase 4: Verify**
1. Confirm the symptom no longer reproduces
2. Confirm the fix does not break upstream behavior
3. Run the full test suite

### Adding Instrumentation

When manual tracing hits a dead end:

```typescript
// Before the problematic operation — log context, not just the error
const stack = new Error().stack;
console.error('DEBUG [operation]:', { input, cwd, stack });
```

- Use `console.error()` in tests (logger may be suppressed in test output)
- Log before the operation, not after it fails
- Include all context: directory, cwd, environment variables, timestamps

### Design Decisions

- **Trace backward, not forward** — Forward tracing follows the happy path. Backward tracing follows the actual execution path. These diverge when invalid state enters mid-execution.
- **Instrumentation before, not after** — Logging before a failure captures the state that caused it. Logging after loses the cause context.
- **Defense-in-depth is part of the fix** — Fixing the source is necessary but not sufficient. Add validation at intermediate layers so the next similar bug is caught earlier.

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