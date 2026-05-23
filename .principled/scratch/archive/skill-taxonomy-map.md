# Skill Taxonomy Map

## Overview

39 skills across 8 clusters. Primary axis: workflow stage. Secondary axis: primary action type.

---

## Cluster 1: Capture

**Stage:** Intake / Task Capture
**Hub/Spoke:** Spoke-only (pure execution)

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `add-task` | Create | Standalone — creates draft task files in `.specs/tasks/draft/` |

**Notes:**
- Single responsibility: capture user intent verbatim into a task file
- Downstream of this cluster: `plan-task` for refinement

---

## Cluster 2: Analysis

**Stage:** Investigation / Understanding
**Hub/Spoke:** Hub (`analyse`) + Spokes

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `analyse` | Analyze | **Hub** — auto-selects between Gemba Walk, Value Stream Mapping, Muda Analysis |
| `analyse-problem` | Analyze | Standalone — A3-format structured problem documentation |
| `root-cause-analysis` | Analyze | Standalone — Five Whys or Fishbone methods |
| `root-cause-tracing` | Analyze | Standalone — backward tracing through call stack |
| `ideation` | Create | Standalone — brainstorm mode (refinement) or create-ideas mode (divergent generation) |
| `fpf-propose` | Create | Standalone — First Principles Framework hypothesis cycle |
| `fpf-read` | Analyze | Standalone — queries FPF knowledge base |

**Notes:**
- `analyse` is the hub that routes to the right investigation method based on target type
- `ideation` and `fpf-propose` are parallel discovery skills — ideation for creative exploration, FPF for logical hypothesis testing
- `root-cause-analysis` vs `root-cause-tracing`: root-cause-analysis is structured drilling (Five Whys, Fishbone); root-cause-tracing is bug-focused backward instrumentation

**Redundancies:**
- `analyse-problem` vs `root-cause-analysis` — both do root cause investigation but in different contexts:
  - `analyse-problem` for incidents/specific problems (A3 format)
  - `root-cause-analysis` for general debugging (Five Whys/Fishbone)
- These could potentially be unified but serve different workflow contexts

---

## Cluster 3: Planning

**Stage:** Planning / Specification
**Hub/Spoke:** Hub (`create-plans`) + Spokes

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `create-plans` | Create | **Hub** — creates executable PLAN.md files, explicitly invokes `execute-plans` (compositional pair) |
| `plan-task` | Create | Standalone — multi-phase task refinement with independent quality gates |
| `kaizen` | Analyze | Standalone — design-time constraints applied to every code decision |
| `reflexion` | Review | Standalone — self-critique with severity ratings, multi-perspective critique, learning capture |
| `plan-do-check-act` | Execute | Standalone — PDCA iterative improvement cycle |
| `create-prompts` | Create | Standalone — creates executable XML-structured prompts for Claude Code |

**Notes:**
- `create-plans` is the primary planning hub — creates the plan artifact and explicitly invokes execution
- `plan-task` is task refinement (draft → implementation-ready spec) — more granular than `create-plans` which is project-level
- `reflexion` has three modes: reflect (self-review), critique (multi-judge), memorize (learning capture)
- `kaizen` is a constraint/guardrail skill — shapes HOW code is written, not WHAT to build
- `plan-do-check-act` tests changes; `kaizen` prevents bad patterns — complementary

**Redundancies:**
- `create-plans` vs `plan-task`: both do planning but at different scales
  - `create-plans`: project-level, creates PLAN.md consumed directly by `execute-plans`
  - `plan-task`: task-level, refines draft tasks with 6-phase workflow and quality gates
- `reflexion` overlaps with `code-review` in the review dimension — both do multi-agent quality checking

---

## Cluster 4: Authoring

**Stage:** Skill/Prompt/Agent Creation
**Hub/Spoke:** Spoke-only (focused creation)

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `create-skills` | Create | Standalone — creates Claude Code skills with 5-category framework |
| `create-subagents` | Create | Standalone — creates specialized Claude Code subagents with guidance |
| `write-concisely` | Edit | Standalone — applies Strunk & White principles to documentation |

**Notes:**
- Both `create-skills` and `create-subagents` create artifacts (skills vs subagents) but serve different purposes
- `create-subagents` has extensive orchestration reference material (8 reference files) — heavy skill

---

## Cluster 5: Execution

