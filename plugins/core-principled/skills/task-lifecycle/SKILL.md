---
name: task-lifecycle
description: "Manage complete task lifecycle — CAPTURE raw intent as drafts, REFINE into implementation-ready specs, IMPLEMENT with verification gates."
when_to_use: "Use when capturing tasks, refining drafts, or implementing features. Triggers on: 'add task', 'capture', 'refine task', 'implement task', 'build this', 'execute steps'."
argument-hint: "[subcommand] [task-title-or-path] [--flags]"
---

## Routing Guidance

- **CAPTURE mode**: IMMEDIATELY when user expresses intent that should be tracked, refined, and implemented later.
- **REFINE mode**: IMMEDIATELY after a task is drafted — BEFORE implementation begins.
- **IMPLEMENT mode**: IMMEDIATELY after a task has been refined and is ready for implementation.
- **CONTRAST with create-plans**: task-lifecycle manages task-level specs with implementation steps; create-plans creates project-level plans with milestones and phases.
- **CONTRAST with execute-plans**: execute-plans runs PLAN.md files from .principled/plans/; task-lifecycle runs refined task files from .principled/specs/tasks/.

---

## Decision Router

### CAPTURE Mode
IF user wants to capture a task, add to backlog, or log an idea to track → CAPTURE
IF user provides task title/description → CAPTURE
IF combining with refinement → draft will be consumed by REFINE; do not add structure

### REFINE Mode
IF user mentions a draft task file path (e.g., ".principled/specs/tasks/draft/") → REFINE
IF user asks to outline implementation steps → REFINE
IF user says "refine this task" or "detail the steps" AND a draft exists → REFINE
IF user needs to resume an interrupted refinement → REFINE with --continue
IF user manually edited a task → REFINE with --refine
IF user wants quick refinement → REFINE with --fast

### IMPLEMENT Mode
IF user needs to implement a refined task → IMPLEMENT
IF user wants to continue an interrupted implementation → IMPLEMENT with --continue
IF user manually fixed project files → IMPLEMENT with --refine
IF user wants human review after each step → IMPLEMENT with --human-in-the-loop
IF user wants fast implementation without verification → IMPLEMENT with --skip-judges
IF user is done implementing → IMPLEMENT verifies completion and moves to done

---

# CAPTURE Mode

Create a draft task specification file from user intent. Sets up the standardized folder structure, classifies the task type, generates a filename from an action-oriented title, and preserves the original user prompt exactly for downstream refinement.

## Core Principle

Capture intent exactly as stated. The draft preserves the original user prompt verbatim. Future stages enrich it with analysis, architecture, and verification.

## Process Principle

Document intent, verify directory structure exists, classify task type, generate filename, persist to draft folder. Title must start with an action verb (Add, Fix, Update, Implement, Remove, Refactor).

### Task Type Classification

| Type | Extension | Use When |
|------|-----------|----------|
| feature | `.feature.md` | New functionality or capability |
| bug | `.bug.md` | Something is broken or not working |
| refactor | `.refactor.md` | Code restructuring, no behavior change |
| test | `.test.md` | Adding or updating tests |
| docs | `.docs.md` | Documentation changes only |
| chore | `.chore.md` | Maintenance, dependency updates |
| ci | `.ci.md` | CI/CD configuration changes |

## Output

```
Created task file: .principled/specs/tasks/draft/<name>.<type>.md
Title: <action-oriented title>
Type: <feature|bug|refactor|test|docs|chore|ci>
Depends on: <list or "none">
```

---

# REFINE Mode

First: verify git is available. Run `git --version` to confirm. If git is not installed or not in PATH, fail with error: "Git is not available. Install git or ensure it is in your PATH, then retry."

Refine a draft task specification through a coordinated multi-phase workflow. The workflow runs parallel analysis (research, codebase impact, business requirements), synthesizes findings into architecture, decomposes into implementation steps, reorganizes for parallel execution, and adds verification rubrics. Each phase includes an independent quality evaluation before the next phase proceeds.

