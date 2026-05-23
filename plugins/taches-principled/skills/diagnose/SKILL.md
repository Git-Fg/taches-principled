---
name: diagnose
description: "Auto-selects or directly applies the right problem investigation method for a given target. Five modes: A3 (structured incident documentation), Five Whys (single-path causal chains), Fishbone (multi-category cause mapping), Stack Trace (call-chain debugging), and Auto (method selection). Use when user says 'analyze this problem', 'find the root cause', 'trace this bug', or 'why is this happening'."
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
argument-hint: "[problem description] [--mode A3|FIVE-WHYS|FISHBONE|STACK-TRACE|AUTO]"
---

## Decision Router

IF investigating a specific incident, recurring issue, or major problem needing structured documentation → use **A3** mode
IF problem has a clear single causal chain from symptom to root → use **FIVE-WHYS** mode
IF problem has multiple potential contributing factors across domains → use **FISHBONE** mode
IF an error surfaces deep in execution with a long call chain → use **STACK-TRACE** mode
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

**Phase 1: Frame the Problem**
1. **Background** — Why this matters: context, business impact, urgency, who is affected
2. **Current Condition** — What is happening now: facts, data, metrics, examples (not opinions)
3. **Goal/Target** — What success looks like: specific, measurable, time-bound targets

**Phase 2: Analyze Root Causes**
4. **Root Cause Analysis** — Why the problem exists using Five Whys or Fishbone. Dig until reaching systemic or process-level causes.

**Phase 3: Plan and Execute**
5. **Countermeasures** — Specific actions addressing root causes. Each countermeasure traces to a specific root cause from section 4.
6. **Implementation Plan** — Timeline, responsibilities, dependencies, milestones.

**Phase 4: Verify**
7. **Follow-up** — Success metrics, monitoring plan, review dates. Verify success and prevent recurrence.

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

1. State the problem clearly — the specific symptom
2. Ask "Why did this happen?" — answer with the direct cause
3. For each answer, ask "Why?" again — trace one level deeper
4. Repeat until reaching a systemic cause (missing process, validation, automation, or design gap)
5. Validate by tracing forward — root cause → symptom should be a logical chain
6. If branches emerge, explore each independently
7. Propose solutions addressing the root cause — not intermediate answers

The name "five" is a guideline — stop when you reach a process, system, or policy cause.

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

1. State the problem clearly — the "head" of the fish
2. For each category, brainstorm potential causes (don't stop at the first one)
3. Identify which causes are symptoms vs. root causes
4. Cross-reference — mark causes that span multiple categories (systemic)
5. Prioritize — score by impact and likelihood
6. Propose solutions tied to specific root causes

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