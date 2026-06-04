---
name: plan-lifecycle
description: "Plan or run a project end-to-end — PLAN mode creates executable PLAN.md roadmaps with checkpoints; EXECUTE mode runs a plan with worker + critic subagents. Use when the user wants to add a new feature, start a new project, break down work into phases, run a plan, or build something non-trivial."
allowed-tools: Read, Write, Bash, Grep
when_to_use: "Use for multi-phase projects, feature breakdowns, running PLAN.md files, or building out planned phases. Examples: 'plan this project', 'add a feature', 'where do I start', 'run the plan', 'build it'."
argument-hint: "<PLAN|EXECUTE> [path|--phase N]"
---

## Runtime persistence

`.principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts. At intake, read whatever is there if any — prior context may inform this work. When this skill produces durable artifacts, write them to `.principled/` too. Skip if absent.

## Routing Guidance

- **Hub Skill:** Combines project planning (PLAN) and plan execution (EXECUTE).
- **PLAN mode**: 'plan this project', 'create roadmap', 'break down feature', 'decompose work', 'generate PLAN.md'.
- **EXECUTE mode**: 'run plan', 'execute roadmap', 'build it', 'do it', 'run PLAN.md'.

## CONTRAST

- NOT for: day-to-day task tracking or individual task SPECS — use task-lifecycle
- NOT for: early-stage idea exploration before a project exists — use ideation
- NOT for: small A/B tests at small scale — use plan-do-check-act

## Decision Router

IF planning a new project, phase, or feature → **PLAN** mode
IF executing an existing PLAN.md or ROADMAP.md → **EXECUTE** mode

---

# PLAN Mode

Create executable project plans and roadmaps with structured task decomposition.

## Process

1. **Intake** — gather goals, constraints, and dependencies.
2. **Phase Decomposition** — break work into 3-5 high-level phases.
3. **Task Specificity** — define atomic, verifiable tasks for each phase.
4. **Output** — generate `ROADMAP.md` and initial phase `PLAN.md` files.

**Plan formatting:** You MUST read `references/plan-format.md` BEFORE writing any plan file.
**Scope estimation:** You MUST read `references/scope-estimation.md` BEFORE sizing phases.
**Checkpoints:** You MUST read `references/checkpoints.md` BEFORE adding execution gates.

---

# EXECUTE Mode

Executes PLAN.md files using intelligent strategies based on checkpoint types.

## Process

1. **Intake** — load the plan and execution context.
2. **Strategy Selection** — analyze checkpoints to pick Strategy A (Autonomous), B (Segmented), or C (Sequential).
3. **Orchestration** — spawn workers (tp-global-implementer) and critics (tp-critic).
4. **Validation** — run verification commands and milestone reviews.

**Execution strategies:** You MUST read `references/execution-strategies.md` BEFORE starting execution.
**Evaluation protocol:** You MUST read `references/evaluation-protocol.md` BEFORE scoring artifacts.

### Strategy A: Fully Autonomous

**Policy:** Executor is an intelligent orchestrator. **The critic-revise loop is bounded by MAX_ITERATIONS = 3** (Milestone review: MAX_ITERATIONS=3 — higher tolerance for complex cross-task integration issues).

**Milestone critique loop:**
- Every 2-3 tasks completed, or at phase boundary.
- Spawn a tp-critic subagent (general-purpose with write access).
- Loop until no HIGH findings or 3 iterations exhausted.

**Parallel execution rules:**
- Max parallel workers: 3-5 (prevents resource contention).
- Sequential chains execute in order.

---

## Reference Index

| Mode | Reference | Purpose |
|------|-----------|---------|
| PLAN | `references/plan-format.md` | Required formatting and structure |
| PLAN | `references/scope-estimation.md` | Context budgets and sizing |
| PLAN | `references/checkpoints.md` | Execution gate types |
| EXECUTE | `references/execution-strategies.md` | Strategy A/B/C selection |
| EXECUTE | `references/evaluation-protocol.md` | Judge/critic rules |
| EXECUTE | `references/anti-patterns.md` | Execution failure modes |

## Template Index

| Mode | Template | Purpose |
|------|----------|---------|
| PLAN | `templates/brief.md` | Project intake brief |
| PLAN | `templates/roadmap.md` | Multi-phase roadmap |
| PLAN | `templates/phase-prompt.md` | Detailed phase plan |
| EXECUTE | `templates/autonomous-execution.md` | Strategy A workflow |
| EXECUTE | `templates/segment-execution.md` | Strategy B workflow |
| EXECUTE | `templates/sequential-execution.md` | Strategy C workflow |
| EXECUTE | `templates/continue-here.md` | Session handoff |