## Core Principle

Specification quality is a prerequisite for implementation speed. Analysis, architecture, and verification before writing code reduces rework and produces measurably better outcomes.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path | Required | Path to draft task file in `.principled/specs/tasks/draft/` |
| `--continue` | `[stage]` | None | Resume from a specific stage. Auto-detect from task file completion markers if omitted. |
| `--target-quality` | `X.X` | `3.5` | Minimum weighted score (out of 5.0) for judge pass/fail |
| `--max-iterations` | `N` | `3` | Maximum fix-to-verify cycles per phase |
| `--included-stages` | `stage1,...` | All | Comma-separated stages to include |
| `--skip` | `stage1,...` | None | Comma-separated stages to exclude |
| `--fast` | flag | N/A | Alias: `--target-quality 3.0 --max-iterations 1 --included-stages business analysis,decomposition,verifications` |
| `--one-shot` | flag | N/A | Alias: `--included-stages business analysis,decomposition --skip-judges` |
| `--human-in-the-loop` | `phase,...` | None | Pause for human review after specified phases |
| `--skip-judges` | flag | false | Skip all quality evaluations |
| `--refine` | flag | false | Incremental refinement: detect changes via git, re-run only affected stages |

### Stage Names

| Stage | Phase | Purpose |
|-------|-------|---------|
| `research` | 2a | Gather relevant resources, documentation, prior art |
| `codebase analysis` | 2b | Identify affected files, interfaces, integration points |
| `business analysis` | 2c | Refine description, create acceptance criteria |
| `architecture synthesis` | 3 | Synthesize research and analysis into architectural overview |
| `decomposition` | 4 | Break into implementation steps with success criteria and risks |
| `parallelize` | 5 | Reorganize steps for maximum parallel execution |
| `verifications` | 6 | Add evaluation rubrics for each implementation step |

### Usage Examples

```bash
# Full refinement with all stages
/task-lifecycle refine .principled/specs/tasks/draft/add-validation.feature.md

# Fast mode
/task-lifecycle refine .principled/specs/tasks/draft/quick-fix.bug.md --fast

# Continue from interruption
/task-lifecycle refine .principled/specs/tasks/draft/complex-api.feature.md --continue architecture synthesis

# Incremental refinement after edits
/task-lifecycle refine .principled/specs/tasks/todo/my-task.feature.md --refine
```

## Sub-Agent Dispatch

Every phase subagent must receive: scope (specific phase and task file path), context (prior artifact paths), artifact directive (scratchpad, update task, or new document), output format (structured report with file paths and findings).

**Spawn Footer**: Your context starts fresh — no access to prior conversation or other subagents' outputs. Return structured output (file paths, findings, artifacts) to the orchestrator. If you encounter anything unexpected or have any question or doubt, stop and report back. Do not proceed silently on assumptions.

**Failure Signal**: If unable to complete the task, return: `{"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}`

### Phase Agent Prompt Structure

```
Phase: [Phase Name]
Task File: <TASK_FILE>
Prior Artifacts: <paths to scratchpad/analysis files from prior phases>

Your task: <specific actions for this phase>

CRITICAL: Write findings to scratchpad first at .principled/specs/scratchpad/<unique-id>.md.
Only update the task file with validated conclusions.
Do NOT output your analysis inline — write everything to files.

Report: artifact paths created/updated, key findings summary, any issues.
```

### Judge Agent Prompt Structure

```
Evaluate artifact at: <artifact_path>

Role: <phase role>
Rubric: <criteria table>

Context: Task File <TASK_FILE>, Phase [Name]

Score each criterion 1-5. Provide chain-of-thought justification BEFORE each score.
Compute weighted overall. Return PASS/FAIL with specific improvements if FAIL.
```

## Phase Workflow

### Phase 2: Parallel Analysis

Launch three analysis sub-phases in parallel. Each phase uses a dedicated subagent and produces a scratchpad file plus task artifacts. Each phase has an independent judge evaluation.