**Stage:** Implementation / Orchestration
**Hub/Spoke:** Multiple hubs + spokes

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `execute-plans` | Execute | **Hub** — executes PLAN.md files, auto-selects strategy based on checkpoint types |
| `execute-prompts` | Execute | Standalone — executes prompt files |
| `implement-task` | Execute | **Hub** — orchestrates multi-step task implementation with judge verification |
| `subagent-orchestration` | Orchestrate | **Hub** — spawns parallel subagents, owns all cognition |
| `sadd-dispatch` | Dispatch | **Hub** — single-task dispatch with auto model selection |
| `sadd-execute` | Execute | **Hub** — meta-judge verification with 4 modes (single/steps/parallel/competitive) |
| `sadd-patterns` | Create | Standalone — designs multi-agent architectures |
| `sadd-judge` | Evaluate | **Hub** — meta-judge then judge with optional debate |
| `sadd-tot` | Create | Standalone — Tree of Thoughts systematic exploration |
| `do-competitively` | Execute | **Hub** — competitive multi-agent generation with meta-judge evaluation |
| `judge-with-debate` | Evaluate | **Hub** — multi-round debate between judges until consensus |
| `subagent-driven-development` | Execute | **Hub** — dispatch fresh subagent per task with code review gates |

**Notes:**
- Largest cluster with 12 skills — execution is where most complexity lives
- `execute-plans` is the project-level execution hub — executes plan files created by `create-plans`
- `implement-task` is the task-level execution hub — implements refined tasks with per-step verification
- `sadd-*` skills (tp-sadd plugin) form a complete execution system:
  - `sadd-dispatch`: simple single-task dispatch
  - `sadd-execute`: execution with quality verification gates
  - `sadd-judge`: evaluation with optional debate
  - `sadd-patterns`: architecture design
  - `sadd-tot`: systematic exploration
- `subagent-orchestration` is the low-level orchestration primitive — spawn patterns, RACE framework, failure modes
- `do-competitively` and `judge-with-debate` are both multi-agent evaluation but with different strategies:
  - `do-competitively`: generate multiple solutions, evaluate, select best
  - `judge-with-debate`: single solution, multiple judges debate until consensus

**Redundancies:**
- `sadd-dispatch` vs `subagent-driven-development`: both dispatch subagents for tasks
  - `sadd-dispatch`: simpler, auto model selection, CoT + self-critique
  - `subagent-driven-development`: plan-driven with code review gates between tasks
- `implement-task` vs `sadd-execute`: both do implementation with verification
  - `implement-task`: task-level, per-step verification with judge agents
  - `sadd-execute`: more flexible, 4 modes including competitive
- `subagent-driven-development` vs `sadd-dispatch`: both dispatch subagents
  - `subagent-driven-development`: plan-based, sequential with code review gates
  - `sadd-dispatch`: simpler single-task dispatch with model selection
- `do-competitively` vs `sadd-tot`: both do multi-solution exploration
  - `do-competitively`: competitive generation + meta-judge evaluation
  - `sadd-tot`: Tree of Thoughts (explore → prune → expand → evaluate)

---

## Cluster 6: Verification

**Stage:** Quality Assurance / Code Improvement
**Hub/Spoke:** Hub (`code-review`) + Spokes

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `code-review` | Review | **Hub** — multi-agent PR/local review with 6 specialized agents |
| `code-simplify` | Refactor | Standalone — 5-stage simplification pipeline with numeric thresholds |
| `update-docs` | Write | Standalone — doc updates after code changes |

**Notes:**
- `code-review` has 6 parallel agents covering different review dimensions (Bug Hunter, Security Auditor, Code Quality Reviewer, Contracts Reviewer, Historical Context Reviewer, Test Coverage Reviewer)
- `code-simplify` is purely mechanism (the how) — applies numeric thresholds to identify simplification targets
- `update-docs` operates post-code-change, before commit

**Redundancies:**
- `code-review` and `reflexion` both do multi-perspective review:
  - `code-review`: focused on code artifacts (bugs, security, quality, contracts, tests)
  - `reflexion`: focused on completed work quality with three modes (reflect/critique/memorize)

---

## Cluster 7: Shipping

