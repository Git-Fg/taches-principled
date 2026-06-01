---
name: implement-task
description: "Execute refined tasks with verification gates. Spawn developer, then judge agent. Iterate until quality threshold."
allowed-tools: Read, Edit, Write, Bash
when_to_use: "Use when user asks to implement a refined task specification, execute implementation steps, or build a feature."
argument-hint: "[task file] [--continue] [--refine] [--human-in-the-loop] [--target-quality X.X] [--skip-judges]"
---

## Routing Guidance

- IMMEDIATELY after a task has been refined and is ready for implementation — verification gates are mandatory.
- CONTRAST with execute-plans: That skill executes PLAN.md files from .principled/plans/; this skill executes refined task files from .specs/tasks/ (todo/, in-progress/, done/).

## Decision Router

IF user needs to implement a refined task → execute implementation steps with per-step verification
IF user needs to continue an interrupted implementation → use `--continue` to resume from last completed step
IF user manually fixed project files → use `--refine` to detect changes and re-verify affected steps
IF user wants human review after each step → use `--human-in-the-loop`
IF user wants fast implementation without verification gates → use `--skip-judges`
IF user is done implementing → verify completion and move task to done

# Implement Task

First: verify git is available. Run `git --version` to confirm. If git is not installed or not in PATH, fail with error: "Git is not available. Install git or ensure it is in your PATH, then retry."

Orchestrate multi-step task implementation with automated quality verification. Each implementation step spawns a dedicated subagent, then verified by an independent judge subagent. Supports three verification patterns plus final Definition of Done verification.

The orchestrator spawns and aggregates but never implements or evaluates directly. Every implementation step gets a dedicated agent. Every verification gets an independent judge.

## Core Principle

Context is the orchestrator's most precious resource. Protecting it means delegating everything: implementations to developer agents, evaluations to judge agents. The orchestrator that reads artifacts stops being able to orchestrate.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path or filename | Auto-detect | Task file to implement. If omitted, auto-select from todo/ or in-progress/. |
| `--continue` | flag | false | Resume from last completed step. Launches judge to verify last incomplete step state, then resumes from there. |
| `--refine` | flag | false | Detect git changes to project files, map to affected implementation steps, re-verify from earliest affected step. |
| `--human-in-the-loop` | `[step,step,...]` | None | Pause for human review after specified steps. Without step numbers, pauses after every step. |
| `--target-quality` | `X.X` or `X.X,Y.Y` | `4.0,4.5` | Single value sets both standard and critical threshold. Two comma-separated values set standard,critical. |
| `--max-iterations` | `N` or `unlimited` | `3` | Maximum fix-to-verify cycles per step. `unlimited` iterates until threshold is met. |
| `--skip-judges` | flag | false | Skip all verification — steps proceed directly after implementation without quality gates |

### Threshold Resolution

- Standard components threshold: default 4.0/5.0. Used for steps not marked as critical.
- Critical components threshold: default 4.5/5.0. Used for steps marked as critical in the task file.
- Single `--target-quality X.X` sets both thresholds to the same value.
- Two values `--target-quality X.X,Y.Y` set standard and critical thresholds separately.

### Usage Examples

```bash
# Implement a specific task
/implement add-validation.feature.md

# Auto-select from todo/ or in-progress/
/implement

# Continue from interruption
/implement add-validation.feature.md --continue

# Refine after manual code edits
/implement add-validation.feature.md --refine

# Human review after every step
/implement add-validation.feature.md --human-in-the-loop

# Higher quality threshold for both standard and critical
/implement critical-api.feature.md --target-quality 4.5
```

## Phase 0: Select Task and Move to In-Progress

### Task Resolution Principle

Resolve task file: search in order `in-progress/`, `todo/`, `done/`. If argument empty, auto-select single file from in-progress/ or todo/.

### Continue Mode Principle

Detect `[DONE]` markers on step titles. Launch judge to verify last completed step state. If PASS, resume from next step. If FAIL, re-implement that step.

### Refine Mode Principle

Detect git changes to project files. Map changed files to implementation steps via Expected Output and Verification sections. Re-verify from earliest affected step. Pass user changes as context to subagents.

## Phase 1: Load and Analyze Task

This is the ONLY phase where the orchestrator reads a file.

**Verification Level Classification Principle:**
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

Triggered after a step PASSES if the step is in `HUMAN_IN_THE_LOOP_STEPS`. Present judge feedback and artifacts. On user feedback, incorporate into next step. On "n", pause workflow.

## Phase 3: Final Verification (Definition of Done)

After all steps complete, spawn DoD verification subagent to verify each checkbox item.

**On any FAIL:** Launch fix subagents for failing items, then re-verify. Iterate until all PASS.

## Phase 4: Move Task to Done

```bash
git mv .specs/tasks/in-progress/<TASK_FILE> .specs/tasks/done/
```

## Phase 5: Report

Generate implementation summary with step status, verification results, and DoD verification.

## Evaluation Integrity Rules

**Evaluation uses the shared judge protocol — see `../execute-plans/references/evaluation-protocol.md`** for chain-of-thought, scratchpad-first writing, MAX_ITERATIONS semantics, and the full integrity rules. This section covers only the implement-task-specific mechanics.

## Panel Voting Algorithm

1. **Collect**: both judge scores per criterion
2. **Median**: average scores per criterion
3. **High variance check**: if |score1 - score2| > 2.0, flag for potential disagreement
4. **Weighted overall**: sum(median x weight) for all criteria
5. **Pass/fail**: overall >= threshold

If high variance detected: present both perspectives to user for resolution. If user declines, use median (conservative).

## Error Handling

- **Implementation failure**: Present details to user, re-launch with clarifications
- **Judge FAIL**: Re-launch implementation with feedback. Iterate until PASS or MAX_ITERATIONS
- **Judge disagreement (>2.0)**: Ask user to resolve
- **Refine edge cases**: No changes detected or changes don't map to steps

## Design Decisions

IF implementing a verified step → BEFORE writing code read `references/patterns.md`. Do not assume implementation patterns without reading this file.

### Separate standard and critical thresholds
Using a higher threshold for critical paths (4.5 vs 4.0) focuses quality effort where it matters most.

### Refine mode preserves user changes
When users manually edit source files, `--refine` detects changes and re-verifies consistency.

### Continue mode for resilience
`--continue` detects where work stopped and resumes including re-verifying the boundary step.