**Synchronization Point**: Wait for ALL three phases AND their judges to pass before proceeding to Phase 3. If one phase finishes significantly before others, spawn its judge immediately rather than waiting.

### Phase 2a: Research

- Search for documentation, existing patterns, and libraries relevant to the task
- Identify common pitfalls, best practices, and reference implementations
- Create a reusable skill document with findings
- Write all research to scratchpad first, then create the skill document
- Do NOT output research results inline — write everything to files

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, skill document at `.claude/skills/<topic>/SKILL.md`

**Evaluation dimensions (weight)**:
- Resource coverage (0.30): documentation and references gathered
- Pattern relevance (0.25): identified patterns are applicable and actionable
- Issue anticipation (0.20): common pitfalls identified with solutions
- Reusability (0.15): skill is general enough for multiple tasks
- Task integration (0.10): task file updated with skill reference

**On judge FAIL**: Re-launch with judge feedback incorporated. Do not proceed until PASS or MAX_ITERATIONS reached.

### Phase 2b: Codebase Impact Analysis

- Identify all files that will be modified, created, or deleted
- Document key functions, classes, and interfaces affected
- Map integration points and dependencies between components
- Assess risk level for each affected area with mitigations
- Write all analysis to scratchpad first, then create the analysis document

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, analysis file at `.principled/specs/analysis/analysis-<name>.md`

**Evaluation dimensions (weight)**:
- File identification accuracy (0.35): all affected files identified with specific paths
- Interface documentation (0.25): key functions and classes documented with signatures
- Integration mapping (0.25): integration points identified with impact assessment
- Risk assessment (0.15): high-risk areas identified with mitigations

### Phase 2c: Business Analysis

- Use a scratchpad to capture the complete analysis process
- Do NOT accept surface-level descriptions at face value — probe for underlying intent
- Define scope boundaries (included, excluded, boundary cases)
- Extract core elements: actors, actions/behaviors, data entities, constraints
- Break requirements into functional and non-functional categories
- Verify testability: clear Given/When/Then, measurable outcomes
- Synthesize the refined description (2-3 paragraphs: what, why, who, constraints)
- Write validated conclusions to the task file: Description, Scope, User Scenarios, Acceptance Criteria

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, updated task file with Description, Scope, User Scenarios, Acceptance Criteria sections

**Evaluation dimensions (weight)**:
- Description clarity (0.30): what/why clearly explained, scope boundaries defined
- Acceptance criteria quality (0.35): criteria are specific, testable, use Given/When/Then for complex cases
- Scenario coverage (0.20): primary flow documented, error scenarios considered
- Scope definition (0.15): in-scope/out-of-scope explicit, no implementation details in description

### Phase 3: Architecture Synthesis

Spawn after all Phase 2 phases and judges pass. Synthesize research, codebase analysis, and business requirements into an architectural overview.

- Read scratchpad and analysis files from Phase 2a, 2b, 2c
- Define the solution strategy and approach with reasoning
- Document key architectural decisions and trade-offs
- Specify components, responsibilities, and interfaces
- List expected file changes (create/modify/delete) consistent with codebase analysis
- Update task file with Architecture Overview section
- Only include sections relevant to task complexity — do not add boilerplate sections

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, updated task file with Architecture Overview section

### Phase 4: Decomposition

Spawn after Phase 3 passes. Break the architecture into ordered implementation steps.

- Define ordered implementation steps with clear dependencies
- Each step must have: clear goal, expected output files, success criteria, subtasks
- No step larger than the large estimate threshold — split oversized steps
- Identify blockers, risks, and mitigations for each step
- Organize in phases: Setup, Foundational, User Stories, Polish
- Include Definition of Done section at task level listing completion criteria
- Write to scratchpad first, then update the task file

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, updated task file with Implementation Process section

### Phase 5: Parallelize

Spawn after Phase 4 passes. Reorganize implementation steps for maximum parallel execution.