**Stage:** Git Operations / Release
**Hub/Spoke:** Spoke-only

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `git-ship` | Create | Standalone — conventional commits + PR creation |
| `git-review` | Review | Standalone — line-specific PR review comments |
| `git-issues` | Create | Standalone — fetch issues + create technical specs |
| `git-advanced` | Execute | Standalone — git notes + worktrees |

**Notes:**
- All four are domain-specific (git/GitHub) — no orchestration within the cluster
- `git-issues` produces specs that feed into `plan-task` or `implement-task` pipeline
- `git-ship` produces PRs that feed into `git-review`

---

## Cluster 8: Maintenance

**Stage:** FPF Lifecycle Management
**Hub/Spoke:** Spoke-only

| Skill | Action Type | Interaction Pattern |
|-------|-------------|---------------------|
| `fpf-maintenance` | Execute | Standalone — reset cycles, reconcile knowledge base, evidence freshness management |

**Notes:**
- Minimal cluster (1 skill) — FPF is a self-contained reasoning framework
- Complements `fpf-propose` and `fpf-read` in the FPF trilogy

---

## Cross-Cutting Observations

### Hub Skills (Orchestrators)

| Hub Skill | Cluster | Orchestrates |
|-----------|---------|--------------|
| `analyse` | Analysis | Investigation method selection |
| `create-plans` | Planning | Plan creation → invokes `execute-plans` |
| `execute-plans` | Execution | Plan execution with strategy selection |
| `implement-task` | Execution | Task implementation with per-step verification |
| `subagent-orchestration` | Execution | Parallel subagent spawning |
| `code-review` | Verification | 6 parallel review agents |
| `sadd-dispatch` | Execution | Single-task dispatch |
| `sadd-execute` | Execution | Multi-mode execution with verification |
| `sadd-judge` | Execution | Meta-judge → judge evaluation pipeline |
| `do-competitively` | Execution | Competitive generation + evaluation |
| `judge-with-debate` | Execution | Multi-round debate consensus |
| `subagent-driven-development` | Execution | Per-task dispatch with review gates |

### Compositional Pairs

| Create Skill | Execute Skill | Purpose |
|--------------|---------------|---------|
| `create-plans` | `execute-plans` | Project-level planning + execution |
| `create-prompts` | `execute-prompts` | Prompt creation + execution |
| `plan-task` | `implement-task` | Task refinement + implementation |
| `create-skills` | (direct use) | Skill authoring → skill invocation |

### Redundancy Hotspots

1. **Execution orchestration** (`sadd-dispatch`, `subagent-driven-development`, `subagent-orchestration`) — multiple skills do similar dispatch work with different emphasis
2. **Multi-solution exploration** (`do-competitively`, `sadd-tot`) — both explore multiple solutions but with different methods
3. **Root cause investigation** (`analyse-problem`, `root-cause-analysis`, `root-cause-tracing`) — three skills for similar debugging work
4. **Quality review** (`code-review`, `reflexion`) — overlap in multi-agent review
5. **Planning** (`create-plans`, `plan-task`) — different scales of planning work

### Plugin Boundaries

| Plugin | Clusters | Skills |
|--------|----------|--------|
| `taches-principled` | 1, 2, 3, 4, 5 (partial), 6 | 22 skills |
| `tp-sadd` | 5 (execution) | 8 skills |
| `tp-fpf` | 2 (analysis), 8 (maintenance) | 3 skills |
| `tp-git` | 7 (shipping) | 4 skills |
| `tp-tdd` | 4 (authoring) | 1 skill |

---

## Skill Count by Cluster

| Cluster | Count | Skills |
|---------|-------|--------|
| Execution | 12 | execute-plans, execute-prompts, implement-task, subagent-orchestration, sadd-dispatch, sadd-execute, sadd-patterns, sadd-judge, sadd-tot, do-competitively, judge-with-debate, subagent-driven-development |
| Analysis | 7 | analyse, analyse-problem, root-cause-analysis, root-cause-tracing, ideation, fpf-propose, fpf-read |
| Planning | 6 | create-plans, plan-task, kaizen, reflexion, plan-do-check-act, create-prompts |
| Verification | 3 | code-review, code-simplify, update-docs |
| Authoring | 3 | create-skills, create-subagents, write-concisely |
| Shipping | 4 | git-ship, git-review, git-issues, git-advanced |
| Capture | 1 | add-task |
| Maintenance | 1 | fpf-maintenance |
| **Total** | **37** | (tdd overlaps with execution - counted in Authoring) |