- Reorganize steps with explicit dependency chains
- Identify steps that can run in parallel (no transitive dependencies between them)
- Assign appropriate agent difficulty levels to each step
- Generate a parallelization diagram showing execution order and parallel tracks
- Add parallel execution directive with MUST requirements for each parallel group
- Only parallelize within the current task scope — do not plan or create tasks for future work
- Write to scratchpad first, then update the task file

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, updated task file with parallelization annotations and agent assignments

### Phase 6: Verifications

Spawn after Phase 5 passes. Add evaluation rubrics for each implementation step.

- For each implementation step, determine verification level:

| Level | When to Use | Configuration |
|-------|-------------|---------------|
| None | Simple operations (mkdir, delete, config changes) | Skip verification entirely |
| Single Judge | Non-critical artifacts | 1 judge, threshold from task context |
| Panel of 2 Judges | Critical artifacts (business logic, security, data) | 2 judges, median voting, higher threshold |
| Per-Item Judges | Multiple similar items (validators, handlers, endpoints) | 1 judge per item, parallel execution |

- Create role-specific weighted rubrics for each step with measurable criteria
- Weights must sum to 1.0 for each rubric
- Set context-appropriate thresholds
- Include a verification summary table at the end of the task file

**Artifacts**: Scratchpad at `.principled/specs/scratchpad/<hex-id>.md`, updated task file with `#### Verification` sections for each step

### Phase 7: Promote

After all phases complete, move the refined task from draft to todo:

```bash
git mv <TASK_FILE> .principled/specs/tasks/todo/
```

---

# IMPLEMENT Mode

First: verify git is available. Run `git --version` to confirm. If git is not installed or not in PATH, fail with error: "Git is not available. Install git or ensure it is in your PATH, then retry."

Orchestrate multi-step task implementation with automated quality verification. Each implementation step spawns a dedicated subagent, then verified by an independent judge subagent. Supports three verification patterns plus final Definition of Done verification.

## Core Principle

Context is the orchestrator's most precious resource. Protecting it means delegating everything: implementations to developer agents, evaluations to judge agents. The orchestrator that reads artifacts stops being able to orchestrate.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path or filename | Auto-detect | Task file to implement. Auto-select from todo/ or in-progress/ if omitted. |
| `--continue` | flag | false | Resume from last completed step. Launches judge to verify last incomplete step state. |
| `--refine` | flag | false | Detect git changes to project files, map to affected steps, re-verify from earliest affected. |
| `--human-in-the-loop` | `[step,step,...]` | None | Pause for human review after specified steps. |
| `--target-quality` | `X.X` or `X.X,Y.Y` | `4.0,4.5` | Single value sets both thresholds. Two comma-separated values set standard,critical separately. |
| `--max-iterations` | `N` or `unlimited` | `3` | Maximum fix-to-verify cycles per step. |
| `--skip-judges` | flag | false | Skip all verification — steps proceed directly without quality gates |

### Threshold Resolution

- Standard components threshold: default 4.0/5.0. Used for steps not marked as critical.
- Critical components threshold: default 4.5/5.0. Used for steps marked as critical.
- Single `--target-quality X.X` sets both thresholds to the same value.

### Usage Examples

```bash
# Implement a specific task
/task-lifecycle implement add-validation.feature.md

# Auto-select from todo/ or in-progress/
/task-lifecycle implement

# Continue from interruption
/task-lifecycle implement add-validation.feature.md --continue

# Human review after every step
/task-lifecycle implement add-validation.feature.md --human-in-the-loop
```

## Phase 0: Select Task and Move to In-Progress

**Task Resolution**: search in order `in-progress/`, `todo/`, `done/`. If argument empty, auto-select single file.

**Continue Mode**: Detect `[DONE]` markers on step titles. Launch judge to verify last completed step state. Resume from next step if PASS, re-implement if FAIL.

**Refine Mode**: Detect git changes to project files. Map changed files to implementation steps via Expected Output and Verification sections.

## Phase 1: Load and Analyze Task

This is the ONLY phase where the orchestrator reads a file.

**Verification Level Classification**:
- No verification section → Pattern A (skip)
- Single Judge → Pattern B, 1 judge, standard threshold
- Panel of 2 Judges → Pattern B, 2 judges, critical threshold
- Per-Item Judges → Pattern C, 1 judge per item

Critical steps always use critical threshold regardless of verification level.

## Phase 2: Execute Implementation Steps

Execute steps in dependency order. Steps marked `Parallel with:` run simultaneously.

### Verification Patterns

**Pattern A: Simple Step**
No verification needed. Spawn implementation agent, mark done, proceed.

**Pattern B: Single Item with Verification**
Implementation with 1-2 independent judges. Aggregation uses median. Iterate on FAIL.

**Pattern C: Multi-Item with Per-Item Judges**
1 judge per item, parallel execution. Iterate only failing items on FAIL.

### Human-in-the-Loop Checkpoint

Triggered after a step PASSES if the step is in `HUMAN_IN_THE_LOOP_STEPS`. Present judge feedback and artifacts.

## Phase 3: Final Verification (Definition of Done)

After all steps complete, spawn DoD verification subagent to verify each checkbox item.

**On any FAIL**: Launch fix subagents for failing items, then re-verify. Iterate until all PASS.

## Phase 4: Move Task to Done

```bash
git mv .principled/specs/tasks/in-progress/<TASK_FILE> .principled/specs/tasks/done/
```

## Phase 5: Report

Generate implementation summary with step status, verification results, and DoD verification.

---

# Shared Evaluation Protocol

**Evaluation uses the shared judge protocol — see `../execute-plans/references/evaluation-protocol.md`** for chain-of-thought, scratchpad-first writing, MAX_ITERATIONS semantics, and the full integrity rules.

### Scoring Scale (per criterion)

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Missing essential elements, fundamental misunderstanding |
| 2 | Below Average | Some correct elements, significant gaps |
| 3 | Adequate | Meets basic requirements, functional but minimal |
| 4 | Good | Meets all requirements, few minor issues |
| 5 | Excellent | Exceptional quality, exceeds expectations |

### Decision Logic

- **PASS** (score >= THRESHOLD): Phase complete, proceed to next phase
- **FAIL** (score < THRESHOLD): Re-launch phase with judge feedback incorporated
- **MAX_ITERATIONS reached**: Proceed to next phase regardless of score, log warning

### Panel Voting Algorithm

1. **Collect**: both judge scores per criterion
2. **Median**: average scores per criterion
3. **High variance check**: if |score1 - score2| > 2.0, flag for potential disagreement
4. **Weighted overall**: sum(median x weight) for all criteria
5. **Pass/fail**: overall >= threshold

If high variance detected: present both perspectives to user for resolution.

---

# Design Decisions

IF entering a refinement stage (research, analysis, decomposition, verification) → BEFORE acting read `references/stages.md`. Do not skip stage-specific guidance.

IF implementing a verified step → BEFORE writing code read `references/patterns.md`. Do not assume implementation patterns without reading this file.

### Separate draft and todo folders
Draft is for unrefined tasks; todo is for tasks ready to implement. The separation enforces refinement as a required step.

### Type as file extension
The file extension encodes the task type directly, making it visible in file listings and grep searches without opening the file.

### Parallel analysis before synthesis
Running research, codebase analysis, and business analysis in parallel is faster than sequential. This prevents the common failure mode of designing architecture without understanding business requirements or codebase constraints.

### Independent judges per phase
Separate judge subagents prevent confirmation bias. Independent judges provide objective quality signals and catch blind spots.

### Scratchpad-first methodology
All analysis goes to a scratchpad before the task file. This prevents premature commitment to unverified findings.

### Separate standard and critical thresholds
Using a higher threshold for critical paths (4.5 vs 4.0) focuses quality effort where it matters most.